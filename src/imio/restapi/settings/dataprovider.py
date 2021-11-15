# -*- coding: utf-8 -*-

from imio.restapi.settings.interfaces import ISettings
from plone import api
from plone.restapi.deserializer import boolean_value
from z3c.form.interfaces import IForm
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IValue
from z3c.form.interfaces import IWidget
from z3c.form.interfaces import NO_VALUE
from zope.component import adapts
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IField

import os


@implementer(IValue)
class SettingsDataProvider(object):
    adapts(Interface, IFormLayer, IForm, IField, IWidget)

    # env vars with name as key and default value as value
    _env_keys = {
        "WS_URL": "",
        "CLIENT_ID": "",
        "APPLICATION_ID": "",
        "APPLICATION_URL": "",
        "RETURN_FULLOBJECT_AFTER_CREATION_DEFAULT": True}

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self._values = {}

    def get(self):
        key = self.field.__name__
        if key in self.values:
            return self.values[key]
        return api.portal.get_registry_record(
            key, interface=ISettings, default=NO_VALUE
        )

    @property
    def values(self):
        if not self._values:
            self._values = {
                k.lower(): boolean_value(os.getenv(k, default))
                if isinstance(default, bool) else os.getenv(k, default)
                for k, default in self._env_keys.items()}
        return self._values
