############
Installation
############

You can `pip` install M3 in using PyPi via:

.. code-block:: bash

    pip install mthree


This will install an OpenMP optimized version on Linux, and serial versions for OSX and Windows. Alternatively, one can install from source:

.. code-block:: bash

    python install .


To enable OpenMP, you must have an OpenMP 4.0+ enabled compiler and install with:

.. code-block:: bash

    MTHREE_OPENMP=1 pip install .


OpenMP on OSX
-------------

On OSX one must install GCC using homebrew:

.. code-block:: bash

    brew install gcc


Then installation with openmp can be accomplished using a call like:

.. code-block:: bash

    MTHREE_OPENMP=1 CC=gcc-14 CXX=g++14 python setup.py install

Note that previously the instructions said to install LLVM and NOT GCC. However, in the latest version of OSX (Sequoia) LLVM based installations will build, but segfault upon execution. GCC however works fine, thus the change above.
