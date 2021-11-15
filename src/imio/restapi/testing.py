# -*- coding: utf-8 -*-

from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_WORKFLOWS_INTEGRATION_TESTING
from plone.testing import z2
from zope.globalrequest import setLocal

import collective.documentgenerator
import imio.restapi
import plone.app.dexterity


class ImioRestapiLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=imio.restapi)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "imio.restapi:default")


class ImioRestapiDocGenLayer(PloneSandboxLayer):
    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=imio.restapi)
        self.loadZCML(package=collective.documentgenerator)

    def setUpPloneSite(self, portal):
        # necessary for collective.fingerpointing used
        # when installing "collective.documentgenerator:demo"
        setLocal('request', portal.REQUEST)

        applyProfile(portal, "imio.restapi:default")
        applyProfile(portal, "collective.documentgenerator:demo")


IMIO_RESTAPI_FIXTURE = ImioRestapiLayer()

IMIO_RESTAPI_DOCGEN_FIXTURE = ImioRestapiDocGenLayer()

IMIO_RESTAPI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_RESTAPI_FIXTURE,), name="ImioRestapiLayer:IntegrationTesting"
)


IMIO_RESTAPI_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_RESTAPI_FIXTURE, PLONE_RESTAPI_AT_FUNCTIONAL_TESTING),
    name="ImioRestapiLayer:FunctionalTesting",
)

IMIO_RESTAPI_DOCGEN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_RESTAPI_DOCGEN_FIXTURE, PLONE_RESTAPI_AT_FUNCTIONAL_TESTING),
    name="ImioRestapiWithDocGenLayer:FunctionalTesting",
)

IMIO_RESTAPI_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(IMIO_RESTAPI_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="ImioRestapiLayer:AcceptanceTesting",
)

IMIO_RESTAPI_WORKFLOWS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_RESTAPI_FIXTURE, PLONE_RESTAPI_WORKFLOWS_INTEGRATION_TESTING, z2.ZSERVER_FIXTURE),
    name="ImioRestapiLayer:IntegrationWorkflowTesting"
)

IMIO_RESTAPI_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_RESTAPI_FIXTURE, PLONE_RESTAPI_DX_FUNCTIONAL_TESTING),
    name="ImioRestapiLayer:FunctionalDXTesting",
)
