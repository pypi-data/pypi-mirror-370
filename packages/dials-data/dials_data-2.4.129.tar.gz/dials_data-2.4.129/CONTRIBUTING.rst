.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/dials/data/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Add Datasets
~~~~~~~~~~~~

DIALS data was planned to support a more or less arbitrary number of datasets.
You can contribute by adding more.

Write Documentation
~~~~~~~~~~~~~~~~~~~

DIALS Regression Data could always use more documentation, whether as part of the
official DIALS Regression Data docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/dials/data/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `dials-data` for local development.

1. Fork the `dials/data` `repository on GitHub <https://github.com/dials/data>`__.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/data.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv dials_data
    $ cd dials_data/
    $ python setup.py develop

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. Before committing changes to the repository you should install pre-commit::

    $ pre-commit install

   If you do not have pre-commit set up, you can install it with pip.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. Unless you are only touching datasets the pull request should include tests.
2. If you add or update a dataset then make individual pull requests for each
   dataset, so that they can be discussed and approved separately.
3. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in HISTORY.rst.


Deploying
---------

Any commit on the master branch is now automatically deployed to PyPI, so there
is no need to play around with tags or version numbers on a regular basis.

For slightly larger changes make sure that the entry in HISTORY.rst is updated,
and then run::

$ bumpversion minor # possible: major / minor, do not use patch

Travis will then automatically tag the commit once it hits the master branch
and the tests pass, and then deploy to PyPI as usual.
