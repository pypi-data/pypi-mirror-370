import unittest
from pathlib import Path

import pylibcue

TEST_DATA = Path(__file__).parent / "testdata"


class TestCue(unittest.TestCase):

    def test_minimal(self):
        cd = pylibcue.Cd.from_file(TEST_DATA / "minimal.cue")
        self.assertEqual(len(cd), 2)
        self.assertIsNotNone(cd.cdtext)
        self.assertIsNotNone(cd.rem)
        self.assertIsNone(cd.cdtext.title)
        self.assertEqual(cd[1].start, (4, 10, 59))
        self.assertIsNotNone(cd[1].cdtext)
        self.assertIsNotNone(cd[1].rem)
        self.assertIsNone(cd[1].cdtext.title)

    def test_example(self):
        cd = pylibcue.Cd.from_file(TEST_DATA / "example.cue")
        self.assertEqual(cd.catalog, "4549767191621")
        self.assertEqual(cd.cdtext.performer, "サンドリオン")
        self.assertEqual(cd.cdtext.title, "天体図")
        self.assertEqual(len(cd), 4)
        self.assertEqual(len(cd.cdtext._asdict()), 11)
        self.assertEqual(len(cd.rem._asdict()), 5)
        self.assertEqual(list(cd.cdtext._asdict().values()).count(None), 11 - 2)

        for i in cd:
            self.assertEqual(i.filename, "COCC-18150.wav")
            self.assertIs(i.mode, pylibcue.TrackMode.AUDIO)
            self.assertEqual(i.cdtext.performer, "サンドリオン")

        track_01 = cd[0]
        self.assertEqual(track_01.index, 1)
        self.assertEqual(track_01.cdtext.title, "天体図")
        self.assertEqual(track_01.isrc, "JPCO02329890")
        self.assertEqual(track_01.start, (0, 0, 0))
        self.assertEqual(track_01.length, (4, 8, 50))
        self.assertEqual(track_01.zero_pre, None)
        self.assertTrue(track_01 in cd)

        track_02 = cd[1]
        self.assertEqual(track_02.index, 2)
        self.assertEqual(track_02.cdtext.title, "ゆびきりの唄")
        self.assertEqual(track_02.isrc, "JPCO02329840")
        self.assertEqual(track_02.start, (4, 10, 59))
        self.assertEqual(track_02.length, (4, 4, 32))
        self.assertEqual(track_02.zero_pre, (0, 2, 9))
        self.assertTrue(track_02 in cd)

        track_04 = cd[3]
        self.assertEqual(track_04.index, 4)
        self.assertEqual(track_04.cdtext.title, "ゆびきりの唄 (off vocal ver.)")
        self.assertEqual(track_04.isrc, "JPCO02329849")
        self.assertEqual(track_04.start, (12, 27, 43))
        self.assertIs(track_04.length, None)
        self.assertEqual(track_04.zero_pre, (0, 2, 18))
        self.assertTrue(track_04 in cd)

    def test_more(self):
        cd = pylibcue.Cd.from_file(TEST_DATA / "more.cue")
        self.assertEqual(cd.cdtext.songwriter, "Songwriter0")
        self.assertEqual(cd.cdtext.composer, "Composer0")
        self.assertEqual(cd.cdtext.arranger, "Arranger0")
        self.assertEqual(cd.cdtext.message, "message0")
        self.assertEqual(cd.cdtext.disc_id, "1234ABCD")
        self.assertEqual(cd.cdtext.upc_isrc, "1234567890")
        self.assertEqual(cd.cdtext.genre, "Genre0")
        self.assertEqual(cd.rem.date, "2023")
        self.assertEqual(cd.cdtextfile, "cdtext0.cdt")
        self.assertEqual(cd[0].zero_pre, (0, 1, 0))
        self.assertEqual(cd[0].zero_post, (0, 1, 0))
        self.assertTrue(cd[0] & pylibcue.TrackFlag.COPY_PERMITTED)
        self.assertTrue(cd[0] & pylibcue.TrackFlag.FOUR_CHANNEL)
        self.assertFalse(cd[0] & pylibcue.TrackFlag.NONE)


class TestParsing(unittest.TestCase):

    def test_from_str(self):
        with open(TEST_DATA / "example.cue", "r", encoding='utf-8') as f:
            content = f.read()
        cd = pylibcue.Cd.from_str(content)
        self.assertEqual(cd.cdtext.title, "天体図")
        self.assertEqual(len(cd), 4)

    def test_encoding(self):
        cd = pylibcue.Cd.from_file(TEST_DATA / "example.jis.cue", encoding='shift-jis')
        self.assertEqual(cd.encoding, 'shift-jis')
        self.assertEqual(cd.cdtext.title, "天体図")
        self.assertEqual(cd[0].cdtext.title, "天体図")

    def test_error_unreadable(self):
        with self.assertRaises(IOError) as e:
            _ = pylibcue.Cd.from_file("not_exist.cue")
        self.assertEqual(str(e.exception), "Failed to read file")

    def test_error_parse(self):
        with self.assertRaises(ValueError) as e:
            _ = pylibcue.Cd.from_str("123456")
        self.assertEqual(str(e.exception), "Failed to parse cue string")


if __name__ == "__main__":
    unittest.main()
