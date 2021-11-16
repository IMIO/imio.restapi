# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from imio.restapi.utils import sizeof_fmt
from plone import api
from plone.restapi.deserializer import boolean_value
from plone.restapi.services import Service

import json
import os


STATS_UNAUTHORIZED = 'User must be Manager to use the "stats" option!'


class InfosGet(Service):
    """Returns informations about installed versions.
       Methods that should be overrided :
       - _stats_types_queries: catalog queries to compute number of elements of given type;
       - _packages_names: package to display version for;
       - _extra_result: method to return extra arbitrary data.
       """

    def _stats_types_queries(self):
        """To be overrided !!!
           Returned format :
           {'MeetingConfig': {'portal_type': 'MeetingConfig'},
            'annex': {'portal_type': 'annex'}, }
        """
        queries = {}
        return queries

    def _packages_names(self):
        """To be overrided !!!
           Returns list of package names."""
        return ["imio.restapi"]

    def _extra_result(self):
        """To be overrided !!!
           Returns arbitrary extra result."""
        return {}

    def _stats_users(self):
        portal_membership = api.portal.get_tool("portal_membership")
        users = portal_membership.searchForMembers()
        count = 0
        for user in users:
            user_groups = user.getGroups()
            if user_groups and user_groups != ["AuthenticatedUsers"]:
                count = count + 1
        return count

    def _stats_groups(self):
        return len(api.group.get_groups())

    def _stats_types(self):
        types = {}
        catalog = api.portal.get_tool("portal_catalog")
        for name, query in self._stats_types_queries().items():
            types[name] = len(catalog(**query))
        return types

    def _stats_database(self):
        # soft dependency
        from imio.pyutils.system import error
        from Products.CPUtils.Extensions.utils import tobytes

        # zope
        database = {"fs_sz": 0, "bl_sz": 0}
        app = self.context.restrictedTraverse("/")
        dbs = app["Control_Panel"]["Database"]
        for db in dbs.getDatabaseNames():
            readable_size = dbs[db].db_size()
            size = int(tobytes(readable_size[:-1] + " " + readable_size[-1:] + "B"))
            # keep only largest
            if size > database["fs_sz"]:
                database["fs_sz"] = size
                database["fs_sz_readable"] = sizeof_fmt(size)
        # blobstorage
        instdir = os.getenv("PWD")
        if instdir is None:
            # try with INSTANCE_HOME, it is like
            # /srv/instances/instance_name/parts/instance1
            instdir = os.getenv("INSTANCE_HOME").split("/parts/")[0]
        if os.path.exists(instdir):
            # .sizes.json
            sizefile = os.path.join(instdir, '.sizes.json')
            try:
                fh = open(sizefile)
                res = json.load(fh)
                fh.close()
                size = int(res.get(u'local_size', 0))
                if size > database['fs_sz']:
                    size -= database['fs_sz']
                    database['bl_sz'] = size
                    database["bl_sz_readable"] = sizeof_fmt(size)
            except Exception, msg:
                error(u".sizes.json not valid in '{}': '{}'".format(instdir, msg))
        return database

    def _stats(self):
        """ """
        include_stats = self.request.form.get("include_stats", False)
        stats = {}
        if boolean_value(include_stats):
            user = api.user.get_current()
            if not user.has_role("Manager"):
                raise Unauthorized(STATS_UNAUTHORIZED)

            # all this was gently borrowed from imio.updates inst_infos.py
            stats["users"] = self._stats_users()
            stats["groups"] = self._stats_groups()
            stats["types"] = self._stats_types()
            stats["database"] = self._stats_database()
        return stats

    def _packages(self):
        """ """
        packages = {}
        for package_name in self._packages_names():
            version = api.env.get_distribution(package_name)._version
            packages[package_name] = version
        return packages

    def reply(self):
        result = {}
        result["connected_user"] = api.user.get_current().getId()
        result["packages"] = self._packages()
        result["stats"] = self._stats()
        result.update(self._extra_result())
        return result
