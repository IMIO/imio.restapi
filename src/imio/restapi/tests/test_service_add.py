# -*- coding: utf-8 -*-

from imio.restapi.services.add import FILE_DATA_INCOMPLETE_ERROR
from imio.restapi.testing import IMIO_RESTAPI_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

import base64
import requests
import transaction
import unittest


class TestFolderCreate(unittest.TestCase):
    layer = IMIO_RESTAPI_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

    def test_folder_post_1_level(self):
        response = requests.post(
            self.portal_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Folder",
                "id": "myfolder",
                "title": "My Folder",
                "__children__": [
                    {"@type": "Document", "id": "mydocument", "title": "My Document"}
                ],
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        # first level
        self.assertIsNotNone(self.portal.get("myfolder"))
        self.assertEqual("My Folder", self.portal.myfolder.Title())
        self.assertEqual("Folder", response.json().get("@type"))
        self.assertEqual("myfolder", response.json().get("id"))
        self.assertEqual("My Folder", response.json().get("title"))
        expected_url = self.portal_url + u"/myfolder"
        self.assertEqual(expected_url, response.json().get("@id"))

        # second level
        children_obj = self.portal.myfolder.get("mydocument")
        self.assertIsNotNone(children_obj)
        children_json = response.json()["__children__"][0]
        self.assertEqual("My Document", children_obj.Title())
        self.assertEqual("Document", children_json.get("@type"))
        self.assertEqual("mydocument", children_json.get("id"))
        self.assertEqual("My Document", children_json.get("title"))
        expected_url = self.portal_url + u"/myfolder/mydocument"
        self.assertEqual(expected_url, children_json.get("@id"))

    def test_folder_post_2_level(self):
        response = requests.post(
            self.portal_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Folder",
                "id": "myfolder",
                "title": "My Folder",
                "__children__": [
                    {
                        "@type": "Folder",
                        "id": "myfolder",
                        "title": "My Folder",
                        "__children__": [
                            {
                                "@type": "Document",
                                "id": "mydocument",
                                "title": "My Document",
                            }
                        ],
                    }
                ],
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        # first level
        self.assertIsNotNone(self.portal.get("myfolder"))
        self.assertEqual("My Folder", self.portal.myfolder.Title())
        self.assertEqual("Folder", response.json().get("@type"))
        self.assertEqual("myfolder", response.json().get("id"))
        self.assertEqual("My Folder", response.json().get("title"))
        expected_url = self.portal_url + u"/myfolder"
        self.assertEqual(expected_url, response.json().get("@id"))

        # second level
        children_obj = self.portal.myfolder.get("myfolder")
        self.assertIsNotNone(children_obj)
        children_json = response.json()["__children__"][0]
        self.assertEqual("My Folder", children_obj.Title())
        self.assertEqual("Folder", children_json.get("@type"))
        self.assertEqual("myfolder", children_json.get("id"))
        self.assertEqual("My Folder", children_json.get("title"))
        expected_url = self.portal_url + u"/myfolder/myfolder"
        self.assertEqual(expected_url, children_json.get("@id"))

        # third level
        children_obj = self.portal.myfolder.myfolder.get("mydocument")
        self.assertIsNotNone(children_obj)
        children_json = response.json()["__children__"][0]["__children__"][0]
        self.assertEqual("My Document", children_obj.Title())
        self.assertEqual("Document", children_json.get("@type"))
        self.assertEqual("mydocument", children_json.get("id"))
        self.assertEqual("My Document", children_json.get("title"))
        expected_url = self.portal_url + u"/myfolder/myfolder/mydocument"
        self.assertEqual(expected_url, children_json.get("@id"))

    def test_folder_post_file(self):
        # must define "filename" or "content-type" while adding file
        # to find correct contentType on created file
        response = requests.post(
            self.portal_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "File",
                "id": "myfile",
                "title": "My File",
                "file": {"data": "123456", "encoding": "ascii",},
            },
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.json()[u"message"], FILE_DATA_INCOMPLETE_ERROR)

        # add file correctly
        response = requests.post(
            self.portal_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "File",
                "id": "myfile",
                "title": "My File",
                "file": {"data": "123456", "encoding": "ascii", "filename": "file.txt"},
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        myfile = self.portal.myfile
        self.assertEqual(myfile.Title(), "My File")
        file = myfile.getFile()
        self.assertEqual(file.filename, "file.txt")
        self.assertEqual(file.content_type, "text/plain")
        # due to a bug in plone.restapi while creating file with another
        # encoding than base64, we coment this under, so for AT,
        # do not define an encoding or use base64, DX is correct in both cases...
        # self.assertEqual(file.size(), 6)
        # self.assertEqual(file.data, '123456')

        # if "encoding" not given, considered as "base64"
        response = requests.post(
            self.portal_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "File",
                "id": "myfile2",
                "title": "My File 2",
                "file": {"data": base64.b64encode("654321"), "filename": "file.txt"},
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        myfile2 = self.portal.myfile2
        self.assertEqual(myfile2.Title(), "My File 2")
        file2 = myfile2.getFile()
        self.assertEqual(file2.filename, "file.txt")
        self.assertEqual(file2.content_type, "text/plain")
        self.assertEqual(file2.size(), 6)
        self.assertEqual(file2.data, "654321")

    def test_folder_post_wf_transitions(self):
        response = requests.post(
            self.portal_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Folder",
                "id": "myfolder",
                "title": "My Folder",
                "wf_transitions": ["unknown1"],
                "__children__": [
                    {
                        "@type": "Document",
                        "id": "mydocument",
                        "title": "My Document",
                        "wf_transitions": ["unknown2", "publish"],
                    }
                ],
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        # unknown transitions are ignored
        json = response.json()
        self.assertEqual(json["review_state"], "private")
        self.assertEqual(json["__children__"][0]["review_state"], "published")
        # review_state correctly reindexed
        brains = self.portal.portal_catalog(review_state="published")
        doc = brains[0].getObject()
        self.assertEqual(doc.UID(), json["__children__"][0]["UID"])
