# -*- coding: utf-8 -*-

from imio.restapi.vocabularies import base
from imio.restapi import utils


class ApplicationsVocabularyFactory(base.RestVocabularyFactory):
    """ Vocabulary that return all the applications for the same client """

    @property
    def url(self):
        return u"{ws_url}/route/{client_id}".format(
            ws_url=utils.get_ws_url(), client_id=utils.get_client_id()
        )

    def transform(self, json):
        values = {
            r["application_id"]: r["application_id"] for r in json.get("routes", [])
        }
        return base.dict_2_vocabulary(values)


ApplicationsVocabulary = ApplicationsVocabularyFactory()
