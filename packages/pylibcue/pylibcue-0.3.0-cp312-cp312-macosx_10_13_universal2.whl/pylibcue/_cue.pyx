# cython: language_level=3, auto_pickle=False

from cython cimport pymutex
from libc.stdio cimport fopen, fclose, FILE
from os import fsencode

from . cimport _libcue as libcue
from .mode import TrackMode

cdef dict _PTI = {
    "title": libcue.PTI_TITLE, "performer": libcue.PTI_PERFORMER,
    "songwriter": libcue.PTI_SONGWRITER, "composer": libcue.PTI_COMPOSER,
    "arranger": libcue.PTI_ARRANGER, "message": libcue.PTI_MESSAGE,
    "disc_id": libcue.PTI_DISC_ID, "genre": libcue.PTI_GENRE,
    "upc_isrc": libcue.PTI_UPC_ISRC, "size_info": libcue.PTI_SIZE_INFO,
    "toc_info": libcue.PTI_TOC_INFO1
}

cdef dict _REM = {
    "date": libcue.REM_DATE,
    "album_gain": libcue.REM_REPLAYGAIN_ALBUM_GAIN,
    "album_peak": libcue.REM_REPLAYGAIN_ALBUM_PEAK,
    "track_gain": libcue.REM_REPLAYGAIN_TRACK_GAIN,
    "track_peak": libcue.REM_REPLAYGAIN_TRACK_PEAK,
}

cdef class CDText:
    """Metadata in CD-TEXT fields."""

    cdef:
        libcue.Cdtext *_cdtext
        Cd _ref

        void _init(self, libcue.Cdtext *cdtext, Cd ref):
            if cdtext is NULL:
                raise MemoryError
            self._cdtext = cdtext
            self._ref = ref

    __slots__ = tuple(_PTI.keys())

    cdef object _getattr(self, str item):
        cdef const char *content = libcue.cdtext_get(_PTI[item], self._cdtext)
        if content is NULL:
            return None
        return content.decode(encoding=self._ref.encoding)

    def __init__(self):
        raise NotImplementedError

    def __getattr__(self, item):
        if item not in self.__slots__:
            raise AttributeError(f"Cannot extract {item} from CD-TEXT")
        return self._getattr(item)

    def _asdict(self):
        return {item: self._getattr(item) for item in self.__slots__}

cdef class Rem:
    """Metadata in REM fields."""

    cdef:
        libcue.Rem *_rem
        Cd _ref

        void _init(self, libcue.Rem *rem, Cd ref):
            if rem is NULL:
                raise MemoryError
            self._rem = rem
            self._ref = ref

    __slots__ = tuple(_REM.keys())

    cdef object _getattr(self, str item):
        cdef const char *content = libcue.rem_get(_REM[item], self._rem)
        if content is NULL:
            return None
        return content.decode(encoding=self._ref.encoding)

    def __init__(self):
        raise NotImplementedError

    def __getattr__(self, item):
        if item not in self.__slots__:
            raise AttributeError(f"Cannot extract {item} from REM fields")
        return self._getattr(item)

    def _asdict(self):
        return {item: self._getattr(item) for item in self.__slots__}

cdef pymutex _parser_lock

cdef class Cd:
    """Represents a CD described by CUE sheet.
    Its tracks are accessible via index and iteration.

    Use classmethods ``from_file`` or ``from_str`` to create instance.
    """

    cdef:
        libcue.Cd *_cd
        readonly str encoding

        void _init(self, libcue.Cd *cd, str encoding):
            if cd is NULL:
                raise MemoryError
            self._cd = cd
            self.encoding = encoding

    def __dealloc__(self):
        if self._cd is not NULL:
            libcue.cd_delete(self._cd)
            self._cd = NULL

    cdef int _get_ntrack(self) nogil:
        return libcue.cd_get_ntrack(self._cd)

    # public

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "Use classmethods (Cd.from_str and Cd.from_file) "
            "to create Cd object from CUE contents"
        )

    @classmethod
    def from_file(cls, object path, str encoding = "utf-8"):
        """Create Cd instance by parsing CUE sheet file.

        :raises IOError: If the file cannot be read
        :raises ValueError: If libcue fail to parse CUE data
        """
        cdef bytes encoded_path = fsencode(path)
        cdef const char *_path = encoded_path
        cdef FILE *fp
        cdef libcue.Cd *cd
        with nogil:
            fp = fopen(_path, "r")
            if fp is NULL:
                raise IOError("Failed to read file")
            with _parser_lock:
                cd = libcue.cue_parse_file(fp)
            fclose(fp)
        if cd is NULL:
            raise ValueError("Failed to parse cue file")

        cdef Cd obj = cls.__new__(cls)
        obj._init(cd, encoding)
        return obj

    @classmethod
    def from_str(cls, str string):
        """Create Cd instance by parsing string as CUE content.

        :raises ValueError: If libcue failed to parse CUE data
        """
        cdef bytes encoded = string.encode()
        cdef const char *content = encoded
        cdef libcue.Cd *cd
        with nogil, _parser_lock:
            cd = libcue.cue_parse_string(content)
        if cd is NULL:
            raise ValueError("Failed to parse cue string")
        cdef Cd obj = cls.__new__(cls)
        obj._init(cd, "utf-8")
        return obj

    @property
    def cdtext(self):
        """Metadata in CD-TEXT fields of CD section.

        Creates new ``CDText`` instance on each access.
        """
        cdef CDText cdtext = CDText.__new__(CDText)
        cdtext._init(libcue.cd_get_cdtext(self._cd), self)
        return cdtext

    @property
    def rem(self):
        """Metadata in REM fields of CD section.

        Creates new ``Rem`` instance on each access.
        """
        cdef Rem rem = Rem.__new__(Rem)
        rem._init(libcue.cd_get_rem(self._cd), self)
        return rem

    @property
    def cdtextfile(self):
        cdef const char *content = libcue.cd_get_cdtextfile(self._cd)
        if content is NULL:
            return None
        return content.decode(encoding=self.encoding)

    @property
    def catalog(self):
        cdef const char *content = libcue.cd_get_catalog(self._cd)
        if content is NULL:
            return None
        return content.decode(encoding=self.encoding)

    def __len__(self):
        return self._get_ntrack()

    def __getitem__(self, int index):
        if index < 0 or index >= self._get_ntrack():
            raise IndexError("Track index out of range")
        cdef Track track = Track.__new__(Track)
        track._init(libcue.cd_get_track(self._cd, index + 1), index + 1, self)
        return track

    def __contains__(self, Track track):
        cdef int i
        for i in range(self._get_ntrack()):
            if track._track == libcue.cd_get_track(self._cd, i + 1):
                return True
        return False

