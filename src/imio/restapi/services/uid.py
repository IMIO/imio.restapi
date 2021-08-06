# -*- coding: utf-8 -*-

from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class UIDGet(Service):
    def __init__(self, context, request):
        super(UIDGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, uid):
        # Treat any path segments after /@uid as parameters
        self.params.append(uid)
        return self

    @property
    def _uid(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (dotted name of"
                "the record to be retrieved)"
            )

        return self.params[0]

    def check_security(self):
        # Only expose type information to authenticated users
        portal_membership = getToolByName(self.context, "portal_membership")
        if portal_membership.isAnonymousUser():
            raise Unauthorized

    def reply(self):
        self.check_security()
        obj = api.content.get(UID=self._uid)
        if not obj:
            self.request.response.setStatus(204)
            return None
        serializer = queryMultiAdapter((obj, self.request), ISerializeToJson)

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message="No serializer available."))

        return serializer(version=self.request.get("version"))
