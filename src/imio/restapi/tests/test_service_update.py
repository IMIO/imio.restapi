# -*- coding: utf-8 -*-
import unittest
from base64 import b64encode

import transaction
from Products.CMFCore.utils import getToolByName
from ZPublisher.pubevents import PubStart
from imio.restapi.testing import IMIO_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from zope.event import notify


class TestContentPatch(unittest.TestCase):

    layer = IMIO_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory(
            "Document", id="doc1", title="My Document", description="Some Description"
        )
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.doc1, "publish")
        transaction.commit()

    def traverse(
        self, path="/plone", accept="application/json", method="PATCH", auth=None
    ):
        request = self.layer["request"]
        request.environ["PATH_INFO"] = path
        request.environ["PATH_TRANSLATED"] = path
        request.environ["HTTP_ACCEPT"] = accept
        request.environ["REQUEST_METHOD"] = method
        if auth is None:
            auth = "%s:%s" % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        request._auth = "Basic %s" % b64encode(auth.encode("utf8")).decode("utf8")
        notify(PubStart(request))
        return request.traverse(path)

    def test_patch_document(self):
        self.request["BODY"] = '{"title": "Patched Document"}'
        uid = self.portal.doc1.UID()
        service = self.traverse("/plone/@content/{0}".format(uid))
        transaction.begin()
        service.reply()
        transaction.commit()
        self.assertEqual(204, self.request.response.getStatus())
        self.assertEqual("Patched Document", self.portal.doc1.Title())

    def test_patch_document_will_delete_value_with_null(self):
        self.assertEqual(self.portal.doc1.description, "Some Description")

        self.request["BODY"] = '{"description": null}'
        uid = self.portal.doc1.UID()
        service = self.traverse("/plone/@content/{0}".format(uid))
        transaction.begin()
        service.reply()
        transaction.commit()
        self.assertEqual(204, self.request.response.getStatus())
        self.assertEqual(u"", self.portal.doc1.description)
