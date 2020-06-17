# -*- coding: utf-8 -*-

from plone.restapi.deserializer import json_body
from plone.restapi.services.content import add
from ZPublisher.HTTPRequest import HTTPRequest

import json


def create_request(base_request, body):
    request = HTTPRequest(
        base_request.stdin, base_request._orig_env, base_request.response
    )
    for attr in base_request.__dict__.keys():
        setattr(request, attr, getattr(base_request, attr))
    request.set("BODY", body)
    return request


class FolderPost(add.FolderPost):
    def reply(self):
        data = json_body(self.request)
        children = []
        if "__children__" in data:
            children = data.pop("__children__")
            self.request.set("BODY", json.dumps(data))
        result = super(FolderPost, self).reply()
        if children:
            results = []
            for child in children:
                context = self.context.get(result["id"])
                request = create_request(self.request, json.dumps(child))
                child_request = FolderPost()
                child_request.context = context
                child_request.request = request
                results.append(child_request.reply())
            result["__children__"] = results
        return result


class BulkFolderPost(FolderPost):
    def reply(self):
        data = json_body(self.request)
        result = []
        for element in data["data"]:
            self.request.set("BODY", json.dumps(element))
            result.extend(super(BulkFolderPost, self).create_content())
        return {"data": result}
