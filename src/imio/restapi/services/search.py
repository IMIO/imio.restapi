# -*- coding: utf-8 -*-

from imio.helpers.content import uuidsToObjects
from imio.restapi.utils import listify
from plone.app.querystring.queryparser import parseFormquery
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict
from plone.restapi.services.search.get import SearchGet as BaseSearchGet


class SearchGet(BaseSearchGet):
    """Base SearchGet, handles :
       - using a base_search_uid (Collection UID) as base query;
       - adding additional parameters to query;
       - formalize metadata_fields."""

    @property
    def _additional_fields(self):
        """By default add 'UID' to returned data."""
        return ["UID"]

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
            collection = uuidsToObjects(uuids=base_search_uid)
            if collection:
                collection = collection[0]
                query = parseFormquery(collection, collection.query)
        return query

    def _set_query_additional_params(self):
        """ """
        query = {}
        return query

    def _clean_query(self, query):
        """Remove parameters that are not indexes names to avoid warnings like :
           WARNING plone.restapi.search.query No such index: 'my_custom_parameter'"""
        query.pop("my_custom_parameter", None)

    def _set_metadata_fields(self):
        """Must be set in request.form."""
        form = self.request.form
        # manage metadata_fields
        additional_metadata_fields = listify(form.get("metadata_fields", []))
        additional_metadata_fields += self._additional_fields
        form["metadata_fields"] = additional_metadata_fields

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

        self._set_metadata_fields()

        return SearchHandler(self.context, self.request).search(query)

    def reply(self):
        return self._process_reply()
