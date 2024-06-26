Changelog
=========


1.0rc3 (unreleased)
-------------------

- Python 3 compatibility.
  [gbastien]

1.0rc2 (2024-05-27)
-------------------

- Do not fail to log restapi call when using DELETE.
  [gbastien]

1.0rc1 (2024-03-14)
-------------------

- Moved unused `utils.listify` to `imio.pyutils.utils.listify`.
  [gbastien]
- When using a `base_search_uid` take also `sort_on/sort_order`
  defined on the Collection.
  [gbastien]

1.0b3 (2023-08-25)
------------------

- Added parameter `debug_mode` to the settings, when enabled, input and output
  requests are displayed into the Zope log.
  [gbastien]

1.0b2 (2023-05-31)
------------------

- Added helper `utils.serialize_term` that will serialize a vocabulary term
  the same way it is done by the `FieldSerializer`.
  [gbastien]

1.0b1 (2022-01-03)
------------------

- In `FolderPost.do_reply` if an error occurs, do not continue,
  stop and return the result with the error immediately.
  [gbastien]

- Added `return_fullobject_after_creation_default`, `True` by default,
  to the `imio.restapi` settings panel. This will do the full serialized object to
  be returned after an object is created (this is already the current behavior).
  When set to False, the summary serialization will be returned.
  [gbastien]

- Fixed `@infos?include_stats=1` blobstorage size computation to use `.size.json`.
  [gbastien]

1.0a15 (2021-11-08)
-------------------

- Override 'update' and 'workflow transition' to use the uid
  [vpiret]


1.0a14 (2021-07-16)
-------------------

- Avoid duplicates in `metadata_fields`.
  [gbastien]

- In `@infos` if `PWD` env variable is not available, try to determinate instance
  path using the `INSTANCE_HOME` env variable.
  [gbastien]

- Require `plone.restapi<8` in `setup.py` as versions 8+ are only for Python3.
  [gbastien]

- Fixed tests due to changes in `collective.documentgenerator` where
  the `ConfigurablePODTemplate` named `test_ods_template` is no more generable
  on type `Document`.
  [gbastien]

- Added possibility to redefine the name of the `metadata_fields` form parameter
  so it may be overrided by a subclass for example.
  [gbastien]


1.0a13 (2021-02-15)
-------------------

- Cleanup `base_search_uid` parameter to avoid warnings in instance logs
  [mpeeters]

- Adapt `@search` service to use the context instead of using `path` index that can be buggy on some circumstances
  [mpeeters]


1.0a12 (2021-02-03)
-------------------

- Improve `@search` by allowing element UID other than Collection for `base_search_uid` parameter that can be used as a base path
  [mpeeters]

- Moved management of additional `metadata_fields` from the `SearchGet` service
  to the `DefaultJSONSummarySerializer` created for that, it will override
  the default `plone.restapi` `DefaultJSONSummarySerializer` and add
  `id` and `UID` by default to the results.
  [gbastien]


1.0a11 (2020-09-10)
-------------------

- Leave `FolderPost._after_reply_hook` empty (was managing `wf_transitions`)
  or `wf_transitions` could be broken if a package overrides
  `_after_reply_hook` and forget to call super's original method
  [gbastien]


1.0a10 (2020-06-28)
-------------------

- Add class on list of actions
  [mpeeters]


1.0a9 (2020-06-24)
------------------

- Improve caching of REST vocabularies
  [mpeeters]

- Display `imio-restapi-actions` and `imio-restapi-links` viewlets
  only when package is installed (`IImioRestapiLayer`)
  [gbastien]


1.0a8 (2020-06-23)
------------------

- Improve filtering for remote rest vocabulary by using the id without the domain
  [mpeeters]

- Use `@relative_path` attribute for links
  [mpeeters]

- Implement base serializer to add `@relative_path` attribute
  [mpeeters]


1.0a7 (2020-06-23)
------------------

- Fix an issue with search vocabulary term ids when `b_size` parameter is used
  [mpeeters]


1.0a6 (2020-06-23)
------------------

- Fix permissions for viewlet
  [mpeeters]


1.0a5 (2020-06-23)
------------------

- Fix an error with vocabulary request when there is no body
  [mpeeters]


1.0a4 (2020-06-22)
------------------

- Add missing french translations
  [mpeeters]

- Implement basic auth adapter for requests
  [mpeeters]

- Add an adapter to allow data transform during import of content
  [mpeeters]

- Ensure that REST vocabulary base class have context available
  [mpeeters]

- Add `@uid` rest service
  [mpeeters]

- Add `ImportForm` base class for content import from remote app
  [mpeeters]

- Make `_request_schema` optional to handle more usecases
  [mpeeters]

- Add `import_content` utils to create content from rest call result
  [mpeeters]

- Add `get_application_url` and improve `generate_request_parameters` utils
  [mpeeters]

- Implement a base class vocabulary for search of objects on remote app
  [mpeeters]

- Remove `client_id` parameter from base vocabulary class since the value is set directly on zope config
  [mpeeters]

- Add caching for vocabularies
  [mpeeters]

- Update translations
  [mpeeters]

- Update form implementation for links
  [mpeeters]

- Improve link viewlet
  [mpeeters]

- Implement services for REST links
  [mpeeters]

- Add a serializer for links
  [mpeeters]

- Renamed `@pod endpoint` to `@pod-templates` to be more explicit.
  Endpoint `@pod-templates` is now a default exapandable element
  available in `@components`.
  [gbastien]

- Moved `FolderPost.wf_transitions` call into `FolderPost._after_reply_hook`.
  Update `serialized_obj` `review_state` key if transitions were triggered in
  `FolderPost.wf_transitions`.
  [gbastien]

- Added endpoint `@infos` to get various informations about application.
  This is soft depending on `Products.CPUtils` and `imio.pyutils`.
  [gbastien]

- Require `plone.restapi>=6.13.3`.
  [gbastien]

- Override `@search` default endpoint so it is easier to complete and
  is a base for sub-packages.
  Added management of `base_search_uid`, being able to give a `Collection UID`
  as base query.
  [gbastien]

1.0a3 (2020-06-08)
------------------

- Add `requests` to package dependencies
  [mpeeters]

- In `add.FolderPost.reply`, call `self.__class__` instead `FolderPost`
  to manage `children` in case we inherit from `FolderPost`.
  [gbastien]

- Added `add.FolderPost.prepare_data` to be able to prepare data
  before calling `reply` that will create the element.
  By default, this checks that data for file is correct.
  [gbastien]

- Added hook after `reply` (`_after_reply_hook`).
  [gbastien]

- If key `wf_transitions` is found during creation,
  given WF transitions are triggered.
  [gbastien]

- Added `@warnings` management in `FolderPost`.
  [gbastien]


1.0a2 (2020-01-10)
------------------

- Add REST links
  [mpeeters]

- Add REST actions
  [mpeeters]

- Add a base form class for REST interaction
  [mpeeters]

- Implement a converter from json schema to a z3c.form interface
  [mpeeters]

- Implement an endpoint to return a json schema schema
  [mpeeters]

- Implement control panel
  [mpeeters]

- Add `bulk` endpoint
  [mpeeters]

- Add a endpoint to get Archetypes vocabulary values
  [mpeeters]

- Add package tests
  [mpeeters]

- Add `@pod` endpoint that will return every `collective.documentgenerator`
  generable POD template for a context.
  This include information on the POD template and links to generate the final
  document in available output formats.
  [gbastien]


1.0a1 (2018-12-04)
------------------

- Initial release.
  [mpeeters]
