from unittest import TestCase
from pnb.mcl.utils import *


class Test_check_is_symbol(TestCase):

    def test_error_msg(self):
        with self.assertRaises(ValueError) as cm:
            check_is_symbol('xy z')
        self.assertEqual(
            str(cm.exception),
            r"'xy z' does not match the pattern [A-Za-z_][A-Za-z_0-9]*")

    def test_error_msg_name(self):
        with self.assertRaises(ValueError) as cm:
            check_is_symbol('xy z', 'test')
        self.assertEqual(
            str(cm.exception),
            r"test: 'xy z' does not match the pattern [A-Za-z_][A-Za-z_0-9]*")

    def test_ok(self):
        for text in ["A", "A1", "A_", "_", "_9", "_B", "__", "_F7"]:
            check_is_symbol(text)

    def test_error(self):
        for text in ["", " ", "7", "3a", "X ", " x", "ö", "a.a"]:
            self.assertRaises(ValueError, lambda text=text: check_is_symbol(text))


class Test_check_is_symbol_reference(TestCase):

    def test_error_msg(self):
        with self.assertRaises(ValueError) as cm:
            check_is_symbol_reference('x.y z')
        self.assertEqual(
            str(cm.exception),
            r"'x.y z' does not match the pattern "
                r"[A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)?")

    def test_error_msg_name(self):
        with self.assertRaises(ValueError) as cm:
            check_is_symbol_reference('x.y z', 'test')
        self.assertEqual(
            str(cm.exception),
            r"test: 'x.y z' does not match the pattern "
                r"[A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)?")

    def test_ok(self):
        for text in ["A", "A1", "A_", "_", "_9", "_B", "__", "_F7",
                     "A._", "A1.Q", "A_.z", "_._", "_9.k", "_B.kyl1",
                     "__.B3s", "_F7.L",
                     "dexpi.PositiveDisplacementPump"]:
            check_is_symbol_reference(text)

    def test_error(self):
        for text in ["", " ", "7", "3a", "X ", " x", "ö", "a.2",
                     "dexpi.Negative.DisplacementPump"]:
            self.assertRaises(
                ValueError,
                lambda text=text: check_is_symbol_reference(text))


class Test_check_is_multiple_symbol_references(TestCase):

    def test_error_msg(self):
        with self.assertRaises(ValueError) as cm:
            check_is_multiple_symbol_references(' x.yz')
        self.assertEqual(
            str(cm.exception),
            r"' x.yz' does not match the pattern "
                r"([A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)?"
                r"( [A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)?)*)?")

    def test_error_msg_name(self):
        with self.assertRaises(ValueError) as cm:
            check_is_multiple_symbol_references(' x.yz', 'test')
        self.assertEqual(
            str(cm.exception),
            r"test: ' x.yz' does not match the pattern "
                r"([A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)?"
                r"( [A-Za-z_][A-Za-z_0-9]*(\.[A-Za-z_][A-Za-z_0-9]*)?)*)?")

    def test_ok(self):
        for text in ["", "A B C", "A1 A_", "A_ _", "_ _8", "_9 A XC", "_B",
                     "__", "_F7", "A._", "A1.Q", "A_.z", "_._", "_9.k",
                     "_B.kyl1", "__.B3s", "_F7.L",
                     "mcl is amazing"]:
            check_is_multiple_symbol_references(text)

    def test_error(self):
        for text in [" "]:
            self.assertRaises(
                ValueError,
                lambda text=text: check_is_multiple_symbol_references(text))
