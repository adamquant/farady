from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Define the extensions to be compiled with Cython
extensions = [
    Extension(
        "farady.core_functions",
        ["src/farady/core_functions.py"],
        include_dirs=[numpy.get_include()],
    ),
    Extension(
        "farady.pipelines",
        ["src/farady/pipelines.py"],
        include_dirs=[numpy.get_include()],
    ),
]

# Setup configuration
setup(
    ext_modules=cythonize(extensions, compiler_directives={"language_level": 3}),
    zip_safe=False,
)
