# This code is part of Mthree.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""M3: Matrix-free measurement mitigation"""

import os
import sys
import warnings
import subprocess
import setuptools

import numpy as np
from Cython.Build import cythonize

MAJOR = 3
MINOR = 0
MICRO = 0

ISRELEASED = True
VERSION = "%d.%d.%d" % (MAJOR, MINOR, MICRO)

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

PACKAGES = setuptools.find_packages()
PACKAGE_DATA = {
    "mthree": ["*.pxd"],
}
DOCLINES = __doc__.split("\n")
DESCRIPTION = DOCLINES[0]
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.md"), encoding="utf-8") as readme:
    LONG_DESCRIPTION = readme.read()

CYTHON_EXTS = ["converters", "hamming", "matrix", "probability", "matvec"] + [
    "expval",
    "column_testing",
    "converters_testing",
    "hadamard",
]
CYTHON_MODULES = ["mthree"] * 6 + ["mthree.test"] * 2 + ["mthree.generators"]
CYTHON_SOURCE_DIRS = ["mthree"] * 6 + ["mthree/test"] * 2 + ["mthree/generators"]

# Add openmp flags
OPTIONAL_FLAGS = []
OPTIONAL_ARGS = []
WITH_OMP = False
for _arg in sys.argv:
    if _arg == "--openmp" or _arg == "--with-openmp":
        WITH_OMP = True
        if _arg == "--with-openmp":
            warnings.warn(
                "Using '--with-openmp' to set openmp is deprecated.", DeprecationWarning
            )
        sys.argv.remove(_arg)
        break
if WITH_OMP or os.getenv("MTHREE_OPENMP", False):
    WITH_OMP = True
    if sys.platform == "win32":
        OPTIONAL_FLAGS = ["/openmp"]
    else:
        OPTIONAL_FLAGS = ["-fopenmp"]
    OPTIONAL_ARGS = OPTIONAL_FLAGS

if os.getenv("MTHREE_ARCH", False):
    OPTIONAL_FLAGS.append("-march=" + os.getenv("MTHREE_ARCH"))

INCLUDE_DIRS = [np.get_include()]
# Extra link args
LINK_FLAGS = []
# If on Win and not in MSYS2 (i.e. Visual studio compile)
if sys.platform == "win32" and os.environ.get("MSYSTEM", None) is None:
    COMPILER_FLAGS = ["/O3"]
# Everything else
else:
    COMPILER_FLAGS = [
        "-O3",
        "-ffast-math",
        "-std=c++17",
        "-DNPY_NO_DEPRECATED_API=NPY_1_23_API_VERSION",
    ]

EXT_MODULES = []
# Add Cython Extensions
for idx, ext in enumerate(CYTHON_EXTS):
    mod = setuptools.Extension(
        CYTHON_MODULES[idx] + "." + ext,
        sources=[CYTHON_SOURCE_DIRS[idx] + "/" + ext + ".pyx"],
        include_dirs=INCLUDE_DIRS,
        extra_compile_args=COMPILER_FLAGS + OPTIONAL_FLAGS,
        extra_link_args=LINK_FLAGS + OPTIONAL_ARGS,
        language="c++",
    )
    EXT_MODULES.append(mod)


def git_short_hash():
    try:
        git_str = "+" + os.popen('git log -1 --format="%h"').read().strip()
    except:  # pylint: disable=bare-except
        git_str = ""
    else:
        if git_str == "+":  # fixes setuptools PEP issues with versioning
            git_str = ""
    return git_str


FULLVERSION = VERSION
if not ISRELEASED:
    FULLVERSION += ".dev" + str(MICRO) + git_short_hash()


def write_version_py(filename="mthree/version.py"):
    cnt = """\
# THIS FILE IS GENERATED FROM MTHREE SETUP.PY
# pylint: disable=missing-module-docstring
short_version = '%(version)s'
version = '%(fullversion)s'
openmp = %(with_omp)s
"""
    a = open(filename, "w")
    try:
        a.write(
            cnt
            % {
                "version": VERSION,
                "fullversion": FULLVERSION,
                "with_omp": str(WITH_OMP),
            }
        )
    finally:
        a.close()


local_path = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(local_path)
sys.path.insert(0, local_path)
sys.path.insert(0, os.path.join(local_path, "mthree"))  # to retrive _version

# always rewrite _version
if os.path.exists("mthree/version.py"):
    os.remove("mthree/version.py")

write_version_py()


# Add command for running pylint from setup.py
class PylintCommand(setuptools.Command):
    """Run Pylint on all mthree Python source files."""

    description = "Run Pylint on mthree Python source files"
    user_options = [
        # The format is (long option, short option, description).
        ("pylint-rcfile=", None, "path to Pylint config file")
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.pylint_rcfile = ""  # pylint: disable=attribute-defined-outside-init

    def finalize_options(self):
        """Post-process options."""
        if self.pylint_rcfile:
            assert os.path.exists(self.pylint_rcfile), (
                "Pylint config file %s does not exist." % self.pylint_rcfile
            )

    def run(self):
        """Run command."""
        command = ["pylint"]
        if self.pylint_rcfile:
            command.append("--rcfile=%s" % self.pylint_rcfile)
        command.append(os.getcwd() + "/mthree")
        subprocess.run(command, stderr=subprocess.STDOUT, check=False)


# Add command for running PEP8 tests from setup.py
class StyleCommand(setuptools.Command):
    """Run pep8 from setup."""

    description = "Run style from setup"
    user_options = [
        # The format is (long option, short option, description).
        ("abc", None, "abc")
    ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        command = "pycodestyle --max-line-length=100 mthree"
        subprocess.run(command, shell=True, check=False, stderr=subprocess.STDOUT)


setuptools.setup(
    name="mthree",
    version=VERSION,
    python_requires=">=3.9",
    packages=PACKAGES,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="",
    author="Paul Nation",
    author_email="paul.nation@ibm.com",
    license="Apache 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
    ],
    cmdclass={"lint": PylintCommand, "style": StyleCommand},
    install_requires=REQUIREMENTS,
    package_data=PACKAGE_DATA,
    ext_modules=cythonize(EXT_MODULES, language_level=3),
    include_package_data=True,
    zip_safe=False,
)
