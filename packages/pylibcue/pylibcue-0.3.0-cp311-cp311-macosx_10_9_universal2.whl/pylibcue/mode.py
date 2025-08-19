from enum import IntEnum, IntFlag, auto


class TrackMode(IntEnum):
    AUDIO = 0
    MODE1 = auto()
    MODE1_RAW = auto()
    MODE2 = auto()
    MODE2_FORM1 = auto()
    MODE2_FORM2 = auto()
    MODE2_FORM_MIX = auto()
    MODE2_RAW = auto()


class TrackFlag(IntFlag):
    NONE = 0x00
    PRE_EMPHASIS = 0x01
    COPY_PERMITTED = 0x02
    DATA = 0x04
    FOUR_CHANNEL = 0x08
    SCMS = 0x10
    ANY = 0xFF
