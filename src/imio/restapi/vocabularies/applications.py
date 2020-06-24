# -*- coding: utf-8 -*-

from imio.restapi import utils
from imio.restapi.vocabularies import base


class ApplicationsVocabularyFactory(base.RestVocabularyFactory):
    """ Vocabulary that return all the applications for the same client """

    def body(self):
        return {}

    @property
    def url(self):
        return u"{ws_url}/route/{client_id}".format(
            ws_url=utils.get_ws_url(), client_id=utils.get_client_id()
        )

    def transform(self, json):
        values = {
            r["application_id"]: r["application_id"]
            for r in json.get("routes", [])
            if r["application_id"] not in utils.get_application_id()
        }
        return base.dict_2_vocabulary(values)


ApplicationsVocabulary = ApplicationsVocabularyFactory()
