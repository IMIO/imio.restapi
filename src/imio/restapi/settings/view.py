# -*- coding: utf-8 -*-

from imio.restapi import _
from imio.restapi.settings.interfaces import ISettings
from imio.restapi.settings.interfaces import ISettingsForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope.interface import implementer


@implementer(ISettingsForm)
class SettingsEditForm(RegistryEditForm):
    schema = ISettings
    label = _(u"Imio REST API")
    ignoreContext = True


SettingsView = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)
