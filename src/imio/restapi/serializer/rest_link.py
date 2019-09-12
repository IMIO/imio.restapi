# -*- coding: utf-8 -*-

from imio.restapi.interfaces import IRESTLink
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(IRESTLink, Interface)
class SerializeRestLinkToJson(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, version=None):
        version = "current" if version is None else version
        if version != "current":
            return {}

        result = {
            "path": self.context.path,
            "uid": self.context.uid,
            "title": self.context.title,
            "application_id": self.context.application_id,
            "schema_name": self.context.schema_name,
        }

        return result
