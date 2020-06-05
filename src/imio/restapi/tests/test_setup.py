# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from imio.restapi.testing import IMIO_RESTAPI_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class TestSetup(unittest.TestCase):
    """Test that imio.restapi is properly installed."""

    layer = IMIO_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if imio.restapi is installed."""
        self.assertTrue(self.installer.isProductInstalled("imio.restapi"))

    def test_browserlayer(self):
        """Test that IImioRestapiLayer is registered."""
        from imio.restapi.interfaces import IImioRestapiLayer
        from plone.browserlayer import utils

        self.assertIn(IImioRestapiLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = IMIO_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstallProducts(["imio.restapi"])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if imio.restapi is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled("imio.restapi"))

    def test_browserlayer_removed(self):
        """Test that IImioRestapiLayer is removed."""
        from imio.restapi.interfaces import IImioRestapiLayer
        from plone.browserlayer import utils

        self.assertNotIn(IImioRestapiLayer, utils.registered_layers())
