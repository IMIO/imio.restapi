# -*- coding: utf-8 -*-

from imio.helpers.content import uuidsToObjects
from plone.app.contenttypes.interfaces import ICollection
from plone.app.querystring.queryparser import parseFormquery
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services.search.get import SearchGet as BaseSearchGet


class SearchGet(BaseSearchGet):
    """Base SearchGet, handles :
       - using a base_search_uid (Collection UID) as base query;
       - adding additional parameters to query."""

    def _set_query_before_hook(self):
        """Manipulate query before hook."""
        query = {}
        return query

    def _set_query_after_hook(self):
        """Manipulate after before hook."""
        query = {}
        return query

    def _set_query_base_search(self):
        """ """
        query = {}
        form = self.request.form
        base_search_uid = form.get("base_search_uid", "").strip()
        if base_search_uid:
            element = uuidsToObjects(uuids=base_search_uid)
            if element and ICollection.providedBy(element[0]):
                collection = element[0]
                query = parseFormquery(collection, collection.query)
            elif element:
                self.context = element[0]
        return query

    def _set_query_additional_params(self):
        """ """
        query = {}
        return query

    def _clean_query(self, query):
        """Remove parameters that are not indexes names to avoid warnings like :
           WARNING plone.restapi.search.query No such index: 'my_custom_parameter'"""
        query.pop("base_search_uid", None)

    def _process_reply(self):
        """Easier to override if necessary to call various ways from reply method."""
        query = {}

        query.update(self._set_query_before_hook())
        query.update(self._set_query_base_search())
        query.update(self._set_query_additional_params())
        query.update(self.request.form.copy())
        query.update(self._set_query_after_hook())
        self._clean_query(query)
        query = unflatten_dotted_dict(query)

        return SearchHandler(self.context, self.request).search(query)

    def reply(self):
        return self._process_reply()
