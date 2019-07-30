# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from imio.restapi.interfaces import IRESTLink
from persistent import Persistent
from persistent.list import PersistentList
from zope.annotation import IAnnotations
from zope.interface import implementer
from zope.component import adapter
from zope.schema.fieldproperty import FieldProperty
from zope.interface import Interface

ANNOTATION_KEY = "imio.restapi.link"


def get_links(context):
    annotations = IAnnotations(context)
    if ANNOTATION_KEY not in annotations:
        return None
    return annotations[ANNOTATION_KEY]


def initialize_links(context):
    annotations = IAnnotations(context)
    if ANNOTATION_KEY not in annotations:
        annotations[ANNOTATION_KEY] = PersistentList()
    return annotations[ANNOTATION_KEY]


def add_link(context, link):
    links = get_links(context)
    if links is None:
        links = initialize_links(context)
    links.append(link)


@implementer(IRESTLink)
@adapter(dict, Interface)
class RESTLink(Persistent):
    """
    A persistent link to an object created or retrieved by REST API
    """
    _path = FieldProperty(IRESTLink["path"])
    _uid = FieldProperty(IRESTLink["uid"])
    _title = FieldProperty(IRESTLink["title"])
    _application_id = FieldProperty(IRESTLink["application_id"])
    _schema_name = FieldProperty(IRESTLink["schema_name"])

    def __init__(self, result, form):
        self._path = result["response"]["@id"]
        self._uid = result["response"]["UID"]
        self._title = result["response"]["title"]
        self._application_id = result["application_id"]
        self._schema_name = unicode(form._request_schema)

    @property
    def path(self):
        return getattr(self, '_path', '')

    @property
    def uid(self):
        return getattr(self, '_uid', None)

    @property
    def title(self):
        return getattr(self, '_title', 'missing')

    @property
    def application_id(self):
        return getattr(self, '_application_id', None)

    @property
    def schema_name(self):
        return getattr(self, '_schema_name', None)


class RestLinkView(BrowserView):
    index = ViewPageTemplateFile("templates/link.pt")

    def render(self):
        return self.index()
