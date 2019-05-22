# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from plone.restapi.services import Service
from zExceptions import Unauthorized
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import Interface
from zope.component import queryMultiAdapter


class IRequestSchema(Interface):
    """ """


@implementer(IRequestSchema)
class RequestSchemaAdapter(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_schema(self):
        """ Return the json associated schema """
        raise NotImplementedError


class RequestSchemaTestAdapter(RequestSchemaAdapter):
    def get_schema(self):
        return {
            "title": "Submit a custom request",
            "fieldsets": [
                {
                    "fields": ["title", "description", "text"],
                    "id": "default",
                    "title": "Default",
                },
                {
                    "fields": ["subjects", "allow_discussion"],
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
                "title": {"description": "", "title": "Title", "type": "string"},
                "subjects": {
                    "choices": [],
                    "description": "Tags are commonly used for ad-hoc organization of content.",
                    "enum": [],
                    "enumNames": [],
                    "title": "Tags",
                    "type": "string",
                    "widget": "select2",
                    "vocabulary": "@vocabularies/plone.app.vocabularies.Keywords",
                },
                "allow_discussion": {
                    "choices": [["True", "Yes"], ["False", "No"]],
                    "description": "Allow discussion for this content object.",
                    "enum": ["True", "False"],
                    "enumNames": ["Yes", "No"],
                    "title": "Allow discussion",
                    "type": "string",
                    "widget": "radio",
                },
            },
            "required": ["title"],
        }


class RequestSchemaDocumentAdapter(RequestSchemaAdapter):
    def get_schema(self):
        return {
            "fieldsets": [
                {
                    "fields": [
                        "title",
                        "description",
                        "text",
                    ],
                    "id": "default",
                    "title": "Default"
                },
                {
                    "fields": [
                        "exclude_from_nav",
                    ],
                    "id": "settings",
                    "title": "Paramètres"
                },
                {
                    "fields": [
                        "subjects",
                    ],
                    "id": "categorization",
                    "title": "Catégorisation"
                },
                {
                    "fields": [
                        "effective",
                        "expires"
                    ],
                    "id": "dates",
                    "title": "Dates"
                },
            ],
            "properties": {
                "description": {
                    "description": "Utilisé dans les pages listant des éléments et les pages de résultats de recherche.",
                    "minLength": 0,
                    "title": "Description",
                    "type": "string",
                    "widget": "textarea"
                },
                "effective": {
                    "description": "La date à laquelle cet élément sera publié. Si aucune date n'est indiquée, l'élément est visible immédiatement.",
                    "title": "Date de publication",
                    "type": "string",
                    "widget": "datetime"
                },
                "exclude_from_nav": {
                    "default": False,
                    "description": "Si l'option est activée, cet élément n'apparaîtra pas dans la navigation.",
                    "title": "Exclure de la navigation",
                    "type": "boolean",
                    "widget": "singlecheckbox"
                },
                "expires": {
                    "description": "La date à laquelle cet élément arrivera à expiration. À la date indiquée, l'élément sera invisible pour les autres utilisateurs. Si aucune date n'est indiquée, l'élément n'expirera jamais.",
                    "title": "Date d'expiration",
                    "type": "string",
                    "widget": "datetime"
                },
                "subjects": {
                    "description": "Les mots-clés sont utilisés couramment pour organiser le contenu de façon ad hoc.",
                    "items": {
                        "description": "",
                        "title": "",
                        "type": "string"
                    },
                    "title": "Mots-clés",
                    "type": "string",
                    "widget": "select2",
                    "vocabulary": "@vocabularies/plone.app.vocabularies.Keywords",
                },
                "text": {
                    "description": "",
                    "title": "Texte",
                    "type": "string",
                    "widget": "richtext"
                },
                "title": {
                    "description": "",
                    "title": "Titre",
                    "type": "string"
                },
            },
            "required": [
                "title"
            ],
            "title": "Document",
            "type": "object",
            "actions": [
                {
                    "type": "button",
                    "id": "create",
                    "title": u"Créer",
                    "action": {
                        "path": "/",
                        "parameters": {
                            "@type": "Document",
                        }
                    }
                },
            ],
        }


@implementer(IPublishTraverse)
class RequestSchemaGet(Service):
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
                "Must supply exactly one parameter (dotted name of"
                "the record to be retrieved)"
            )

        return self.params[0]

    def check_security(self):
        # Only expose type information to authenticated users
        portal_membership = getToolByName(self.context, "portal_membership")
        if portal_membership.isAnonymousUser():
            raise Unauthorized

    def reply(self):
        self.check_security()

        self.content_type = "application/json+schema"
        adapter = queryMultiAdapter(
            (self.context, self.request), IRequestSchema, name=self._request_name
        )
        if not adapter:
            self.content_type = "application/json"
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": 'Type "{}" could not be found.'.format(self._request_name),
            }
        return adapter.get_schema()
