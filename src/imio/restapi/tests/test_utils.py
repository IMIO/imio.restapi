# -*- coding: utf-8 -*-
from imio.helpers.content import get_vocab
from imio.restapi.testing import IMIO_RESTAPI_INTEGRATION_TESTING  # noqa
from imio.restapi.utils import serialize_term

import unittest


class TestUtils(unittest.TestCase):
    """ """

    layer = IMIO_RESTAPI_INTEGRATION_TESTING

    def test_serialize_term(self):
        """This helper will serialize a vocabulary term the same way FieldSerializer does it."""
        vocab = get_vocab(self.layer["portal"], "plone.app.vocabularies.PortalTypes")
        self.assertEqual(
            serialize_term("Document", vocab),
            {'token': 'Document', 'title': u'Page'})
        # breaks if token not found
        self.assertRaises(LookupError, serialize_term, "Unknown", vocab)
