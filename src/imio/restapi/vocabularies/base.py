# -*- coding: utf-8 -*-

from imio.restapi import utils
from plone.memoize import ram
from time import time
from zope.schema.vocabulary import SimpleVocabulary


def dict_2_vocabulary(dictionary):
    """Transform a dictionary into a vocabulary"""
    terms = [SimpleVocabulary.createTerm(k, k, v) for k, v in dictionary.items()]
    return SimpleVocabulary(terms)


def _rest_vocabulary_cache_key(func, obj):
    return (func, getattr(obj, "body", {}), time() // (5 * 60))


class RestVocabularyFactory(object):
    method = "GET"

    @property
    def body(self):
        raise NotImplementedError

    def transform(self, json):
        raise NotImplementedError

    @property
    def headers(self):
        return {"Accept": "application/json", "Content-Type": "application/json"}

    @property
    def url(self):
        raise NotImplementedError

    def synchronous_request(self):
        args = (self.method, self.url)
        kwargs = {"headers": self.headers, "auth": ("admin", "admin")}
        if self.method == "POST":
            kwargs["json"] = self.body
        return utils.ws_synchronous_request(*args, **kwargs)

    def __call__(self, context):
        self.context = context
        r = self.synchronous_request()
        if r.status_code == 200:
            return self.transform(r.json())
        return self.transform({})


class RemoteRestVocabularyFactory(SimpleVocabulary, RestVocabularyFactory):
    method = "POST"
    request_type = "GET"
    vocabulary_name = None
    application_id = None

    def __init__(self, *interfaces, **kwargs):
        """ Override of SimpleVocabulary __init__ """
        terms = self.get_terms()
        super(RemoteRestVocabularyFactory, self).__init__(terms, *interfaces, **kwargs)

    @property
    def url(self):
        return "{ws_url}/request".format(ws_url=utils.get_ws_url())

    @property
    def client_id(self):
        return utils.get_client_id()

    @property
    def body(self):
        return {
            "client_id": self.client_id,
            "application_id": self.application_id,
            "request_type": self.request_type,
            "path": self.request_path,
            "parameters": self.parameters,
        }

    @property
    def request_path(self):
        return "/@vocabularies/{0}".format(self.vocabulary_name)

    @property
    def parameters(self):
        return {}

    def transform(self, json_body):
        terms_values = json_body["response"].get("terms", [])
        return [
            self.createTerm(e["token"], e["token"], e["title"]) for e in terms_values
        ]

    @ram.cache(_rest_vocabulary_cache_key)
    def get_terms(self):
        r = self.synchronous_request()
        if r.status_code == 200:
            return self.transform(r.json())
        return self.transform({})
