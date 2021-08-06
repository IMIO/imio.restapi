# -*- coding: utf-8 -*-

from imio.restapi import utils
from imio.restapi.interfaces import IRESTLink
from persistent import Persistent
from persistent.list import PersistentList
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.fieldproperty import FieldProperty


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


def add_remote_link(context, path, remote_application_id, back_link=False):
    # XXX To be implemented
    client_id = utils.get_client_id()
    r_args, r_kwargs = utils.generate_request_parameters(
        "{0}/@rest_link".format(path), client_id, remote_application_id
    )
    parameters = {
        "path": context.absolute_url(),
        "uid": context.UID(),
        "title": context.Title(),
        "application_id": utils.get_application_id(),
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
    _back_link = FieldProperty(IRESTLink["back_link"])

    def __init__(self, path, uid, title, application_id, back_link=False):
        self.path = path
        self.uid = uid
        self.title = title
        self.application_id = application_id
        self.back_link = back_link

    @property
    def path(self):
        return getattr(self, "_path", "")

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def uid(self):
        return getattr(self, "_uid", None)

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def title(self):
        return getattr(self, "_title", "missing")

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def application_id(self):
        return getattr(self, "_application_id", None)

    @application_id.setter
    def application_id(self, value):
        self._application_id = value

    @property
    def back_link(self):
        return self._back_link

    @back_link.setter
    def back_link(self, value):
        self._back_link = value


@adapter(dict, Interface)
class RESTLink(RESTLinkObject):
    def __init__(self, result, context):
        super(RESTLink, self).__init__(
            result["response"]["@relative_path"],
            result["response"]["UID"],
            result["response"]["title"],
            result["application_id"],
        )

    def add_on(self, context):
        """ Add the link on the given context """
        add_link(context, self)


class RestLinkView(BrowserView):
    index = ViewPageTemplateFile("templates/link.pt")

    def render(self):
        return self.index()
