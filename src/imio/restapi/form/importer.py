# -*- coding: utf-8 -*-

from imio.restapi.interfaces import IContentImporter
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IContentImporter)
@adapter(dict, Interface)
class BaseContentImporter(object):
    _fields = []  # An explicit list of field that should be used

    def __init__(self, raw_data, context):
        self.raw_data = raw_data
        self.context = context

    @property
    def fields(self):
        """ Return the filtered fields in addition to the mandatory fields """
        base = ["@type", "UID", "id", "title"]
        return list(set(base + self._fields))

    def transform_data(self, data):
        """ Hook method that allow data transform """
        return data

    def parse_data(self):
        if not self._fields:
            return self.transform_data(self.raw_data)
        return self.transform_data({k: self.raw_data[k] for k in self.fields})
