# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from imio.restapi.interfaces import IImioRestapiLayer
from imio.restapi.utils import listify
from Products.ZCatalog.interfaces import ICatalogBrain
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer import dxcontent
from plone.restapi.serializer import summary
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


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


@implementer(ISerializeToJsonSummary)
@adapter(ICatalogBrain, Interface)
class DefaultJSONSummarySerializer(summary.DefaultJSONSummarySerializer):
    """Formalize management of defining extra metadata_fields in the serializer."""

    @property
    def _additional_fields(self):
        """By default add 'id' and 'UID' to returned data."""
        return ["id", "UID"]

    def _set_metadata_fields(self):
        """Must be set in request.form."""
        form = self.request.form
        # manage metadata_fields
        additional_metadata_fields = listify(form.get("metadata_fields", []))
        additional_metadata_fields += self._additional_fields
        form["metadata_fields"] = additional_metadata_fields

    def __call__(self):
        """ """
        self._set_metadata_fields()
        result = super(DefaultJSONSummarySerializer, self).__call__()
        return result
