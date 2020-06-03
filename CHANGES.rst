Changelog
=========


1.0a3 (unreleased)
------------------

- In `add.FolderPost.reply`, call `self.__class__` instead `FolderPost`
  to manage `children` in case we inherit from `FolderPost`.
  [gbastien]
- Added `add.FolderPost.prepare_child_data` to be able to prepare child data
  before calling `reply` that will create the element.
  [gbastien]
- Added some hooks before (`_prepare_data`) and
  after `reply` (`_after_reply_hook`).
  [gbastien]
- If key `wf_transitions` is found during creation,
  given WF transitions are triggered.
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
