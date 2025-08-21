from unittest import TestCase

from lofar_parameterset.parameterset import parameterset


class TestParameterSet(TestCase):
    def test_construction(self):
        p = parameterset({"foo": "bar"})

        self.assertIn("foo", p)
        self.assertEqual(p["foo"], "bar")

    def test_fromString(self):
        PARSET = """
        foo = bar
        a.b.c = 3
        """

        p = parameterset.fromString(PARSET)

        self.assertIn("foo", p)
        self.assertEqual(p["foo"], "bar")
        self.assertIn("a.b.c", p)
        self.assertIn(p["a.b.c"], "3")

    def test_str(self):
        p = parameterset({"foo": "bar", "a.b.c": 3})
        self.assertEqual("\n".join(["a.b.c=3", 'foo="bar"']), str(p))

    def test_str_quoted(self):
        p = parameterset({"single_quote": "'single'", "double_quote": '"double"'})
        self.assertEqual(
            "\n".join(["double_quote='\"double\"'", "single_quote=\"'single'\""]),
            str(p),
        )

    def test_makeSubset(self):
        PARSET = """
        one.a = 1
        one.b = 2
        two.a = 3
        two.b = 4
        two.c.d = 5
        """

        p = parameterset.fromString(PARSET)
        subset = p.makeSubset("one.")

        self.assertDictEqual({"a": "1", "b": "2"}, subset)

    def test_fullModuleName(self):
        p = parameterset({"a.b.c.d": "xxxx"})

        self.assertEqual("a.b.c.d", p.fullModuleName("d"))
        self.assertEqual("a.b.c", p.fullModuleName("b.c"))
        self.assertEqual("", p.fullModuleName("d.param"))

    def test_getString(self):
        p = parameterset({"foo": "bar"})

        self.assertEqual("bar", p.getString("foo"))
        self.assertEqual("baz", p.getString("foo2", "baz"))

        with self.assertRaises(KeyError):
            _ = p.getString("baz")

    def test_getIntVector(self):
        PARSET = """
        key=[1, 2, 3, 4]
        """

        p = parameterset.fromString(PARSET)

        self.assertListEqual([1, 2, 3, 4], p.getIntVector("key"))

    def test_getStringVector(self):
        PARSET = """
        quoted=['Xre','Xim','Yre','Yim']
        unquoted=[Xre, Xim, Yre, Yim]
        """

        p = parameterset.fromString(PARSET)

        self.assertListEqual(["Xre", "Xim", "Yre", "Yim"], p.getStringVector("quoted"))
        self.assertListEqual(
            ["Xre", "Xim", "Yre", "Yim"], p.getStringVector("unquoted")
        )
