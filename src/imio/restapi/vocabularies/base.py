# -*- coding: utf-8 -*-

from zope.schema.vocabulary import SimpleVocabulary

import requests
import os


def dict_2_vocabulary(dictionary):
    """Transform a dictionary into a vocabulary"""
    terms = [SimpleVocabulary.createTerm(k, k, v)
             for k, v in dictionary.items()]
    return SimpleVocabulary(terms)


class RestVocabularyFactory(object):
    method = 'GET'

    @property
    def base_url(self):
        """ Example : {ws_url}/request """
        raise NotImplementedError

    @property
    def body(self):
        raise NotImplementedError

    def transform(self, json):
        raise NotImplementedError

    @property
    def ws_url(self):
        return os.getenv('WS_URL')

    @property
    def headers(self):
        return {'Accept': 'application/json'}

    @property
    def url(self):
        return self.base_url.format(ws_url=self.ws_url)

    def __call__(self, context):
        if self.method == 'GET':
            r = requests.get(
                self.url,
                headers=self.headers,
                auth=('admin', 'admin'),
            )
        elif self.method == 'POST':
            r = requests.post(
                self.url,
                headers=self.headers,
                auth=('admin', 'admin'),
                body=self.body,
            )
        if r.status_code == 200:
            return self.transform(r.json())
        return self.transform({})


class RemoteRestVocabularyFactory(RestVocabularyFactory):
    method = 'POST'
