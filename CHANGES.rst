Changelog
=========


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
