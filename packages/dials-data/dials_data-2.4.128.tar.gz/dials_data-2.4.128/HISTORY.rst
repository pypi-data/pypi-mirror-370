=======
History
=======

2.5 (????-??-??)
^^^^^^^^^^^^^^^^

* Fix permission generation when extracting tar archives. Files extracted will be created with
  default permissions, instead of what has been packed in with the archive. This solves the issue
  of shared data stores becoming inaccessible to some users.
* ``DataFetcher``: new parameter verify=True to verify download hashinfo by default.

2.4 (2022-03-07)
^^^^^^^^^^^^^^^^

* dials_data no longer uses ``py.path`` internally.
* dials_data now includes type checking with mypy.
* We started using the ``requests`` library for faster downloads.
* Downloads now happen in parallel.

2.3 (2022-01-11)
^^^^^^^^^^^^^^^^

* Drop Python 3.6 compatibility
* Dataset `SSX_CuNiR_processed` has been renamed to `cunir_serial_processed` for consistency
  with `cunir_serial`

2.2 (2021-06-18)
^^^^^^^^^^^^^^^^

* Deprecate the use of ``py.path`` as test fixture return type.
  You can either silence the warning by specifying ``dials_data("dataset", pathlib=False)``
  or move to the new ``pathlib.Path`` return objects by setting ``pathlib=True``.
  This deprecation is planned to be in place for a considerable amount of time.
  In the next major release (3.0) the default return type will become ``pathlib.Path``,
  with ``py.path`` still available if ``pathlib=False`` is specified. At this point
  the ``pathlib=`` argument will be deprecated.
  In the following minor release (3.1) all support for ``py.path`` will be dropped.

2.1 (2020-06-11)
^^^^^^^^^^^^^^^^

* Drops Python 2.7 compatibility
* Uses importlib.resources to access resource files (requires Python 3.9 or installed package importlib_resources)

2.0 (2019-04-15)
^^^^^^^^^^^^^^^^

* Convert dials_data to a pytest plugin

1.0 (2019-02-16)
^^^^^^^^^^^^^^^^

* Add functions for forward-compatibility
* Enable new release process including automatic deployment of updates

0.6 (2019-02-15)
^^^^^^^^^^^^^^^^

* Added datasets blend_tutorial, thaumatin_i04

0.5 (2019-01-24)
^^^^^^^^^^^^^^^^

* Added documentation
* Added datasets fumarase, vmxi_thaumatin

0.4 (2019-01-11)
^^^^^^^^^^^^^^^^

* Beta release
* Added datasets insulin, pychef
* Automated generation of hashinfo files via Travis


0.3 (2019-01-09)
^^^^^^^^^^^^^^^^

* Dataset download mechanism
* Added dataset x4wide


0.2 (2019-01-08)
^^^^^^^^^^^^^^^^

* Alpha release
* Basic command line interface
* pytest fixture


0.1 (2018-11-02)
^^^^^^^^^^^^^^^^

* First automatic deployment and release on PyPI
