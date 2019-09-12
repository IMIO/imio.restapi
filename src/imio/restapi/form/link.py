# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView
from imio.restapi.interfaces import IRESTLink
from imio.restapi import utils
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


def add_remote_link(context, path, remote_application_id, schema_name):
    client_id = utils.get_client_id()
    r_args, r_kwargs = utils.generate_request_parameters(
        "{0}/@rest_link".format(path), client_id, remote_application_id
    )
    parameters = {
        "path": context.absolute_url(),
        "uid": context.UID(),
        "title": context.Title(),
        "application_id": utils.get_application_id(),
        "schema_name": schema_name,
    }
    r_kwargs["json"]["parameters"] = parameters
    utils.ws_asynchronous_request(*r_args, **r_kwargs)


def update_link(context, link):
    """Synchronize the link informations with the source object"""
    # XXX To be implemented
    pass


def remove_link(context, link=None, uid=None):
    """Remove the link, this do not remove the source object"""
    links = get_links(context)
    if link is None and uid is not None:
        search = [e for e in links if e.uid == uid]
        if len(search) == 0:
            return
        link = search[0]
    links.remove(link)
    return link


@implementer(IRESTLink)
class RESTLinkObject(Persistent):
    """
    A persistent link to an object created or retrieved by REST API
    """

    _path = FieldProperty(IRESTLink["path"])
    _uid = FieldProperty(IRESTLink["uid"])
    _title = FieldProperty(IRESTLink["title"])
    _application_id = FieldProperty(IRESTLink["application_id"])
    _schema_name = FieldProperty(IRESTLink["schema_name"])

    def __init__(self, path, uid, title, application_id, schema_name):
        self._path = path
        self._uid = uid
        self._title = title
        self._application_id = application_id
        self._schema_name = schema_name

    @property
    def path(self):
        return getattr(self, "_path", "")

    @property
    def uid(self):
        return getattr(self, "_uid", None)

    @property
    def title(self):
        return getattr(self, "_title", "missing")

    @property
    def application_id(self):
        return getattr(self, "_application_id", None)

    @property
    def schema_name(self):
        return getattr(self, "_schema_name", None)


@adapter(dict, Interface)
class RESTLink(RESTLinkObject):
    def __init__(self, result, form):
        super(RESTLink, self).__init__(
            result["response"]["@id"],
            result["response"]["UID"],
            result["response"]["title"],
            result["application_id"],
            unicode(form._request_schema),
        )


class RestLinkView(BrowserView):
    index = ViewPageTemplateFile("templates/link.pt")

    def render(self):
        return self.index()
