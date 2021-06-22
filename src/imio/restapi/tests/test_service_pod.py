# -*- coding: utf-8 -*-

from imio.restapi.testing import IMIO_RESTAPI_DOCGEN_FUNCTIONAL_TESTING
from plone import api
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

import re
import requests
import transaction
import unittest


class TestServicePodTemplatesGet(unittest.TestCase):
    layer = IMIO_RESTAPI_DOCGEN_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        api.user.grant_roles(TEST_USER_ID, roles=["Manager"])
        login(self.portal, TEST_USER_NAME)

    def _create_doc(self):
        """ """
        self.doc = api.content.create(
            container=self.portal, type="Document", id="doc", title="Doc"
        )
        self.doc_url = self.doc.absolute_url()
        self.endpoint_url = "{0}/@pod-templates".format(self.doc_url)
        transaction.commit()

    def test_pod_endpoint_generate_url(self):
        self._create_doc()
        response = requests.get(
            self.endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={},
        )
        # 3 POD templates available for doc
        pod_templates = response.json()
        self.assertEqual(
            [pt["id"] for pt in pod_templates],
            [
                u"test_template",
                u"test_template_multiple",
                u"test_template_reuse",
            ],
        )
        # test_template
        self.assertTrue(u"generate_url_odt" in pod_templates[0])
        # test_template_multiple
        self.assertTrue(u"generate_url_odt" in pod_templates[1])
        self.assertTrue(u"generate_url_pdf" in pod_templates[1])
        self.assertTrue(u"generate_url_doc" in pod_templates[1])
        self.assertTrue(u"generate_url_docx" in pod_templates[1])
        # test_template_reuse
        self.assertTrue(u"generate_url_odt" in pod_templates[2])
        self.assertTrue(u"generate_url_pdf" in pod_templates[2])
        self.assertTrue(u"generate_url_doc" in pod_templates[2])
        self.assertTrue(u"generate_url_docx" in pod_templates[2])

    def test_pod_endpoint_get_generated_pod(self):
        self._create_doc()
        # get pod templates
        response = requests.get(
            self.endpoint_url,
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={},
        )
        pod_templates = response.json()
        # generate an ODT pod template
        generate_url_odt = pod_templates[0]["generate_url_odt"]
        response = requests.get(
            generate_url_odt,
            headers={"Accept": "application/octet-stream"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={},
        )
        self.assertEqual(
            response.headers["content-disposition"],
            'inline;filename="General template Doc.odt"',
        )
        filename = re.findall("filename=(.+)", response.headers["content-disposition"])[
            0
        ].replace('"', "")
        self.assertEqual(filename, "General template Doc.odt")

    def test_pod_expandable(self):
        self._create_doc()
        # get informations for doc
        response = requests.get(
            self.doc.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={},
        )
        json = response.json()
        self.assertTrue("pod-templates" in json["@components"])
        self.assertEqual(json["@components"]["pod-templates"]["@id"], self.endpoint_url)
