# -*- coding: utf-8 -*-

from imio.restapi.vocabularies import base

import os


class ApplicationsVocabularyFactory(base.RestVocabularyFactory):
    """ Vocabulary that return all the applications for the same client """

    @property
    def base_url(self):
        return u"{0}{1}".format(u"{ws_url}/route/", os.getenv("CLIENT_ID"))

    def transform(self, json):
        values = {
            r["application_id"]: r["application_id"] for r in json.get("routes", [])
        }
        return base.dict_2_vocabulary(values)


ApplicationsVocabulary = ApplicationsVocabularyFactory()
