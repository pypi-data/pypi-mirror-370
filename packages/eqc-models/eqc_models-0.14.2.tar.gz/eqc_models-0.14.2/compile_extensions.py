import os
import sys
from setuptools import Extension
from setuptools.command.build_py import build_py as _build_py
import numpy

# # Set cvqboost compile args
# if sys.platform == "darwin":
#     openmp_prefix = os.environ.get(
#         "LIBOMP_PREFIX", "/opt/homebrew/opt/libomp"
#     )
#     openmp_include = os.path.join(openmp_prefix, "include")
#     openmp_lib = os.path.join(openmp_prefix, "lib", "libomp.a")
#     extra_compile_args_cvq = [
#         "-Xpreprocessor",
#         "-fopenmp",
#         "-O3",
#         "-ffast-math",
#         "-march=native",
#     ]
#     extra_link_args_cvq = [openmp_lib, "-O3", "-march=native"]
# elif sys.platform.startswith("linux"):
#     extra_compile_args_cvq = [
#         "-static-libgcc",
#         "-fopenmp",
#         "-O3",
#         "-ffast-math",
#     ]
#     extra_link_args_cvq = [
#         "-static-libgcc",
#         "-static-libstdc++",
#         "-fopenmp",
#         "-O3",
#     ]
# elif sys.platform == "win32":
#     extra_compile_args_cvq = ["/openmp"]
#     extra_link_args_cvq = []

# Modules to be compiled and include_dirs when necessary
extensions = [
    Extension(
        "eqc_models.base.polyeval",
        ["eqc_models/base/polyeval.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-ffast-math"],
    ),
    # Extension(
    #     "eqc_models.ml.cvqboost_hamiltonian",
    #     ["eqc_models/ml/cvqboost_hamiltonian.pyx"],
    #     include_dirs=[numpy.get_include()],
    #     extra_compile_args=extra_compile_args_cvq,
    #     extra_link_args=extra_link_args_cvq,
    # ),
]


class build_py(_build_py):
    def run(self):
        self.run_command("build_ext")
        return super().run()

    def initialize_options(self):
        super().initialize_options()
        if self.distribution.ext_modules == None:
            self.distribution.ext_modules = []

        self.distribution.ext_modules.extend(extensions)
