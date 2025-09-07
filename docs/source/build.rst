####################
Building from Source
####################

Following are some notes about the working-in-progress support for building pyhwloc and
hwloc from source on Windows using CMake. Firstly, hwloc doesn't support building the
dynamically linked library with CMake yet. We have to patch hwloc for using the ``SHARED``
CMake keyword. Then we can run the following to build both libraries:

.. code-block:: powershell

    cd hwloc\contrib\windows-cmake\
    cmake -GNinja -DCMAKE_INSTALL_PREFIX=C:\${SOME_PATH}\pyhwloc_dev  -DCMAKE_BUILD_TYPE=RelWithDebInfo  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DHWLOC_BUILD_SHARED_LIBS=ON ..
    ninja
    ninja install

The default build includes tests. Afterward, we can build pyhwloc from source:

.. code-block:: powershell

    cmake -GNinja -DCMAKE_PREFIX_PATH=C:\${SOME_PATH}\pyhwloc_dev -DCMAKE_INSTALL_PREFIX=C:\${SOME_PATH}\pyhwloc_dev  -DCMAKE_BUILD_TYPE=RelWithDebInfo  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..\..\pyhwloc\
    ninja

Most of the tests are failing at the moment.

#############
Running Tests
#############

.. code-block:: sh

    pytest ./pyhwloc/tests/ --cov=pyhwloc --cov-report=html