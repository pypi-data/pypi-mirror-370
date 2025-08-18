from os import environ
from os.path import join

from Cython.Build import cythonize
from setuptools import Extension, setup

LIBCUE_SRC = [
    "cd.c", "cdtext.c", "rem.c", "time.c",
    "cue_parser.c", "cue_scanner.c"
]

LIBCUE_PATH = environ.get("LIBCUE_PATH", join("vendor", "libcue"))
LIBCUE_QUIET_MODE = (
    environ.get("LIBCUE_QUIET_MODE", "").lower() in {"y", "yes", "1", "true", "on"}
)

extensions = [
    Extension(
        "pylibcue._cue",
        ["pylibcue/_cue.pyx", *[join(LIBCUE_PATH, i) for i in LIBCUE_SRC]],
        include_dirs=[LIBCUE_PATH],
        extra_compile_args=["-DLIBCUE_QUIET_MODE"] if LIBCUE_QUIET_MODE else None,
    )
]

setup(ext_modules=cythonize(extensions))
