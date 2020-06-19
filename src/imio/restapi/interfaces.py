# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IImioRestapiLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IRESTAction(Interface):
    """A REST action"""

    id = schema.TextLine(title=u"Action Identifier", required=True, default=u"default")

    title = schema.TextLine(title=u"Action title", required=True)

    application_id = schema.TextLine(
        title=u"Application Identifier",
        description=u"The unique application identifier",
        required=True,
    )

    schema_name = schema.TextLine(
        title=u"Query schema",
        description=u"The query schema for the request",
        required=True,
    )

    view_name = schema.TextLine(
        title=u"Form view", required=True, default=u"default-action-form"
    )


class IRESTLink(Interface):
    """A REST link"""

    path = schema.TextLine(title=u"Path to the object", required=True)

    uid = schema.TextLine(title=u"The object UID", required=True)

    title = schema.TextLine(title=u"The object title", required=True)

    application_id = schema.TextLine(
        title=u"Application Identifier",
        description=u"The unique application identifier",
        required=True,
    )

    back_link = schema.Bool(
        title=u"Back reference",
        description=u"Define if this is a back reference",
        required=True,
        default=False,
    )


class IContentImporter(Interface):
    """ Adapter interface to prepare data to import """


class IRestAuthentication(Interface):
    """ Adapter interface to handle authentification """
