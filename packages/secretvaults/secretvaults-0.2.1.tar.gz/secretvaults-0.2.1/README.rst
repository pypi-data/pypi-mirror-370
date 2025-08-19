secretvaults
=============

SDK for interacting with Nillion's `Private Storage <https://docs.nillion.com/build/private-storage/overview>`__ solutions.

|pypi| |actions|

.. |pypi| image:: https://badge.fury.io/py/secretvaults.svg
   :target: https://badge.fury.io/py/secretvaults
   :alt: PyPI version and link.

.. .. |readthedocs| image:: https://readthedocs.org/projects/secretvaults/badge/?version=latest
..    :target: https://secretvaults.readthedocs.io/en/latest/?badge=latest
..    :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/nillionnetwork/nillion-sv-wrappers-py/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/nillionnetwork/nillion-sv-wrappers-py/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. .. |coveralls| image:: https://coveralls.io/repos/github/NillionNetwork/secretvaults-py/badge.svg?branch=main
..    :target: https://coveralls.io/github/NillionNetwork/secretvaults-py?branch=main
..    :alt: Coveralls test coverage summary.

Description and Purpose
------------------------

Provides functions to simplify usage of Nillion's Private Storage.


Installation and Usage
-----------------------

You can install the package using pip:

.. code-block:: bash

    pip install secretvaults


The library can be imported in the usual ways:

.. code-block:: python

    import secretvaults
    from secretvaults import *



Examples and Documentation
-------------------------------

Please see the `examples <https://github.com/NillionNetwork/secretvaults-py/tree/main/examples>`__ directory for examples and documentation.


Development
-----------

All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__:

.. code-block:: bash

    python -m pip install ".[docs,lint]"

Documentation
-------------

The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__:

.. code-block:: bash

    python -m pip install ".[docs]"
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
------------------------

All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details):

.. code-block:: bash

    python -m pip install ".[test]"
    python -m pytest test

Style conventions are enforced using `Pylint <https://pylint.readthedocs.io>`__:

.. code-block:: bash

    python -m pip install ".[lint]"
    python -m pylint src/secretvaults

Contributions
-------------

To contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/nillionnetwork/secretvaults-py>`__ for this library.

Versioning
----------

The version number format for this library and the changes to the library associated with version number increments conform to `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
----------

This library can be published as a `package on PyPI <https://pypi.org/project/secretvaults>`__ via the GitHub Actions workflow found in ``.github/workflows/build-publish-sign-release.yml`` that follows the `recommendations found in the Python Packaging User Guide <https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/>`__.

