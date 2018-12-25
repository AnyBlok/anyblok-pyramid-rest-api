Change Log
==========

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

0.4.0
-----

Added
~~~~~

* CrudResource.execute(name, kwarg) decorator to define Service on:

  - `collection_path`/execute/`name`: validator on the body
  - `path`/execute/`name`: validator on the path and the body

  ::

      @resource(collection_path='/foo', path='/foo/{bar}')
      class MyResource(CrudResource):
          @CrudResource.execute('print', collection=True)  # schema optional
          def plop(self):  # /foo/execute/print
              # query = self.get_querystring('rest action given to get_model')
              # body = self.body
              ...

          @CrudResource.execute('print')  # schema optional for body, pathschema for path
          def otherplop(self):  # /foo/{bar}/execute/print
              # body = self.body
              ...

* Collection views to update and delete collection defined by querystring:

  - collection_put
  - collection_patch
  - collection_delete




Refactored
~~~~~~~~~~

* If a ``request.error`` is found during the execution of a view in the crud resource,
  then a registry.rollback will be done

0.3.0 (2018-12-07)
------------------

Removed
~~~~~~~

* Compatibility with python 3.3

Fixed
~~~~~
* QueryString filters and tags are executed only one time by query
* in the context manager to save the error, the registry is now rollbacked

Refactored
~~~~~~~~~~

* The error field is now the key of the errors description dict (All validation errors messages are now dict)

0.2.1 (2018-10-06)
------------------

Added
~~~~~

* MANIFEST.in file

Removed
~~~~~~~

* VERSION file

0.2.0 (2018-10-01)
------------------

Added
~~~~~

* **context** key in querystring. The goal is to add some informations 
  to help custom filter and tag to build their query

Refactored
~~~~~~~~~~

* Now the querystring desarializer use regex to get the informations

0.1.0 (2018-09-26)
------------------

Added
~~~~~

* **CRUDResource** class to define REST api
* service behaviours
