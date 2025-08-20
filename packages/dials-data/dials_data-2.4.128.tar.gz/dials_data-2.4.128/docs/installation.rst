.. highlight:: shell

======================
Installation and Usage
======================

There are a number of possible ways to install ``dials-data``.
From the simplest to the most involved these are:


As an end user
^^^^^^^^^^^^^^

Quite simply: You do not need to install ``dials-data``.
It does not add any functionality to end users.


As a developer to run tests with ``dials-data``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You may want to install ``dials-data`` so that you can run regression tests locally.
Or you might say that continuous integration should take care of this.
Both are valid opinions.

.. _basic-installation:

However you do not need to install ``dials-data`` from source. You can simply run::

    pip install -U dials-data

or, in a conda environment::

    conda install -c conda-forge dials-data

This will install or update an existing installation of ``dials-data``.

You can then run your tests as usual using::

    pytest

although, depending on the configuration of the code under test, you
probably need to run it as::

    pytest --regression

to actually enable those tests depending on files from ``dials-data``.


As a developer to write tests with ``dials-data``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Install ``dials-data`` as above.

If your test is written in pytest and you use the fixture provided by
``dials-data`` then you can use regression datasets in your test by
adding the ``dials_data`` fixture to your test, ie:

.. code-block:: python

    def test_accessing_a_dataset(dials_data):
        location = dials_data("x4wide", pathlib=True)

The fixture/variable ``dials_data`` in the test is a
``dials_data.download.DataFetcher`` instance, which can be called with
the name of the dataset you want to access (here: ``x4wide``). If the
files are not present on the machine then they will be downloaded.
If either the download fails or ``--regression`` is not specified then
the test is skipped.

The return value (``location``) is a ``pathlib.Path`` object pointing
to the directory containing the requested dataset.

To get a python ``py.path.local`` object instead you can call:

.. code-block:: python

    def test_accessing_a_dataset(dials_data):
        location = dials_data("x4wide", pathlib=False)

However, please note that the ``py.path`` support is deprecated, and
will be removed at some point in the future. Currently, if you do not
specify the ``pathlib=`` argument a ``py.path`` object is returned.

You can see a list of all available datasets by running::

    dials.data list

or by going through the
`dataset definition files in the repository <https://github.com/dials/data/tree/master/dials_data/definitions>`__.

If you want the tests on your project to be runnable even when
``dials-data`` is not installed in the environment you could add a
dummy fixture to your ``conftest.py``, for example:

.. code-block:: python

    import pytest
    try:
        import dials_data as _  # noqa: F401
    except ModuleNotFoundError:
        @pytest.fixture(scope="session")
        def dials_data():
            pytest.skip("Test requires python package dials_data")


As a developer who wants to add files to ``dials-data``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Follow the steps in :doc:`/contributing` to install ``dials-data`` into a
virtual environment.

You can install ``dials-data`` using ``pip`` as above *unless* you want to
immediately use your dataset definition in tests without waiting for your
pull request to be accepted. In this case you can follow the instructions
in the next step.


As a developer who wants to extend ``dials-data``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Have a look at the :doc:`/contributing` page.

Install your own fork of ``dials-data`` by running::

    pip install -e path/to/fork

in a cctbx/DIALS environment use ``libtbx.pip`` respectively, followed by
a round of ``libtbx.configure`` or ``make reconf``.

If you made substantial changes or updated your source copy you may also
have to run::

    python setup.py develop

This will update your python package index and install/update any
``dials-data`` dependencies if necessary.

To switch back from using your checked out version to the 'official'
version of ``dials-data`` you can uninstall it with::

    pip uninstall dials-data

and then reinstall it following the
`instructions at the top of this page <basic-installation_>`__.


Where are the regression datasets stored?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order of evaluation:

* If the environment variable ``DIALS_DATA`` is set and exists or can be
  created then use that location.
* If the file path ``/dls/science/groups/scisoft/DIALS/dials_data`` exists and is readable then
  use this location. This is a shared directory specific to Diamond Light Source.
* If the environment variable ``LIBTBX_BUILD`` is set and the directory
  ``dials_data`` exists or can be created underneath that location then
  use that.
* Use ``~/.cache/dials_data`` if it exists or can be created.
* Otherwise ``dials-data`` will fail with a RuntimeError.
