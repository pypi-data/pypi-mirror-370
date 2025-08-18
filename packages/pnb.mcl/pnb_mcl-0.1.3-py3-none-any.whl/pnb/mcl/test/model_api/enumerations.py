from pnb.mcl.test.model_api import AbstractTestCase


class Test_Enumeration(AbstractTestCase):

    def test_sortings_when_sorted(self):
        e = self.Enumeration('e')
        ea = self.EnumerationLiteral('a', e)
        eb = self.EnumerationLiteral('b', e)
        self.assertEqual(
            list(e.ownedLiterals),
            [ea, eb])
        self.assertEqual(
            list(e.orderedOwnedLiterals),
            [ea, eb])

    def test_sortings_when_not_sorted(self):
        e = self.Enumeration('e')
        eb = self.EnumerationLiteral('b', e)
        ea = self.EnumerationLiteral('a', e)
        self.assertEqual(
            list(e.ownedLiterals),
            [ea, eb])
        self.assertEqual(
            list(e.orderedOwnedLiterals),
            [eb, ea])
