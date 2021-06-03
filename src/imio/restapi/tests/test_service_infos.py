# -*- coding: utf-8 -*-

from imio.restapi.services.infos import STATS_UNAUTHORIZED
from imio.restapi.testing import IMIO_RESTAPI_DOCGEN_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

import os
import requests
import transaction
import unittest


class testServiceInfosGet(unittest.TestCase):
    layer = IMIO_RESTAPI_DOCGEN_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

    def test_restapi_infos_endpoint(self):
        """@infos"""
        endpoint_url = "{0}/@infos".format(self.portal_url)
        response = requests.get(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={},
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        # return versions and connected_user
        self.assertTrue(u"imio.restapi" in json["packages"])
        self.assertEqual(json["connected_user"], TEST_USER_ID)

        # when not connected
        response = requests.get(
            endpoint_url, headers={"Accept": "application/json"}, auth=(), json={},
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        # return versions and connected_user
        self.assertTrue(u"imio.restapi" in json["packages"])
        self.assertEqual(json["connected_user"], None)
        # stats empty
        self.assertEqual(json["stats"], {})

    def test_restapi_infos_stats(self):
        """@infos?include_stats=1"""
        endpoint_url = "{0}/@infos?include_stats=1".format(self.portal_url)
        # only available to Manager
        response = requests.get(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(), {u"message": STATS_UNAUTHORIZED, u"type": u"Unauthorized"}
        )
        api.user.grant_roles(TEST_USER_NAME, roles=["Manager"])
        logout()
        login(self.portal, TEST_USER_NAME)
        transaction.commit()
        # stats contains various data
        response = requests.get(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue(u"database" in json["stats"])
        self.assertTrue(u"groups" in json["stats"])
        self.assertTrue(u"users" in json["stats"])
        self.assertTrue(u"types" in json["stats"])
        # when PWD does not exist, INSTANCE_HOME is used
        os.environ["INSTANCE_HOME"] = os.environ["PWD"]
        del os.environ["PWD"]
        response = requests.get(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
        )
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue(u"database" in json["stats"])
        self.assertTrue(u"groups" in json["stats"])
        self.assertTrue(u"users" in json["stats"])
        self.assertTrue(u"types" in json["stats"])
