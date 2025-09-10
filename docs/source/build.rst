####################
Building from Source
####################

Building PyHwloc from source on Windows
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

    cmake -GNinja -DCMAKE_PREFIX_PATH=C:\${SOME_PATH}\pyhwloc_dev -DCMAKE_INSTALL_PREFIX=C:\${SOME_PATH}\pyhwloc_dev  -DCMAKE_BUILD_TYPE=RelWithDebInfo  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..\..\pyhwloc\
    ninja

Most of the tests are failing on Windows at the moment.

Building the Document
=====================

We use the ``breathe`` project to generate sphinx doc for low-level API from the C doxygen
document. This requires:

- Set the ``HWLOC_DOXYGEN_GENERATE_XML=YES`` environment variable when running doxygen:

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
- libclang-19-dev

Running Tests
=============

.. code-block:: sh

  pytest ./pyhwloc/tests/ --cov=pyhwloc --cov-report=html


Create a Binary Wheel
=====================

First build the c ext via CMake, then run

.. code-block:: sh

  pip wheel . --no-build-isolation

Use editable build:

.. code-block:: sh

  pip install -e . --no-build-isolation