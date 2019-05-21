# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from plone.restapi.services import Service
from zExceptions import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class RequestSchemaGet(Service):
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RequestSchemaGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    @property
    def _request_name(self):
        if len(self.params) != 1:
            raise Exception(
                'Must supply exactly one parameter (dotted name of'
                'the record to be retrieved)'
            )

        return self.params[0]

    def check_security(self):
        # Only expose type information to authenticated users
        portal_membership = getToolByName(self.context, 'portal_membership')
        if portal_membership.isAnonymousUser():
            raise Unauthorized

    def reply(self):
        self.check_security()

        self.content_type = 'application/json+schema'
        try:
            return {
                "title": "Submit a custom request",
                "fieldsets": [
                    {
                        "fields": [
                            "title",
                            "description",
                            "text",
                        ],
                        "id": "default",
                        "title": "Default",
                    },
                    {
                        "fields": [
                            "subjects",
                            "allow_discussion",
                        ],
                        "id": "settings",
                        "title": "Settings",
                    },
                ],
                "properties": {
                    "description": {
                        "description": "Used in item listings and search results.",
                        "minLength": 0,
                        "title": "Summary",
                        "type": "string",
                        "widget": "textarea",
                    },
                    "text": {
                        "description": "",
                        "title": "Text",
                        "type": "string",
                        "widget": "richtext",
                    },
                    "title": {
                        "description": "",
                        "title": "Title",
                        "type": "string",
                    },
                    "subjects": {
                        "choices": [],
                        "description": "Tags are commonly used for ad-hoc organization of content.",
                        "enum": [],
                        "enumNames": [],
                        "title": "Tags",
                        "type": "string",
                        "widget": "select2",
                        "vocabulary": "@vocabularies/plone.app.vocabularies.Keywords"
                    },
                    "allow_discussion": {
                        "choices": [
                            [
                                "True",
                                "Yes",
                            ],
                            [
                                "False",
                                "No",
                            ]
                        ],
                        "description": "Allow discussion for this content object.",
                        "enum": [
                            "True",
                            "False",
                        ],
                        "enumNames": [
                            "Yes",
                            "No",
                        ],
                        "title": "Allow discussion",
                        "type": "string",
                        "widget": "radio",
                    },
                },
                "required": [
                    "title",
                ],
            }
        except KeyError:
            self.content_type = 'application/json'
            self.request.response.setStatus(404)
            return {
                'type': 'NotFound',
                'message': 'Type "{}" could not be found.'.format(
                    self._request_name,
                )
            }
