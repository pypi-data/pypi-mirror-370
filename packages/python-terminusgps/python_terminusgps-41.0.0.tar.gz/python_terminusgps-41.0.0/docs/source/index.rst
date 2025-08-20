.. python-terminusgps documentation master file, created by
   sphinx-quickstart on Wed Feb 19 10:39:57 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

python-terminusgps documentation
================================

`python-terminusgps <https://pypi.org/project/python-terminusgps>`_ is a package [#f1]_ of subpackages that streamlines the use of web APIs for Terminus GPS developers.

`Terminus GPS <https://terminusgps.com/>`_ is an IoT hardware/software GPS monitoring company.

.. [#f1] In other programming languages, the term "library" is used to describe what Python calls a "package". Put simply, a "package" is a Python "library".

============
Installation
============


Use pip to install from `PyPI <https://pypi.org/project/python-terminusgps/>`_.

.. code:: bash

   pip install python-terminusgps

All subpackages are nested within :py:mod:`terminusgps`:

.. code:: python

    from terminusgps.wialon.session import WialonSession # Creates Wialon API sessions

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    authorizenet/index.rst
    django/index.rst
    wialon/index.rst
