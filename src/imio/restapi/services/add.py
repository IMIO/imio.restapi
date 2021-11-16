# -*- coding: utf-8 -*-

from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from imio.restapi.utils import get_return_fullobject_after_creation_default
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services.content.add import FolderPost
from plone.restapi.services.content.add import PAM_INSTALLED
from plone.restapi.services.content.add import PLONE5
from plone.restapi.services.content.utils import add
from plone.restapi.services.content.utils import create
from Products.CMFPlone.utils import safe_hasattr
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent
from ZPublisher.HTTPRequest import HTTPRequest

import json
import plone.protect.interfaces


FILE_DATA_INCOMPLETE_ERROR = (
    "One of 'filename' or 'content-type' is required while adding a 'file'!"
)
FILE_DATA_ENCODING_WARNING = (
    "While adding 'file', key 'encoding' was not given, assuming it is 'base64'!"
)


def create_request(base_request, body):
    request = HTTPRequest(
        base_request.stdin, base_request._orig_env, base_request.response
    )
    for attr in base_request.__dict__.keys():
        setattr(request, attr, getattr(base_request, attr))
    request.set("BODY", body)
    return request


class FolderPost(FolderPost):
    def __init__(self, context, request):
        super(FolderPost, self).__init__(context, request)
        self.warnings = []

    def prepare_data(self, data):
        """Hook to manipulate the data structure if necessary."""
        # when adding an element having a 'file', check that given data is correct
        if u"file" in data:
            file_data = data[u"file"]
            if "filename" not in file_data and u"content-type" not in file_data:
                raise BadRequest(FILE_DATA_INCOMPLETE_ERROR)
            elif "encoding" not in file_data:
                file_data[u"encoding"] = u"base64"
                self.warnings.append(FILE_DATA_ENCODING_WARNING)
        return data

    def clean_data(self, data):
        """Clean data before creating element."""
        cleaned_data = data.copy()
        return cleaned_data

    def _after_reply_hook(self, serialized_obj):
        """Hook to be overrided if necessary,
           called after reply returned result."""
        pass

    def _wf_transition_additional_warning(self, tr):
        """Hook to add some specific context for
           transition not triggerable warning."""
        return ""

    def wf_transitions(self, serialized_obj):
        """If a key 'wf_transitions' is there, try to trigger it."""
        wf_tr = self.data.get("wf_transitions", [])
        if not wf_tr:
            return
        with api.env.adopt_roles(roles=["Manager"]):
            wfTool = api.portal.get_tool("portal_workflow")
            wf_comment = u"wf_transition_triggered_by_application"
            obj = self.context.get(serialized_obj["id"])
            must_update_serialized_obj = False
            for tr in wf_tr:
                available_transitions = [t["id"] for t in wfTool.getTransitionsFor(obj)]
                if tr not in available_transitions:
                    warning_message = (
                        "While treating wfTransitions, could not "
                        "trigger the '{0}' transition!".format(tr)
                    )
                    warning_message += self._wf_transition_additional_warning(tr)
                    self.warnings.append(warning_message)
                    continue
                # we are sure transition is available, trigger it
                wfTool.doActionFor(obj, tr, comment=wf_comment)
                must_update_serialized_obj = True
            if must_update_serialized_obj:
                serialized_obj[u"review_state"] = api.content.get_state(obj)

    def reply(self):
        if not getattr(self, "parent_data", None):
            self.parent_data = {}
        data = json_body(self.request)
        self.data = self.prepare_data(data)
        self.cleaned_data = self.clean_data(data)
        # set new BODY with cleaned data
        self.request.set("BODY", json.dumps(self.cleaned_data))
        return self._reply()

    def do_reply(self):
        """This is the reply method from plone.restapi, overrided
           to manage returning the fullobject after creation or the summary."""

        # imio.restapi, nothing changed until next comment "imio.restapi ..." comment
        data = json_body(self.request)

        type_ = data.get("@type", None)
        id_ = data.get("id", None)
        title = data.get("title", None)
        translation_of = data.get("translation_of", None)
        language = data.get("language", None)

        if not type_:
            raise BadRequest("Property '@type' is required")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        try:
            obj = create(self.context, type_, id_=id_, title=title)
        except Unauthorized as exc:
            self.request.response.setStatus(403)
            return dict(error=dict(type="Forbidden", message=str(exc)))
        except BadRequest as exc:
            self.request.response.setStatus(400)
            return dict(error=dict(type="Bad Request", message=str(exc)))

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        temporarily_wrapped = False
        if IAcquirer.providedBy(obj) and not safe_hasattr(obj, "aq_base"):
            obj = obj.__of__(self.context)
            temporarily_wrapped = True

        # Update fields
        deserializer = queryMultiAdapter((obj, self.request), IDeserializeFromJson)
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(
                error=dict(message="Cannot deserialize type {}".format(obj.portal_type))
            )

        try:
            deserializer(validate_all=True, create=True)
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="DeserializationError", message=str(e)))

        if temporarily_wrapped:
            obj = aq_base(obj)

        if not getattr(deserializer, "notifies_create", False):
            notify(ObjectCreatedEvent(obj))

        obj = add(self.context, obj, rename=not bool(id_))

        # Link translation given the translation_of property
        if PAM_INSTALLED and PLONE5:
            from plone.app.multilingual.interfaces import (
                IPloneAppMultilingualInstalled,
            )  # noqa
            from plone.app.multilingual.interfaces import ITranslationManager

            if (
                IPloneAppMultilingualInstalled.providedBy(self.request)
                and translation_of
                and language
            ):
                source = self.get_object(translation_of)
                if source:
                    manager = ITranslationManager(source)
                    manager.register_translation(language, obj)

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", obj.absolute_url())

        # imio.restapi, begin changes, manage returning full object or summary
        return_full_object = data.get(
            "return_fullobject", get_return_fullobject_after_creation_default())
        if return_full_object:
            serializer = queryMultiAdapter((obj, self.request), ISerializeToJson)
        else:
            serializer = queryMultiAdapter((obj, self.request), ISerializeToJsonSummary)

        serialized_obj = serializer()
        # imio.restapi, end changes, manage returning full object or summary

        # HypermediaBatch can't determine the correct canonical URL for
        # objects that have just been created via POST - so we make sure
        # to set it here
        serialized_obj["@id"] = obj.absolute_url()

        return serialized_obj

    def _reply(self):
        children = []
        if "__children__" in self.data:
            children = self.data.pop("__children__")
            self.request.set("BODY", json.dumps(self.data))
        result = self.do_reply()
        if "error" in result:
            return result
        self.wf_transitions(result)
        self._after_reply_hook(result)
        result["@warnings"] = self.warnings
        if children:
            results = []
            for child in children:
                context = self.context.get(result["id"])
                request = create_request(self.request, json.dumps(child))
                child_request = self.__class__(context, request)
                child_request.warnings = []
                child_request.context = context
                child_request.request = request
                child_request.parent_data = self.data
                child_result = child_request.reply()
                results.append(child_result)
            result["__children__"] = results
        return result


class BulkFolderPost(FolderPost):
    def reply(self):
        data = json_body(self.request)
        result = []
        for element in data["data"]:
            self.request.set("BODY", json.dumps(element))
            result.extend(super(BulkFolderPost, self).create_content())
        return {"data": result}
