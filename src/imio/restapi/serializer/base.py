# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from imio.restapi.interfaces import IImioRestapiLayer
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer import dxcontent
from plone.restapi.serializer import summary
from plone.restapi.serializer.summary import DEFAULT_METADATA_FIELDS
from plone.restapi.serializer.summary import NON_METADATA_ATTRIBUTES
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.interfaces import ICatalogBrain
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

    def _get_metadata_fields_name(self):
        """May be overrided when necessary."""
        return "metadata_fields"

    def metadata_fields(self):
        """Override from plone.restapi to be able to change the metadata_fields name..."""
        # following line is replaced
        # additional_metadata_fields = self.request.form.get("metadata_fields", [])
        additional_metadata_fields = self.request.form.get(self._get_metadata_fields_name(), [])
        if not isinstance(additional_metadata_fields, list):
            additional_metadata_fields = [additional_metadata_fields]
        # following line is added, additional metadata_fields
        additional_metadata_fields += self._additional_fields

        additional_metadata_fields = set(additional_metadata_fields)

        if "_all" in additional_metadata_fields:
            fields_cache = self.request.get("_summary_fields_cache", None)
            if fields_cache is None:
                catalog = getToolByName(self.context, "portal_catalog")
                fields_cache = set(catalog.schema()) | NON_METADATA_ATTRIBUTES
                self.request.set("_summary_fields_cache", fields_cache)
            additional_metadata_fields = fields_cache

        return DEFAULT_METADATA_FIELDS | additional_metadata_fields
