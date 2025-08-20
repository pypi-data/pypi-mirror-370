mergeron: Python for analyzing merger enforcement policy
========================================================


.. image:: https://img.shields.io/pypi/v/mergeron
   :alt: PyPI - Package Version
   :target: https://pypi.python.org/pypi/mergeron/
.. image:: https://img.shields.io/pypi/pyversions/mergeron
   :alt: PyPI - Python Version
   :target: https://pypi.python.org/pypi/mergeron/
.. image:: https://img.shields.io/pypi/status/mergeron
   :alt: PyPI - Package status
   :target: https://pypi.python.org/pypi/mergeron/
.. image:: https://github.com/capeconomics/mergeron/actions/workflows/documentation.yml/badge.svg
   :alt: documentation
   :target: https://github.com/capeconomics/mergeron/actions/workflows/documentation.yml
.. image:: https://github.com/capeconomics/mergeron/actions/workflows/packaging.yml/badge.svg
    :alt: CI
    :target: https://github.com/capeconomics/mergeron/actions/workflows/packaging.yml

|

.. image:: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json
   :target: https://python-poetry.org/
.. image:: https://www.mypy-lang.org/static/mypy_badge.svg
   :target: https://mypy-lang.org/
.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff/
.. image:: https://img.shields.io/badge/code%20style-black-000000
   :target: https://github.com/psf/black/
.. image:: https://img.shields.io/badge/License-MIT-yellow
   :alt: License: MIT
   :target: https://opensource.org/licenses/MIT/


*Visualize* the sets of mergers falling within specified concentration and diversion-ratio thresholds.  *Analyze* merger investigations data published by the U.S. Federal Trade Commission in various reports on extended merger investigations (Second Requests) during 1996 to 2011.
*Generate* data under specified distributions of firm counts, market shares, price-cost margins, and prices, optionally imposing equilibrium conditions for Bertrand oligopoly with MNL demand and or restrictions implied by statutory filing thresholds. *Compute* intrinsic enforcement rates or
intrinsic clearance rates using the generated data, given thresholds for
concentration;
diversion ratio;
gross upward pricing pressure (GUPPI);
critical marginal cost reduction (CMCR); and
illustrative price rise (IPR).

Installation
------------

To install the package, use the following shell command:

.. code:: bash

    pip install mergeron


Documentation
-------------

Usage guide and API reference are `available <https://capeconomics.github.io/mergeron/>`_.
