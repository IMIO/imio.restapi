# -*- coding: utf-8 -*-

from imio.restapi.testing import IMIO_RESTAPI_DOCGEN_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

import requests
import unittest


class TestServiceSearchGet(unittest.TestCase):
    """@search"""

    layer = IMIO_RESTAPI_DOCGEN_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

    def test_search_base(self):
        endpoint_url = "{0}/@search".format(self.portal_url)
        response = requests.get(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={},
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertEqual(json[u"items_total"], 12)
        # "id" and "UID" are added to the default search result
        self.assertTrue("UID" in json["items"][0])
        self.assertTrue("id" in json["items"][0])
