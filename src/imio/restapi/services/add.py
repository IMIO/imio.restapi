# -*- coding: utf-8 -*-

from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services.content import add
from ZPublisher.HTTPRequest import HTTPRequest
from zExceptions import BadRequest

import json

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


class FolderPost(add.FolderPost):
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
        """Hook to be overrided if necessary, by default manage
           the 'wf_transitions' if given."""
        self.wf_transitions(serialized_obj)

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

    def _reply(self):
        children = []
        if "__children__" in self.data:
            children = self.data.pop("__children__")
            self.request.set("BODY", json.dumps(self.data))
        result = super(FolderPost, self).reply()
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
