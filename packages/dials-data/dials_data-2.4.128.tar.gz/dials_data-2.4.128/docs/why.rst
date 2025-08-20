======================
What is ``dials-data``
======================

``dials-data`` is a lightweight, simple python(-only) package.
It is used to provide access to data files used in regression tests,
but does not contain any of those data files itself.

Although we envisage it mostly being used in a cctbx_\ /\ DIALS_
environment for tests in DIALS_, dxtbx_, xia2_ and related packages,
it has no dependencies on either cctbx_ or DIALS_, in fact
all dependencies are explicitly declared in the setup.py_ file and are
installable via standard setuptools/pip methods.
This means ``dials-data`` can easily be used in other projects accessing
the same data, and can be used in temporary environments such as
Travis containers.

But - why?
==========

In the past DIALS_ tests used an internal SVN repository called
dials_regression to collect any file that would be useful in tests,
but should not be distributed with a standard DIALS_ distribution.
This made it easy to add files, from a single JSON file to example
files from different detectors to whole datasets.
Similarly, all a developer had to do to update the collection was to
update the checked out SVN repository.

Over time the downsides of the SVN repository approach became obvious:
a checked out copy requires twice the storage space on the local disk.
Sparse checkouts are possible, but become increasingly complicated as
more files are added. This quickly becomes impractical in distributed
testing environments. The disk space required for checkouts can be
reduced by compressing the data, but then they need to be unpacked for
using the data in tests. By its nature the internal SVN repository was
not publicly accessible. The data files were too large to convert the
repository to a git repository to be hosted on Github, and in any case
a git repository was not the best place either to store large amounts
of data, as old versions of the data or retired datasets are kept
forever, and sparse checkouts would be even more complex. Git LFS
would just raise the complexity even further and would incur associated
costs. A solution outside SVN/git was built with xia2_regression_,
which provided a command to download a copy of datasets from a regular
webhost. This worked well for a while but still made it complicated to
use the data files in tests, as they had to be downloaded -- in full --
first.

With dxtbx_, dials_ and xia2_ moving to pytest_ we extended the
xia2_regression_ concept into the regression_data_ fixture to provide
a simple way to access the datasets in tests, but the data still
needed downloading separately and could not easily be used outside
of the dials_ repository and not at all outside of a dials_
distribution. Adding data files was still a very involved process.

``dials-data`` is the next iteration of our solution to this problem.

What can ``dials-data`` do
==========================

The entire pipeline, from adding new data files, to the automatic
download, storage, preparation, verification and provisioning of the
files to tests happens in a single, independent Python package.

Data files are versioned without being kept in an SVN or git
repository. The integrity of data files can be guaranteed. Files are
downloaded/updated as and when required. The provenance of the files
is documented, so it can be easily identified who the author of the
files is and under what license they have been made available.
New datasets can be created, existing ones can be updated easily by
anyone using Github pull requests.

.. _cctbx: https://cctbx.github.io
.. _DIALS: https://dials.github.io
.. _dxtbx: https://github.com/cctbx/cctbx_project/tree/master/dxtbx
.. _pytest: https://docs.pytest.org/
.. _regression_data: https://github.com/dials/dials/blob/e54b36b38b3f37c043a5f8f6e54c84db612a387b/conftest.py#L42-L57
.. _setup.py: https://github.com/dials/data/blob/master/setup.py
.. _xia2: https://xia2.github.io
.. _xia2_regression: https://github.com/xia2/xia2_regression
