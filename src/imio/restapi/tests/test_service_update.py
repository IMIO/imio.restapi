# -*- coding: utf-8 -*-
from imio.restapi.testing import IMIO_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName

import requests
import transaction
import unittest


class TestContentPatch(unittest.TestCase):
    layer = IMIO_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory(
            "Document", id="doc1", title="My Document", description="Some Description"
        )
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.doc1, "publish")
        transaction.commit()

    def tearDown(self):
        login(self.portal, SITE_OWNER_NAME)
        self.portal.manage_delObjects(["doc1"])
        transaction.commit()

    def test_patch_document(self):
        self.request["BODY"] = '{"title": "Patched Document"}'

        uid = self.portal.doc1.UID()
        endpoint_url = "{0}/@content/{1}".format(self.portal_url, uid)
        response = requests.patch(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"title": "Patched Document"},
        )
        transaction.commit()
        self.assertEqual(204, response.status_code)
        self.assertEqual("Patched Document", self.portal.doc1.Title())

    def test_patch_document_will_delete_value_with_null(self):
        self.assertEqual(self.portal.doc1.description, "Some Description")
        uid = self.portal.doc1.UID()
        endpoint_url = "{0}/@content/{1}".format(self.portal_url, uid)
        response = requests.patch(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"description": ""},
        )
        transaction.commit()
        self.assertEqual(204, response.status_code)
        self.assertEqual(u"", self.portal.doc1.description)

    def test_patch_document_unauthorized(self):
        uid = self.portal.doc1.UID()
        endpoint_url = "{0}/@content/{1}".format(self.portal_url, uid)
        response = requests.patch(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={"description": ""},
        )
        transaction.commit()
        self.assertEqual(401, response.status_code)
