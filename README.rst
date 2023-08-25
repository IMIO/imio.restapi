.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://travis-ci.com/IMIO/imio.restapi.svg?branch=master
    :target: https://travis-ci.com/IMIO/imio.restapi

.. image:: https://coveralls.io/repos/github/IMIO/imio.restapi/badge.svg?branch=master
    :target: https://coveralls.io/github/IMIO/imio.restapi?branch=master

.. image:: http://img.shields.io/pypi/v/imio.restapi.svg
   :alt: PyPI badge
   :target: https://pypi.org/project/imio.restapi


============
imio.restapi
============

plone.restapi endpoints and adaptations

Features
--------

- ``add element``:

    - with children
    - trigger WF transitions
- ``@pod-templates`` endpoint (collective.documentgenerator)
- ``disable returning fullobject serialization upon creation``:

  - by default when an object is created, the fullobject serialization is returned which is doing some processing sometimes unnecessary
  - adding an environment variable ``RETURN_FULLOBJECT_AFTER_CREATION_DEFAULT False`` will return the summary serialization when an object is created
  - this will change the default behavior but it is still possible to change this behavior for a particular POST by defining the ``"return_fullobject": true/false`` in the Body

Todo
----

- manage wf_transitions triggered when creating an element in the deserializer when we will be using only DX
- include cleanHTML functionnality at the deserializer level, also when we will be using only DX


Installation
------------

Install imio.restapi by adding it to your buildout::

    [buildout]

    ...

    eggs =
        imio.restapi


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/imio.restapi/issues
- Source Code: https://github.com/collective/imio.restapi
- Documentation: https://docs.plone.org/foo/bar


License
-------

The project is licensed under the GPLv2.
