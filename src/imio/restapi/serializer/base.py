# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from plone.restapi.serializer import dxcontent
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.interface import implementer
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from imio.restapi.interfaces import IImioRestapiLayer
from plone import api


@implementer(ISerializeToJson)
@adapter(IDexterityContent, IImioRestapiLayer)
class SerializeToJson(dxcontent.SerializeToJson):
    def __call__(self, *args, **kwargs):
        result = super(SerializeToJson, self).__call__(*args, **kwargs)
        result["@relative_path"] = get_relative_path(self.context)
        return result


@implementer(ISerializeToJson)
@adapter(IDexterityContainer, IImioRestapiLayer)
class SerializeFolderToJson(dxcontent.SerializeFolderToJson):
    def __call__(self, *args, **kwargs):
        result = super(SerializeFolderToJson, self).__call__(*args, **kwargs)
        result["@relative_path"] = get_relative_path(self.context)
        return result


def get_relative_path(context):
    context = aq_inner(context)
    portal = api.portal.get()

    relative_path = context.getPhysicalPath()[len(portal.getPhysicalPath()):]
    return "/{}".format("/".join(relative_path))
