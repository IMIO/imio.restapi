# -*- coding: utf-8 -*-

from imio.restapi import utils
from imio.restapi.form import tools
from plone.z3cform.fieldsets.extensible import ExtensibleForm
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form.form import Form
from z3c.form.interfaces import ActionExecutionError


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
        url = "{0}/request".format(utils.get_ws_url())
        json_body = {
            "client_id": form.client_id,
            "application_id": form._application_id,
            "request_type": self.action.get("request_type", "POST"),
            "path": self.action["path"],
            "parameters": self.action.get("parameters", {}),
        }
        json_body["parameters"].update({k: v for k, v in data.items() if v})
        result = utils.ws_synchronous_request(
            "POST",
            url,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            auth=("admin", "admin"),
            json=json_body,
        )


class BaseForm(ExtensibleForm, Form):
    ignoreContext = True
    _request_schema = "Document"
    _application_id = "IADELIB"

    @property
    def client_id(self):
        return utils.get_client_id()

    def request_schema(self):
        url = "{0}/request".format(utils.get_ws_url())
        return utils.ws_synchronous_request(
            "POST",
            url,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            auth=("admin", "admin"),
            json={
                "client_id": self.client_id,
                "application_id": self._application_id,
                "request_type": "GET",
                "path": "/@request_schema/{0}".format(self._request_schema),
                "parameters": {},
            },
        )

    def update(self):
        r = self.request_schema()
        if r.status_code == 200:
            schema = r.json()["response"]
            converter = tools.JsonSchema2Z3c(
                schema, self.client_id, self._application_id
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
        self.actions.update()


class FormView(FormWrapper):
    form = BaseForm
