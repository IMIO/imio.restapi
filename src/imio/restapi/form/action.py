# -*- coding: utf-8 -*-

from imio.restapi.interfaces import IRESTAction
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@implementer(IRESTAction)
class RESTAction(object):
    template = ViewPageTemplateFile("templates/action.pt")

    id = FieldProperty(IRESTAction["id"])
    title = FieldProperty(IRESTAction["title"])
    application_id = FieldProperty(IRESTAction["application_id"])
    schema_name = FieldProperty(IRESTAction["schema_name"])
    view_name = FieldProperty(IRESTAction["view_name"])

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def klass(self):
        return u"action action-{0}".format(self.id)

    @property
    def url(self):
        return u"{0}/@@{1}".format(self.context.absolute_url(), self.view_name)

    def render(self):
        return self.template()
