from libc.stdio cimport FILE

cdef extern from "libcue.h" nogil:

    enum TrackMode:
        MODE_AUDIO
        MODE_MODE1
        MODE_MODE1_RAW
        MODE_MODE2
        MODE_MODE2_FORM1
        MODE_MODE2_FORM2
        MODE_MODE2_FORM_MIX
        MODE_MODE2_RAW

    enum TrackFlag:
        FLAG_NONE = 0x00
        FLAG_PRE_EMPHASIS = 0x01
        FLAG_COPY_PERMITTED = 0x02
        FLAG_DATA = 0x04
        FLAG_FOUR_CHANNEL = 0x08
        FLAG_SCMS = 0x10
        FLAG_ANY = 0xff

    enum Pti:
        PTI_TITLE
        PTI_PERFORMER
        PTI_SONGWRITER
        PTI_COMPOSER
        PTI_ARRANGER
        PTI_MESSAGE
        PTI_DISC_ID
        PTI_GENRE
        PTI_TOC_INFO1
        PTI_TOC_INFO2
        PTI_RESERVED1
        PTI_RESERVED2
        PTI_RESERVED3
        PTI_RESERVED4
        PTI_UPC_ISRC
        PTI_SIZE_INFO
        PTI_END

    enum RemType:
        REM_DATE
        REM_REPLAYGAIN_ALBUM_GAIN
        REM_REPLAYGAIN_ALBUM_PEAK
        REM_REPLAYGAIN_TRACK_GAIN
        REM_REPLAYGAIN_TRACK_PEAK
        REM_END

    ctypedef struct Cd:
        pass

    ctypedef struct Track:
        pass

    ctypedef struct Cdtext:
        pass

    ctypedef struct Rem:
        pass

    Cd *cue_parse_file(FILE *fp)
    Cd *cue_parse_string(const char * string)
    void cd_delete(Cd *cd)

    # CD functions
    const char *cd_get_cdtextfile(const Cd *cd)
    const char *cd_get_catalog(const Cd *cd)
    int cd_get_ntrack(const Cd *cd)

    # CDTEXT functions
    Cdtext *cd_get_cdtext(const Cd *cd)
    Cdtext *track_get_cdtext(const Track *track)
    const char *cdtext_get(Pti pti, const Cdtext *cdtext)

    # REM functions
    Rem *cd_get_rem(const Cd *cd)
    Rem *track_get_rem(const Track *track)
    const char *rem_get(unsigned int cmt, Rem *rem)

    # Track functions
    Track *cd_get_track(const Cd *cd, int i)
    const char *track_get_filename(const Track *track)
    long track_get_start(const Track *track)
    long track_get_length(const Track *track)
    TrackMode track_get_mode(const Track *track)
    int track_is_set_flag(const Track *track, TrackFlag flag)
    long track_get_zero_pre(const Track *track)
    long track_get_zero_post(const Track *track)
    const char *track_get_isrc(const Track *track)
