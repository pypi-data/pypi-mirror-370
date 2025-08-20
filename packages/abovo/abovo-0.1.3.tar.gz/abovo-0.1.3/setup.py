from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import os
import glob
import platform
import sys

sources = ["pybind/bindings.cpp"] + glob.glob("src/nn/*.cpp") + glob.glob("src/nn/activation/*.cpp") + glob.glob("src/nn/loss/*.cpp") + glob.glob("src/nn/matmul/*.cpp") + glob.glob("src/nn/quantization/*.cpp")

extra_compile_args = ["-std=c++17"]
extra_link_args = []
define_macros = []

on_rtd = os.environ.get('READTHEDOCS') == 'True'

if not on_rtd:
    if platform.system() == "Darwin":
        extra_compile_args.append("-arch")
        if platform.machine() == 'arm64':
            extra_compile_args.append("arm64")
        else:
            extra_compile_args.append("x86_64")

# ARM detection
is_arm = platform.machine() == 'arm64'
if is_arm:
    if platform.system() == "Darwin":  # macOS ARM
        define_macros.append(('USE_ARM_NEON', '1'))
    elif platform.system() == "Linux" and not on_rtd:  # Linux ARM, not on RTD
        define_macros.append(('USE_ARM_NEON', '1'))
        extra_compile_args.append("-mfloat-abi=hard")
else:
    # disable NEON for x86
    define_macros.append(('NO_ARM_NEON', '1'))

# OpenMP settings
if platform.system() == "Darwin":  # macOS
    # Homebrew paths
    homebrew_prefix = "/opt/homebrew" if os.path.exists("/opt/homebrew") else "/usr/local"
    libomp_path = os.path.join(homebrew_prefix, "opt/libomp")
    
    if os.path.exists(libomp_path):
        # add OpenMP support
        extra_compile_args.extend(["-Xpreprocessor", "-fopenmp", f"-I{libomp_path}/include"])
        extra_link_args.extend([f"-L{libomp_path}/lib", "-lomp"])
    else:
        # disable OpenMP if libomp not available
        define_macros.append(('NO_OPENMP', '1'))
elif platform.system() == "Linux" and not on_rtd:  # Linux, not on RTD
    extra_compile_args.append("-fopenmp")
    extra_link_args.append("-fopenmp")
elif platform.system() == "Windows":  # Windows
    extra_compile_args = ["/std:c++17", "/openmp"]
    extra_link_args = []

# dummy extension for RTD
if on_rtd:
    class DummyExtension(Extension):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        
    class DummyBuildExt(build_ext):
        def build_extension(self, ext):
            pass
    
    abovo_ext = DummyExtension("_abovo", sources=[])
    build_cmd = DummyBuildExt
else:
    # for normal builds, use the real extension
    abovo_ext = Pybind11Extension(
        "_abovo",
        sources=sources,
        include_dirs=["include"],
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args
    )
    build_cmd = build_ext

setup(
    name="abovo",
    version="0.1.3",
    description="A C++ neural network engine with Python bindings, designed for educational performance optimization.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    ext_modules=[abovo_ext],
    cmdclass={"build_ext": build_cmd},
    zip_safe=False,
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=["abovo"],
    include_package_data=True,
    extras_require={
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme',
            'sphinx_autodoc_typehints',
        ],
    },
)