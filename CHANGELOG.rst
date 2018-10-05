Change Log
==========

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

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
