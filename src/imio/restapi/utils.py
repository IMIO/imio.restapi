# -*- coding: utf-8 -*-

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


def ws_synchronous_request(method, *args, **kwargs):
    me = {"GET": requests.get, "POST": requests.post}.get(method)
    r = me(*args, **kwargs)
    if r.status_code == 200:
        kwargs["json"] = r.json()
        result = False
        counter = 0
        while result is False:
            r = requests.get(*args, **kwargs)
            print("request {0}".format(counter))
            if r.status_code == 200:
                result = True
            else:
                if counter >= 500:
                    return r
                counter += 1
                time.sleep(0.01)
        return r


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
