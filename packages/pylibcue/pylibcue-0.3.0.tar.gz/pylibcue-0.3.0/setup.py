from os import environ
from os.path import join

from Cython.Build import cythonize
from setuptools import Extension, setup

LIBCUE_SRC = [
    "cd.c", "cdtext.c", "rem.c", "time.c",
    "cue_parser.c", "cue_scanner.c"
]

LIBCUE_PATH = environ.get("LIBCUE_PATH", join("vendor", "libcue"))

extensions = [
    Extension(
        "pylibcue._cue",
        ["pylibcue/_cue.pyx", *[join(LIBCUE_PATH, i) for i in LIBCUE_SRC]],
        include_dirs=[LIBCUE_PATH],
        extra_compile_args=["-DLIBCUE_QUIET_MODE"],
    )
]

setup(ext_modules=cythonize(extensions))