cdef class Track:
    """Represents a single track from CD in CUE sheet."""

    cdef:
        libcue.Track *_track
        int _index
        Cd _ref

        void _init(self, libcue.Track *track, int index, Cd ref):
            if track is NULL:
                raise MemoryError
            self._track = track
            self._index = index
            self._ref = ref

    # public

    def __init__(self):
        raise NotImplementedError

    @property
    def index(self):
        """Track index in TRACK field. (Start from 1)"""
        return self._index

    @property
    def cdtext(self):
        """Metadata in CD-TEXT fields of track section.

        Creates new ``CDText`` instance on each access.
        """
        cdef CDText cdtext = CDText.__new__(CDText)
        cdtext._init(libcue.track_get_cdtext(self._track), self._ref)
        return cdtext

    @property
    def rem(self):
        """Metadata in REM fields of track section.

        Creates new ``Rem`` instance on each access.
        """
        cdef Rem rem = Rem.__new__(Rem)
        rem._init(libcue.track_get_rem(self._track), self._ref)
        return rem

    @property
    def filename(self):
        """Filename of the audio file that contains the track."""
        cdef const char *filename = libcue.track_get_filename(self._track)
        if filename is NULL:
            return None
        return filename.decode(encoding=self._ref.encoding)

    @property
    def start(self):
        """Start time of the track (skipped pre-gap duration).

        :return: ``(minutes, seconds, frames)`` tuple,
            or ``None`` if INDEX field does not exist
        """
        cdef long start = libcue.track_get_start(self._track)
        return f2msf(start) if start >= 0 else None

    @property
    def length(self):
        """Length of current track calculated with the start time
        of the next track.

        :return: ``(minutes, seconds, frames)`` tuple,
            or ``None`` if cannot determine (e.g. last track)
        """
        cdef long length = libcue.track_get_length(self._track)
        return f2msf(length) if length >= 0 else None

    @property
    def zero_pre(self):
        """Pre-gap (silence before track) duration from PREGAP field
        or calculated with INDEX fields.

        :return: (minutes, seconds, frames) tuple
            or None if cannot determine
        """
        cdef long length = libcue.track_get_zero_pre(self._track)
        return f2msf(length) if length >= 0 else None

    @property
    def zero_post(self):
        """Post-gap duration from POSTGAP field.

        :return: (minutes, seconds, frames) tuple
            or ``None`` if field does not exist
        """
        cdef long length = libcue.track_get_zero_post(self._track)
        return f2msf(length) if length >= 0 else None

    @property
    def isrc(self):
        cdef const char *content = libcue.track_get_isrc(self._track)
        if content is NULL:
            return None
        return content.decode(encoding=self._ref.encoding)

    @property
    def mode(self):
        return TrackMode(<int> libcue.track_get_mode(self._track))

    cpdef has_flag(self, int flag):
        """Check if the track has a specific flag set in FLAGS field.

        :param flag: ``TrackFlag`` Enum to check
        """
        cdef bint ret = libcue.track_is_set_flag(self._track, <libcue.TrackFlag> flag)
        return ret

    def __and__(self, int other):
        return self.has_flag(other)

cdef tuple f2msf(const long frames):
    cdef long seconds = frames // 75
    cdef long minutes = seconds // 60
    return minutes, seconds % 60, frames % 75

def parse_file(object path, str encoding = "utf-8"):
    """Parse a CUE file and create a ``Cd`` instance.

    (alias for ``Cd.from_file``)

    :raises IOError: If the file cannot be read.
    :raises ValueError: If libcue fail to parse CUE data.
    """
    return Cd.from_file(path, encoding)

def parse_str(str string):
    """Parse a CUE string and create a ``Cd`` instance.

    (alias for ``Cd.from_str``)

    :raises ValueError: If libcue failed to parse CUE data
    """
    return Cd.from_str(string)
