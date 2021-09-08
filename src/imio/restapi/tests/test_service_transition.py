# -*- coding: utf-8 -*-
from base64 import b64encode
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
from zExceptions import NotFound
from zope.event import notify
from ZPublisher.pubevents import PubStart


class TestWorkflowTransition(TestCase):

    layer = IMIO_RESTAPI_WORKFLOWS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.wftool = getToolByName(self.portal, "portal_workflow")
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory("Document", id="doc1")

    def traverse(
        self, path="/plone", accept="application/json", method="POST", auth=None
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

    def test_transition_action_succeeds(self):
        uid = self.portal.doc1.UID()
        service = self.traverse("/plone/@wf/{0}/publish".format(uid))
        service.reply()
        self.assertEqual(
            u"published", self.wftool.getInfoFor(self.portal.doc1, u"review_state")
        )

    def test_transition_action_succeeds_changes_effective(self):
        doc1 = self.portal.doc1
        uid = doc1.UID()
        self.assertEqual(doc1.effective_date, None)
        now = DateTime()
        service = self.traverse("/plone/@wf/{0}/publish".format(uid))
        service.reply()
        self.assertTrue(isinstance(doc1.effective_date, DateTime))
        self.assertTrue(doc1.effective_date >= now)

    def test_calling_workflow_with_additional_path_segments_results_in_404(self):
        uid = self.portal.doc1.UID()
        with self.assertRaises(NotFound):
            self.traverse("/plone/doc1/@wf/{0}/publish/test".format(uid))

    def test_transition_including_children(self):
        folder = self.portal[self.portal.invokeFactory("Folder", id="folder")]
        subfolder = folder[folder.invokeFactory("Folder", id="subfolder")]
        uid = folder.UID()
        self.request["BODY"] = '{"include_children": true}'
        service = self.traverse("/plone/@wf/{0}/publish".format(uid))
        service.reply()
        self.assertEqual(200, self.request.response.getStatus())
        self.assertEqual(u"published", self.wftool.getInfoFor(folder, u"review_state"))
        self.assertEqual(
            u"published", self.wftool.getInfoFor(subfolder, u"review_state")
        )

    def test_transition_with_effective_date(self):
        self.request["BODY"] = '{"effective": "2018-06-24T09:17:02"}'
        uid = self.portal.doc1.UID()
        service = self.traverse("/plone/@wf/{0}/publish".format(uid))
        service.reply()
        self.assertEqual(
            "2018-06-24T09:17:00+00:00", self.portal.doc1.effective().ISO8601()
        )

    def test_transition_with_expiration_date(self):
        self.request["BODY"] = '{"expires": "2019-06-20T18:00:00"}'
        uid = self.portal.doc1.UID()
        service = self.traverse("/plone/@wf/{0}/publish".format(uid))
        service.reply()
        self.assertEqual(
            "2019-06-20T18:00:00+00:00", self.portal.doc1.expires().ISO8601()
        )

    def test_transition_with_no_access_to_review_history_in_target_state(self):
        self.wftool.setChainForPortalTypes(["Folder"], "restriction_workflow")
        folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder", title="Test")
        ]
        uid = folder.UID()
        setRoles(
            self.portal, TEST_USER_ID, ["Contributor", "Editor", "Member", "Reviewer"]
        )
        login(self.portal, TEST_USER_NAME)

        auth = "%s:%s" % (TEST_USER_NAME, TEST_USER_PASSWORD)
        service = self.traverse("/plone/@wf/{0}/restrict".format(uid), auth=auth)
        service.reply()
        self.assertEqual(200, self.request.response.getStatus())
        self.assertEqual(u"restricted", self.wftool.getInfoFor(folder, u"review_state"))
