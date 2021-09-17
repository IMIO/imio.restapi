# -*- coding: utf-8 -*-
from DateTime import DateTime
from imio.restapi.testing import IMIO_RESTAPI_WORKFLOWS_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName
from unittest import TestCase

import requests
import transaction


class TestWorkflowTransition(TestCase):

    layer = IMIO_RESTAPI_WORKFLOWS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        self.wftool = getToolByName(self.portal, "portal_workflow")
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory("Document", id="doc1")
        self.folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder", title="Test")
        ]
        self.subfolder = self.folder[
            self.folder.invokeFactory("Folder", id="subfolder")
        ]
        transaction.commit()

    def tearDown(self):
        login(self.portal, SITE_OWNER_NAME)
        self.portal.manage_delObjects(["doc1"])
        self.portal.manage_delObjects(["folder"])
        transaction.commit()

    def test_transition_action_succeeds(self):
        uid = self.portal.doc1.UID()
        endpoint_url = "{0}/@wf/{1}/publish".format(self.portal_url, uid)
        requests.post(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={},
        )
        transaction.commit()
        self.assertEqual(
            u"published", self.wftool.getInfoFor(self.portal.doc1, u"review_state")
        )

    def test_transition_action_succeeds_changes_effective(self):
        uid = self.portal.doc1.UID()
        endpoint_url = "{0}/@wf/{1}/publish".format(self.portal_url, uid)
        self.assertEqual(self.portal.doc1.effective_date, None)
        now = DateTime()
        requests.post(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={},
        )
        transaction.commit()
        self.assertTrue(isinstance(self.portal.doc1.effective_date, DateTime))
        self.assertTrue(self.portal.doc1.effective_date >= now)

    def test_calling_workflow_with_additional_path_segments_results_in_404(self):
        uid = self.portal.doc1.UID()
        endpoint_url = "{0}/@wf/{1}/publish/test".format(self.portal_url, uid)
        response = requests.post(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={},
        )
        transaction.commit()
        self.assertEqual(404, response.status_code)

    def test_transition_including_children(self):
        transaction.commit()
        uid = self.folder.UID()
        endpoint_url = "{0}/@wf/{1}/publish".format(self.portal_url, uid)
        response = requests.post(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"include_children": "true"},
        )
        transaction.commit()
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            u"published", self.wftool.getInfoFor(self.folder, u"review_state")
        )
        self.assertEqual(
            u"published", self.wftool.getInfoFor(self.subfolder, u"review_state")
        )

    def test_transition_with_effective_date(self):
        uid = self.portal.doc1.UID()
        endpoint_url = "{0}/@wf/{1}/publish".format(self.portal_url, uid)
        requests.post(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"effective": "2018-06-24T09:17:02"},
        )
        transaction.commit()
        self.assertEqual(
            "2018-06-24T09:17:00+00:00", self.portal.doc1.effective().ISO8601()
        )

    def test_transition_with_expiration_date(self):
        uid = self.portal.doc1.UID()
        endpoint_url = "{0}/@wf/{1}/publish".format(self.portal_url, uid)
        requests.post(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"expires": "2019-06-20T18:00:00",
                  "comment": "A comment"},
        )
        transaction.commit()
        self.assertEqual(
            "A comment", self.wftool.getInfoFor(self.portal.doc1, u"comments")
        )
        self.assertEqual(
            "2019-06-20T18:00:00+00:00", self.portal.doc1.expires().ISO8601()
        )

    def test_transition_with_no_access_to_review_history_in_target_state(self):
        self.wftool.setChainForPortalTypes(["Folder"], "restriction_workflow")
        folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder_test", title="Test")
        ]
        transaction.commit()
        uid = folder.UID()
        setRoles(
            self.portal, TEST_USER_ID, ["Contributor", "Editor", "Member", "Reviewer"]
        )
        login(self.portal, TEST_USER_NAME)
        endpoint_url = "{0}/@wf/{1}/restrict".format(self.portal_url, uid)
        response = requests.post(
            endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={},
        )
        transaction.commit()
        self.assertEqual(200, response.status_code)
        self.assertEqual(u"restricted", self.wftool.getInfoFor(folder, u"review_state"))
