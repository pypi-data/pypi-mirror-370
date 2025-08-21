.. image:: https://img.shields.io/pypi/v/dimod.svg
    :target: https://pypi.org/project/dimod

.. image:: https://img.shields.io/pypi/pyversions/dimod.svg
    :target: https://pypi.python.org/pypi/dimod

.. image:: https://circleci.com/gh/dwavesystems/dimod.svg?style=svg
    :target: https://circleci.com/gh/dwavesystems/dimod

.. image:: https://codecov.io/gh/dwavesystems/dimod/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/dwavesystems/dimod

=====
dimod
=====

.. start_dimod_about

`dimod` is a shared API for samplers. It provides:

*   Classes for quadratic models---such as the binary quadratic model (BQM)
    class that contains Ising and QUBO models used by samplers such as the
    D-Wave quantum computer---and higher-order (non-quadratic) models.
*   Reference examples of samplers and composed samplers.
*   `Abstract base classes <https://docs.python.org/3/library/abc.html>`_ for
    constructing new samplers and composed samplers.

>>> import dimod
...
>>> # Construct a problem
>>> bqm = dimod.BinaryQuadraticModel({0: -1, 1: 1}, {(0, 1): 2}, 0.0, dimod.BINARY)
...
>>> # Use dimod's brute force solver to solve the problem
>>> sampleset = dimod.ExactSolver().sample(bqm)
>>> print(sampleset)
   0  1 energy num_oc.
1  1  0   -1.0       1
0  0  0    0.0       1
3  0  1    1.0       1
2  1  1    2.0       1
['BINARY', 4 rows, 4 samples, 2 variables]

.. end_dimod_about

For explanations of the terminology, see the
`Ocean glossary <https://docs.dwavequantum.com/en/latest/concepts/index.html>`_.

See the `documentation <https://docs.dwavequantum.com/en/latest/index.html>`_
for more examples.

Installation
============

Installation from `PyPI <https://pypi.org/project/dimod>`_:

.. code-block:: bash

    pip install dimod

License
=======

Released under the Apache License 2.0. See LICENSE file.

Contributing
============

Ocean's
`contributing <https://docs.dwavequantum.com/en/latest/ocean/contribute.html>`_
section has guidelines for contributing to Ocean packages.

dimod includes some formatting customization in the
`.clang-format <.clang-format>`_ and `setup.cfg <setup.cfg>`_ files.

Release Notes
-------------

dimod makes use of `reno <https://docs.openstack.org/reno/>`_ to manage its
release notes.

When making a contribution to dimod that will affect users, create a new
release note file by running

.. code-block:: bash

    reno new your-short-descriptor-here

You can then edit the file created under ``releasenotes/notes/``.
Remove any sections not relevant to your changes.
Commit the file along with your changes.

See reno's
`user guide <https://docs.openstack.org/reno/latest/user/usage.html>`_ for
details.