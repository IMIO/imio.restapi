# -*- coding: utf-8 -*-
from plone.app.uuid.utils import uuidToObject
from plone.restapi.services.workflow import transition
from zExceptions import BadRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound


UID_REQUIRED_ERROR = "Missing UID"
TRANSITION_REQUIRED_ERROR = "Missing workflow transition"
UID_NOT_FOUND_ERROR = 'No element found with UID "%s"!'


@implementer(IPublishTraverse)
class WorkflowTransition(transition.WorkflowTransition):
    """Updates an existing content object."""

    def __init__(self, context, request):
        super(WorkflowTransition, self).__init__(context, request)
        self.uid = None

    def publishTraverse(self, request, name):
        if self.uid is None:
            self.uid = name
        else:
            if self.transition is None:
                self.transition = name
            else:
                raise NotFound(self, name, request)
        return self

    def reply(self):
        if self.uid is None:
            raise Exception(UID_REQUIRED_ERROR)
        if self.transition is None:
            raise Exception(TRANSITION_REQUIRED_ERROR)

        obj = uuidToObject(uuid=self.uid)
        if not obj:
            raise BadRequest(UID_NOT_FOUND_ERROR % self.uid)

        self.context = obj
        super(WorkflowTransition, self).reply()
