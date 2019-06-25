# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from plone.restapi.services import Service
from zExceptions import Unauthorized
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import Interface
from zope.component import queryMultiAdapter


class IRequestSchema(Interface):
    """ """


@implementer(IRequestSchema)
class RequestSchemaAdapter(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_schema(self):
        """ Return the json associated schema """
        raise NotImplementedError


@implementer(IPublishTraverse)
class RequestSchemaGet(Service):
    def __init__(self, context, request):
        super(RequestSchemaGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    @property
    def _request_name(self):
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

        self.content_type = "application/json+schema"
        adapter = queryMultiAdapter(
            (self.context, self.request), IRequestSchema, name=self._request_name
        )
        if not adapter:
            self.content_type = "application/json"
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": 'Type "{}" could not be found.'.format(self._request_name),
            }
        return adapter.get_schema()
