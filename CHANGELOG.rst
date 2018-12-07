Change Log
==========

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

0.3.0
-----

Removed
~~~~~~~

* Compatibility with python 3.3

Fixed
~~~~~
* QueryString filters and tags are executed only one time by query

Refactored
~~~~~~~~~~

* The error field is now the key of the errors description dict (All validation errors messages are now dict)

0.2.2
-----

Fixed
~~~~~

* in the context manager to save the error, the registry is now rollbacked

0.2.1 (2019-10-06)
------------------

Added
~~~~~

* MANIFEST.in file

Removed
~~~~~~~

* VERSION file

0.2.0 (2019-10-01)
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
