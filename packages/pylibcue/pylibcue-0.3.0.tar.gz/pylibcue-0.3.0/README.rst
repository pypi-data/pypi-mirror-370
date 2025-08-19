pylibcue
========

pylibcue is a CUE sheet parser library for python. It provides fast and reliable
CUE sheets parsing interfaces for python by wrapping `libcue
<https://github.com/lipnitsk/libcue>`_ C library with Cython.

*Note:* since v0.2.1, pylibcue uses libcue fork with custom patches (`Cycloctane/libcue
<https://github.com/Cycloctane/libcue>`_) instead of original libcue to provide
additional bugfixes and features.

Install
-------

.. code-block:: bash

    pip install pylibcue

Compile from source
^^^^^^^^^^^^^^^^^^^

Requirements: bison, flex, make.

Clone the repo with ``--recurse-submodules`` argument.

.. code-block:: bash

    pip install --upgrade setuptools Cython build
    make test
    make

Usage
-----

Create a CD instance by parsing a CUE sheet file or string:

.. code-block:: python

    import pylibcue

    cd = pylibcue.parse_file("./example.cue")
    # cd = pylibcue.parse_str("...")

Extract CD metadata and iterate through tracks in CD:

.. code-block:: python

    print("Title:", cd.cdtext.title)
    print("Artist:", cd.cdtext.performer)
    print("Date:", cd.rem.date)
    print("Tracks:")

    for tr in cd:
        print(f"TRACK{tr.index:02d}: {tr.cdtext.title} - {tr.cdtext.performer}")

License
-------

pylibcue is licensed under the GNU General Public License v2.0.
