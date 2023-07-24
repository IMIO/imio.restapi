# -*- coding: utf-8 -*-
"""Init and utils."""

from imio.helpers.security import fplog
from imio.restapi.utils import is_debug_mode_enabled
from plone.restapi.deserializer import boolean_value
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.i18nmessageid import MessageFactory

import json
import logging


_ = MessageFactory("imio.restapi")
logger = logging.getLogger("imio.restapi")


# plonemeeting.restapi, need to monkeypatch here because order of packages
# monkey patching in plonemeeting.restapi does not seem to work...

Service.__old_pm_render = Service.render


def render(self):
    """Monkeypatched to add fplog."""
    query_string = self.request.get('QUERY_STRING', '')
    extras = 'name={0} url={1}{2}'.format(
        self.__name__,
        self.request.get('ACTUAL_URL'),
        query_string and " query_string={0}".format(query_string) or '')
    fplog("restapi_call", extras=extras)

    # debug may be enabled by passing debug=true as parameter to the restapi call
    # or when setting the RESTAPI_DEBUG environment variable
    # or when imio.restapi.debug_mode is True
    # with POST, URL parameters are not in self.request.form
    debug = boolean_value(self.request.form.get('debug', False)) or \
        "debug=true" in query_string or \
        is_debug_mode_enabled()

    # log the input when debug is enabled
    if debug:
        # with POST, data is in the body
        if self.request.get('method', 'GET') != 'GET':
            data = json_body(self.request)
            fplog("restapi_call_debug",
                  extras="INPUT: \n" + json.dumps(data, indent=4, sort_keys=True))
    res = self.__old_pm_render()
    # log the output when debug is enabled
    if debug:
        fplog("restapi_call_debug", extras="OUTPUT: \n" + res)
    return res


Service.render = render
logger.info("Monkey patching plone.restapi.services.RestService (render)")
