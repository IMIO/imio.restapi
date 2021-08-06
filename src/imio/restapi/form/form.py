# -*- coding: utf-8 -*-

from imio.restapi import _
from imio.restapi import utils
from imio.restapi.form import tools
from imio.restapi.form.link import add_link
from imio.restapi.form.link import add_remote_link
from imio.restapi.interfaces import IRESTLink
from plone.dexterity.interfaces import IDexterityContent
from plone.memoize.view import memoize
from plone.restapi.interfaces import IFieldSerializer
from plone.z3cform.fieldsets.extensible import ExtensibleForm
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form.form import Form
from z3c.form.interfaces import ActionExecutionError
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


@implementer(IDexterityContent, Interface)
class DummyObject(object):
    """ Dummy dexterity object """


class GeneratedButton(button.Button):
    def actionFactory(self, request, field):
        return button.ButtonAction(request, field)


class GeneratedButtonActions(button.ButtonActions):
    def __init__(self, *args, **kwargs):
        self._handlers = {}
        super(GeneratedButtonActions, self).__init__(*args, **kwargs)

    def add_handler(self, name, handler):
        if name not in self._handlers:
            self._handlers[name] = handler

    def execute(self):
        for action in self.executedActions:
            handler = self._handlers.get(action.field.__name__)
            if handler is not None:
                try:
                    result = handler(self.form, action)
                except ActionExecutionError:
                    pass
                else:
                    return result


class ButtonHandler(button.Handler):
    def __init__(self, button, action):
        self.button = button
        self.action = action
        self.func = self._execute

    def _execute(self, form, action):
        data, errors = form.extractData()
        if errors:
            form.status = form.formErrorsMessage
            return
        data = self._serialize_data(form, data)
        r_args, r_kwargs = form.base_request_parameters
        r_kwargs["json"]["request_type"] = self.action.get("request_type", "POST")
        r_kwargs["json"]["path"] = self.action["path"]
        r_kwargs["json"]["parameters"] = self.action.get("parameters", {})
        r_kwargs["json"]["parameters"].update({k: v for k, v in data.items() if v})
        r_kwargs["json"]["parameters"]["_rest_link_uid"] = form.context.UID()
        result = utils.ws_synchronous_request(*r_args, **r_kwargs)
        if form._add_link is True:
            json_result = result.json()
            link = getMultiAdapter((json_result, form), IRESTLink)
            add_link(form.context, link)
            add_remote_link(
                form.context,
                json_result["response"]["@id"],
                form.application_id,
                form._request_schema,
            )
        status_message = IStatusMessage(form.request)
        status_message.addStatusMessage(
            form.message.format(title=json_result["response"]["title"]), type="info"
        )
        form.request.response.redirect(form.context.absolute_url())

    def _get_field(self, form, key):
        if key in form.fields:
            return form.fields[key].field
        for group in form.groups:
            if key in group.fields:
                return group.fields[key].field
        raise ValueError

    def _serialize_data(self, form, data):
        dummy_object = type("dummy dexterity object", (DummyObject,), data)()
        for key, value in data.items():
            serializer = queryMultiAdapter(
                (self._get_field(form, key), dummy_object, form.request),
                IFieldSerializer,
            )
            if serializer:
                data[key] = serializer()
        return data


class BaseForm(ExtensibleForm, Form):
    ignoreContext = True
    _request_schema = None
    _application_id = None
    _add_link = True
    _message = _("The content {title} was created")

    @property
    def client_id(self):
        return utils.get_client_id()

    @property
    def request_schema(self):
        return self._request_schema

    @property
    def application_id(self):
        return self._application_id

    @property
    def message(self):
        return translate(self._message, context=self.request)

    @property
    def base_request_parameters(self):
        args = ("POST", "{0}/request".format(utils.get_ws_url()))
        kwargs = {
            "headers": {
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            "json": {
                "client_id": self.client_id,
                "application_id": self.application_id,
                "parameters": {},
            },
        }
        return args, kwargs

    @memoize
    def get_request_schema(self):
        args, kwargs = self.base_request_parameters
        kwargs["json"]["request_type"] = "GET"
        kwargs["json"]["path"] = "/@request_schema/{0}".format(self.request_schema)
        auth = utils.get_authentication(self.request)
        if auth:
            kwargs["json"]["auth"] = auth
        return utils.ws_synchronous_request(*args, **kwargs)

    def update(self):
        if self._request_schema is not None:
            r = self.get_request_schema()
            if r.status_code == 200:
                schema = r.json()["response"]
                converter = tools.JsonSchema2Z3c(
                    schema, self.client_id, self.application_id
                )
                self.title = converter.form_title
                self.fields = converter.generated_fields
                self.groups = converter.generated_groups
                self.buttons = self.create_buttons(schema)
                self.actions = self.create_actions(schema)
        super(BaseForm, self).update()

    def create_buttons(self, schema):
        return button.Buttons(
            *[
                GeneratedButton(str(e["id"]), title=e["title"])
                for e in schema.get("actions", [])
            ]
        )

    def create_actions(self, schema):
        actions = GeneratedButtonActions(self, self.request, self.getContent())
        for action_data in schema.get("actions", []):
            button_field = self.buttons[action_data["id"]]
            actions.add_handler(
                button_field.__name__,
                ButtonHandler(button_field, action_data["action"]),
            )
        return actions

    def updateActions(self):
        if self._request_schema is not None:
            self.actions.update()
        else:
            super(BaseForm, self).updateActions()


class ImportForm(BaseForm):
    _message = _("The content(s) was imported")

    def _get_data(self, data):
        """ Return an iterable with the relative path of Plone objects to create """
        raise NotImplementedError

    @button.buttonAndHandler(_(u"Import"))
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        for path in self._get_data(data):
            utils.import_content(
                self.context, self.request, self.client_id, self.application_id, path
            )
        self.request.response.redirect(self.context.absolute_url())
