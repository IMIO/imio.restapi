# -*- coding: utf-8 -*-

from imio.restapi.interfaces import IRESTAction
from plone import api
from plone.app.layout.viewlets import common as base
from zope.component import getAdapters


class ActionViewlet(base.ViewletBase):
    """Viewlet that display the actions that can be made with the REST api
    on the current context"""

    actions = []

    @property
    def available(self):
        return True

    def update(self):
        if self.available:
            self._apps = api.portal.get_registry_record(
                name="imio.restapi.settings.interfaces.ISettings.application_links",
                default=[],
            )
            self.actions = self._get_actions()

    def _get_actions(self):
        actions = []
        for key, adapter in getAdapters((self.context, self.request), IRESTAction):
            if adapter.application_id in self._apps:
                actions.append(adapter)
        return actions
