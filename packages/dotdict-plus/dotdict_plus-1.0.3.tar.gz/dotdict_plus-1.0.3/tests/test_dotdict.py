import unittest

from dotdict import DotDict


class TestDotDict(unittest.TestCase):

    def test_dotdict(self):
        data = {
            "a": {
                "b": 1,
                "c": 2
            },
            "c": 3,
            "d c": 4,
            "_e": 5
        }
        d = DotDict(data)
        self.assertEqual(d.a.b, 1)
        self.assertEqual(d["a"]["b"], 1)
        self.assertEqual(d.a["b"], 1)
        self.assertEqual(d.c, 3)
        self.assertEqual(d["c"], 3)
        self.assertEqual(d["d c"], 4)
        with self.assertRaises(AttributeError):  # _e不能直接通过.访问, 但可以通过[]访问
            d._e
