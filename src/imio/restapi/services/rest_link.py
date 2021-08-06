# -*- coding: utf-8 -*-

from imio.restapi.form.link import add_link
from imio.restapi.form.link import get_links
from imio.restapi.form.link import remove_link
from imio.restapi.form.link import RESTLinkObject
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class BaseLinkService(Service):
    def __init__(self, context, request):
        super(BaseLinkService, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, uid):
        # Treat any path segments after /@rest_link as parameters
        self.params.append(uid)
        return self

    @property
    def _link_uid(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (dotted name of"
                "the record to be retrieved)"
            )
        return self.params[0]


class LinkPost(Service):
    def reply(self):
        data = json_body(self.request)
        required_values = ("path", "uid", "title", "application_id")

        values = {k: data.get(k, None) for k in required_values}
        missing_values = [k for k in values.keys() if values[k] is None]

        if missing_values:
            raise BadRequest(
                "Properties ({0}) are required".format(", ".join(missing_values))
            )
        link = RESTLinkObject(
            values["path"], values["uid"], values["title"], values["application_id"]
        )
        add_link(self.context, link)
        serializer = queryMultiAdapter((link, self.request), ISerializeToJson)
        return serializer()


class LinkGet(BaseLinkService):
    def reply(self):
        links = get_links(self.context)
        result = {"links": []}
        if links is None:
            return result
        for link in links:
            if self._link_uid and link.uid != self._link_uid:
                continue
            serializer = queryMultiAdapter((link, self.request), ISerializeToJson)
            result["links"].append(serializer())
        return result


class LinkDelete(BaseLinkService):
    def reply(self):
        link = remove_link(self.context, uid=self._link_uid)
        if not link:
            self.request.response.setStatus(204)
            return None
        serializer = queryMultiAdapter((link, self.request), ISerializeToJson)
        result = {"links": [serializer()]}
        return result


@implementer(IPublishTraverse)
class LinkPatch(Service):
    # XXX To be implemented
    pass
