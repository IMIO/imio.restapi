# -*- coding: utf-8 -*-

from plone.restapi.services.vocabularies import get


class ATVocabulariesGet(get.VocabulariesGet):
    """ """

    @property
    def vocabulary_name(self):
        if len(self.params) == 0:
            raise ValueError("Missing vocabulary name")
        return self.params[0]

    def serialize(self, factory, name):
        vocabulary = factory()
        vocabulary_id = "{}/@at_vocabularies/{}".format(
            self.context.absolute_url(), name
        )
        term_id = "{}/{}"
        return {
            "@id": vocabulary_id,
            "terms": [
                {
                    "@id": term_id.format(vocabulary_id, token),
                    "title": title.encode("utf8"),
                    "token": token,
                }
                for token, title in vocabulary.items()
            ],
        }

    def reply(self):
        try:
            name = self.vocabulary_name
            factory = getattr(self.context, name)
        except AttributeError:
            return self._error(
                404, "Not Found", 'The vocabulary "{}" does not exist'.format(name)
            )
        return self.serialize(factory, name)
