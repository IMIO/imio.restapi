# -*- coding: utf-8 -*-
from plone.app.uuid.utils import uuidToObject
from plone.restapi.services.content import update
from zExceptions import BadRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


UID_REQUIRED_ERROR = 'Missing UID'
UID_NOT_FOUND_ERROR = 'No element found with UID "%s"!'


@implementer(IPublishTraverse)
class ContentPatch(update.ContentPatch):
    """Updates an existing content object."""

    def __init__(self, context, request):
        super(ContentPatch, self).__init__(context, request)
        self.uid = None

    def publishTraverse(self, request, name):
        if self.uid is None:
            self.uid = name
        else:
            raise NotFound(self, name, request)
        return self

    def reply(self):
        if self.uid is None:
            raise Exception(UID_REQUIRED_ERROR)
        obj = uuidToObject(uuid=self.uid)
        if not obj:
            raise BadRequest(UID_NOT_FOUND_ERROR % self.uid)

        self.context = obj
        super(ContentPatch, self).reply()
