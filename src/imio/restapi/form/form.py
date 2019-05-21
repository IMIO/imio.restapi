# -*- coding: utf-8 -*-

from imio.restapi import utils
from imio.restapi.form import tools
from plone.z3cform.fieldsets.extensible import ExtensibleForm
from plone.z3cform.layout import FormWrapper
from z3c.form.form import Form


class BaseForm(ExtensibleForm, Form):
    ignoreContext = True
    _request_schema = "foo"
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
            converter = tools.JsonSchema2Z3c(
                r.json()["response"], self.client_id, self._application_id
            )
            self.title = converter.form_title
            self.fields = converter.generated_fields
            self.groups = converter.generated_groups
        super(BaseForm, self).update()


class FormView(FormWrapper):
    form = BaseForm
