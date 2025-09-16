####################
Building from Source
####################

At the moment, installing pyhwloc **requires** building from source as I haven't figured
out how to build a redistributable binary wheel yet. In the future, it's more likely we
will rely on conda instead of PyPI. Maybe the hwloc plugin system could help.

.. contents::
    :backlinks: none
    :local:

Requirements
============

We only support the latest (> 2.12) hwloc. In addition to the basic hwloc, we have
integration with CUDA-related hwloc features and hence, the CTK is required.

Building PyHwloc from Source on Windows
=======================================

Following are some notes about the working-in-progress support for building pyhwloc and
hwloc from source on Windows using CMake. Firstly, hwloc doesn't support building the
dynamically linked library with CMake yet. We have to `patch
<https://github.com/open-mpi/hwloc/pull/738>`__ hwloc for using the ``SHARED`` CMake
keyword. Then we can run the following to build both libraries:

.. code-block:: powershell

  cd hwloc\contrib\windows-cmake\
  cmake -GNinja -DCMAKE_INSTALL_PREFIX=C:\${SOME_PATH}\pyhwloc_dev  -DCMAKE_BUILD_TYPE=RelWithDebInfo  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHWLOC_BUILD_SHARED_LIBS=ON ..
  ninja
  ninja install

The default build includes tests. Afterward, we can build pyhwloc from source:

.. code-block:: powershell

  cmake -GNinja -DCMAKE_PREFIX_PATH=C:\${SOME_PATH}\pyhwloc_dev -DCMAKE_BUILD_TYPE=RelWithDebInfo  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..\..\pyhwloc\
  ninja

Most of the tests are failing on Windows at the moment. Wheel is not yet tested.

Building PyHwloc from Source on Linux
=====================================

- Create a conda environment that's similar to the CI build.
- Build hwloc, install it into the conda environment (``CONDA_PREFIX``). We have example
  scripts used in the CI.
- Install the wheel as described in the next section.

Create a Python Wheel
=====================

- Binary wheel

.. code-block:: sh

  pip wheel -v . -w dist/ --no-build-isolation

- Use editable build:

.. code-block:: sh

  pip install -e . --no-build-isolation

- Source Wheel

.. code-block:: sh

  python -m build --sdist

Building the Document
=====================

We have a docker file in the project for creating the environment with the right
doxygen. Following are notes for how to do it manually.

We use the ``breathe`` project to generate sphinx doc for low-level API from the C doxygen
document. This requires:

- Set the ``HWLOC_DOXYGEN_GENERATE_XML=YES`` environment variable when running doxygen
  with hwloc:

.. code-block:: sh

  cd hwloc/doc
  HWLOC_DOXYGEN_GENERATE_XML=YES doxygen ./doxygen.cfg

- One must run the hwloc `configure` script under the project root with the
  ``--enable-doxygen`` option since the ``doxygen-config.cfg`` file is generated under the
  build root.

- You can inform the sphinx build about the XML path via the ``PYHWLOC_XML_PATH``
  environment variable:

.. code-block:: sh

  cd pyhwloc/docs
  PYHWLOC_XML_PATH=/path/hwloc/doc/doxygen-doc/xml make html

Another issue with doxygen files is how to obtain a clang-assisted doxygen build. The
build-time dependencies (aside from the standard C++ toolchain) for doxygen on Ubuntu
24.04:

- flex
- bison
- xml2
- libclang-19-dev

I have also created an `issue
<https://github.com/conda-forge/doxygen-feedstock/issues/57>`__ for the doxygen feedstock
to ask for clang support. In the meanwhile, see the CI scripts for conda dependencies.

Running Tests
=============

We use ``pytest`` for testing the `pyhwloc` package. The following snippet uses
`pytest-cov` as well. We use the cov package to track the coverage of hwloc features
during early development.

.. code-block:: sh

  pytest ./pyhwloc/tests/ --cov=pyhwloc --cov-report=html

The container image used for GitHub action is built from the `dev/Dockerfile.cpu`:

.. code-block:: sh

  docker build --progress=plain -f ./Dockerfile.cpu . -t pyhwloc:latest
