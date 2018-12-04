# -*- coding: utf-8 -*-

from imio.restapi.testing import IMIO_RESTAPI_FUNCTIONAL_TESTING
from OFS.interfaces import IObjectWillBeAddedEvent
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi import HAS_AT
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import getGlobalSiteManager
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import requests
import transaction
import unittest


class TestFolderCreate(unittest.TestCase):
    layer = IMIO_RESTAPI_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

    def test_folder_post_1_level(self):
        response = requests.post(
            self.portal_url,
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                '@type': 'Folder',
                'id': 'myfolder',
                'title': 'My Folder',
                '__children__': [
                    {
                        '@type': 'Document',
                        'id': 'mydocument',
                        'title': 'My Document',
                    }
                ]
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        # first level
        self.assertIsNotNone(self.portal.get('myfolder'))
        self.assertEqual('My Folder', self.portal.myfolder.Title())
        self.assertEqual('Folder', response.json().get('@type'))
        self.assertEqual('myfolder', response.json().get('id'))
        self.assertEqual('My Folder', response.json().get('title'))
        expected_url = self.portal_url + u'/myfolder'
        self.assertEqual(expected_url, response.json().get('@id'))

        # second level
        children_obj = self.portal.myfolder.get('mydocument')
        self.assertIsNotNone(children_obj)
        children_json = response.json()['__children__'][0]
        self.assertEqual('My Document', children_obj.Title())
        self.assertEqual('Document', children_json.get('@type'))
        self.assertEqual('mydocument', children_json.get('id'))
        self.assertEqual('My Document', children_json.get('title'))
        expected_url = self.portal_url + u'/myfolder/mydocument'
        self.assertEqual(expected_url, children_json.get('@id'))

    def test_folder_post_2_level(self):
        response = requests.post(
            self.portal_url,
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                '@type': 'Folder',
                'id': 'myfolder',
                'title': 'My Folder',
                '__children__': [
                    {
                        '@type': 'Folder',
                        'id': 'myfolder',
                        'title': 'My Folder',
                        '__children__': [
                            {
                                '@type': 'Document',
                                'id': 'mydocument',
                                'title': 'My Document',
                            }
                        ],
                    }
                ]
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        # first level
        self.assertIsNotNone(self.portal.get('myfolder'))
        self.assertEqual('My Folder', self.portal.myfolder.Title())
        self.assertEqual('Folder', response.json().get('@type'))
        self.assertEqual('myfolder', response.json().get('id'))
        self.assertEqual('My Folder', response.json().get('title'))
        expected_url = self.portal_url + u'/myfolder'
        self.assertEqual(expected_url, response.json().get('@id'))

        # second level
        children_obj = self.portal.myfolder.get('myfolder')
        self.assertIsNotNone(children_obj)
        children_json = response.json()['__children__'][0]
        self.assertEqual('My Folder', children_obj.Title())
        self.assertEqual('Folder', children_json.get('@type'))
        self.assertEqual('myfolder', children_json.get('id'))
        self.assertEqual('My Folder', children_json.get('title'))
        expected_url = self.portal_url + u'/myfolder/myfolder'
        self.assertEqual(expected_url, children_json.get('@id'))

        # third level
        children_obj = self.portal.myfolder.myfolder.get('mydocument')
        self.assertIsNotNone(children_obj)
        children_json = response.json()['__children__'][0]['__children__'][0]
        self.assertEqual('My Document', children_obj.Title())
        self.assertEqual('Document', children_json.get('@type'))
        self.assertEqual('mydocument', children_json.get('id'))
        self.assertEqual('My Document', children_json.get('title'))
        expected_url = self.portal_url + u'/myfolder/myfolder/mydocument'
        self.assertEqual(expected_url, children_json.get('@id'))
