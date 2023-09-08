# -*- coding: utf-8 -*-

from imio.restapi.interfaces import IContentImporter
from imio.restapi.interfaces import IRestAuthentication
from imio.restapi.interfaces import IRESTLink
from plone import api
from plone.restapi.deserializer import boolean_value
from plone.restapi.services.content import add
from zope.component import getMultiAdapter
from zope.component import queryAdapter

import json
import os
import requests
import time


def get_ws_url():
    """ Return the webservice url defined in instance config """
    return os.getenv("WS_URL")


def get_client_id():
    """ Return the client_id defined in instance config """
    return os.getenv("CLIENT_ID")


def get_application_id():
    """ Return the application_id defined in instance config """
    return os.getenv("APPLICATION_ID")


def get_application_url():
    """ Return the application_url defined in instance config """
    return os.getenv("APPLICATION_URL")


def get_return_fullobject_after_creation_default():
    """ Return the return_fullobject_after_creation_default defined in instance config """
    return boolean_value(os.getenv("RETURN_FULLOBJECT_AFTER_CREATION_DEFAULT", True))


def is_debug_mode_enabled():
    """ Return the debug_mode defined in instance config """
    return boolean_value(os.getenv("RESTAPI_DEBUG", False)) or \
        api.portal.get_registry_record(
        'imio.restapi.settings.interfaces.ISettings.debug_mode'
    )


def get_authentication(request):
    auth = queryAdapter(request, IRestAuthentication)
    if auth:
        return auth.basic


def generate_request_parameters(
    path, client_id, application_id, method="POST", r_method="POST"
):
    args = (method, "{0}/request".format(get_ws_url()))
    kwargs = {
        "headers": {"Accept": "application/json", "Content-Type": "application/json"},
        "json": {
            "request_type": r_method,
            "client_id": client_id,
            "application_id": application_id,
            "path": path,
            "parameters": {},
        },
    }
    return args, kwargs


def ws_asynchronous_request(method, *args, **kwargs):
    me = {"GET": requests.get, "POST": requests.post}.get(method)
    r = me(*args, **kwargs)
    if r.status_code == 200:
        return r.json()


def ws_synchronous_request(method, *args, **kwargs):
    me = {"GET": requests.get, "POST": requests.post}.get(method)
    r = me(*args, **kwargs)
    if r.status_code == 200:
        kwargs["json"] = r.json()
        result = False
        counter = 0
        while result is False:
            r = requests.get(*args, **kwargs)
            if r.status_code == 200:
                result = True
            else:
                if counter >= 500:
                    return r
                counter += 1
                time.sleep(0.01)
        return r


def import_content(
    context, request, client_id, application_id, path, link=True, back_link=False
):
    """ Import the content from the given application on the current context """
    r_args, r_kwargs = generate_request_parameters(
        path, client_id, application_id, method="POST", r_method="GET"
    )
    auth = get_authentication(request)
    if auth:
        r_kwargs["json"]["auth"] = auth
    result = ws_synchronous_request(*r_args, **r_kwargs)
    json_result = result.json()
    importer = getMultiAdapter((json_result["response"], context), IContentImporter)
    request.set("BODY", json.dumps(importer.parse_data()))
    folder_post = add.FolderPost()
    folder_post.context = context
    folder_post.request = request
    reply = folder_post.reply()
    created_element = context.get(reply["id"])
    link = getMultiAdapter((json_result, context), IRESTLink)
    link.back_link = True
    link.add_on(created_element)


def sizeof_fmt(num, suffix="o"):
    """Readable file size
    :param num: Bytes value
    :type num: int
    :param suffix: Unit suffix (optionnal) default = o
    :type suffix: str
    :rtype: str
    """
    for unit in ["", "k", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def serialize_term(tokens, vocab):
    """Given a term p_values and a p_vocab, generate a serialized version
       with {'token': p_token[0], 'value': term_value}.
       This is useful when it is not a real field and we can not use a FieldSerializer."""
    res = []
    only_one = False
    if isinstance(tokens, basestring):
        only_one = True
        tokens = [tokens]
    for token in tokens:
        res.append({'token': token, 'title': vocab.getTerm(token).title})
    # if we receive one token, we return a dict, if we receive a list of tokens
    # even if only one token in the list, we return a list of dicts
    if res and only_one:
        res = res[0]
    return res
