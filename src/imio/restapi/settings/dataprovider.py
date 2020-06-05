# -*- coding: utf-8 -*-

from imio.restapi.settings.interfaces import ISettings
from plone import api
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

    _env_keys = ("WS_URL", "CLIENT_ID", "APPLICATION_ID", "APPLICATION_URL")

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

    def get(self):
        key = self.field.__name__
        if key in self.values:
            return self.values[key]
        return api.portal.get_registry_record(
            key, interface=ISettings, default=NO_VALUE
        )

    @property
    def values(self):
        return {k.lower(): os.getenv(k) for k in self._env_keys}
