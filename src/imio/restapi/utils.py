# -*- coding: utf-8 -*-

import requests
import time
import os


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


def generate_request_parameters(
    path, client_id, application_id, method="POST", r_method="POST"
):
    args = (method, "{0}/request".format(get_ws_url()))
    kwargs = {
        "headers": {"Accept": "application/json", "Content-Type": "application/json"},
        "auth": ("admin", "admin"),  # XXX Implement authentication
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
        while result == False:
            r = requests.get(*args, **kwargs)
            print("request {0}".format(counter))
            if r.status_code == 200:
                result = True
            else:
                if counter >= 500:
                    __import__("pdb").set_trace()
                    return r
                counter += 1
                time.sleep(0.01)
        return r
