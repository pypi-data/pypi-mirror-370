from warnings import warn
import weakref

from pnb.mcl.test.model_api import AbstractTestCase


class Test_Members(AbstractTestCase):
    """
    Tests for direct instances of Members, which are always derived.
    
    Some tests may seem trivial or redundant. They are included to cover
    different cases w.r.t. the internal update mechanism of a model
    implementation. 
    """

    def test_private_init(self):
        self.assertRaisesRegex(
            TypeError,
            "A Members object cannot be created from user code.",
            lambda: self.Members(self.Package(name='spam'), self.Namespace.members))

    def test_identity(self):
        p = self.Package('p')
        self.assertIs(
            p.ownedMembers,
            p.ownedMembers)

    def test_gc(self):
        # Works in Python 3.12. May fail in other implementations with different
        # behavior of garbage collector,
        p = self.Package('p')
        owned_members_ref = weakref.ref(p.ownedMembers)
        self.assertIsNone(owned_members_ref())

    def test_info(self):
        self.assertEqual(
            self.Package('p').ownedMembers.info,
            "Namespace.ownedMembers of Package 'p'")

    def test_repr(self):
        self.assertEqual(
            repr(self.Package('p').ownedMembers),
            "<Namespace.ownedMembers of Package 'p'>")

    def test_contains_empty(self):
        p = self.Package('p')
        self.assertNotIn('c', p.ownedMembers)
        self.assertNotIn(self.ConcreteClass('c'), p.ownedMembers)

    def test_add_contains(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertIn('c', p.ownedMembers)
        self.assertIn(c, p.ownedMembers)
        self.assertNotIn('d', p.ownedMembers)
        self.assertNotIn(self.ConcreteClass('c'), p.ownedMembers)

    def test_add_add_contains(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c1'))
        p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIn('c1', p.ownedMembers)
        self.assertIn('c2', p.ownedMembers)
        self.assertNotIn('c', p.ownedMembers)
        self.assertNotIn(self.ConcreteClass('c'), p.ownedMembers)

    def test_add_contains_add_contains(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIn('c2', p.ownedMembers)
        self.assertIn(c2, p.ownedMembers)
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertIn('c1', p.ownedMembers)
        self.assertIn(c1, p.ownedMembers)
        self.assertIn('c2', p.ownedMembers)
        self.assertIn(c2, p.ownedMembers)

    def test_getattr_empty(self):
        p = self.Package('p')
        self.assertRaisesRegex(
            AttributeError,
            "Namespace.ownedMembers of Package 'p' has no attribute 'c'.",
            lambda: p.ownedMembers.c)

    def test_add_getattr(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertRaisesRegex(
            AttributeError,
            "Namespace.ownedMembers of Package 'p' has no attribute 'd'.",
            lambda: p.ownedMembers.d)
        self.assertIs(
            p.ownedMembers.c,
            c)

    def test_add_add_getattr(self):
        p = self.Package('p')
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertRaisesRegex(
            AttributeError,
            "Namespace.ownedMembers of Package 'p' has no attribute 'd'.",
            lambda: p.ownedMembers.d)
        self.assertIs(
            p.ownedMembers.c1,
            c1)
        self.assertIs(
            p.ownedMembers.c2,
            c2)

    def test_add_getattr_add_getattr(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIs(
            p.ownedMembers.c2,
            c2)
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertIs(
            p.ownedMembers.c1,
            c1)
        self.assertIs(
            p.ownedMembers.c2,
            c2)

    def test_iter_empty(self):
        p = self.Package('p')
        self.assertEqual(
            list(p.ownedMembers),
            [])

    def test_add_iter(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertEqual(
            list(p.ownedMembers),
            [c])

    def test_add_add_iter(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            list(p.ownedMembers),
            [c1, c2])

    def test_add_iter_add_iter(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertEqual(
            list(p.ownedMembers),
            [c2])
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            list(p.ownedMembers),
            [c1, c2])

    def test_error_changed_on_iter(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c1'))
        with self.assertRaisesRegex(
                RuntimeError,
                'dictionary changed size during iteration'):
            for _ in p.ownedMembers:
                p.packagedElements.add(self.ConcreteClass('c2'))

    def test_len_empty(self):
        p = self.Package('p')
        self.assertEqual(
            len(p.ownedMembers),
            0)

    def test_add_len(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c'))
        self.assertEqual(
            len(p.ownedMembers),
            1)

    def test_add_add_len(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c2'))
        p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            len(p.ownedMembers),
            2)

    def test_add_len_add_len(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertEqual(
            len(p.ownedMembers),
            1)
        p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            len(p.ownedMembers),
            2)

    def test_at_empty(self):
        p = self.Package('p')
        self.assertRaisesRegex(
            KeyError,
            "Namespace.ownedMembers of Package 'p' has no member named 'c'.",
            lambda: p.ownedMembers.at('c'))

    def test_add_at(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertRaisesRegex(
            KeyError,
            "Namespace.ownedMembers of Package 'p' has no member named 'd'.",
            lambda: p.ownedMembers.at('d'))
        self.assertIs(
            p.ownedMembers.at('c'),
            c)

    def test_add_add_at(self):
        p = self.Package('p')
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertRaisesRegex(
            KeyError,
            "Namespace.ownedMembers of Package 'p' has no member named 'd'.",
            lambda: p.ownedMembers.at('d'))
        self.assertIs(
            p.ownedMembers.at('c1'),
            c1)
        self.assertIs(
            p.ownedMembers.at('c2'),
            c2)

    def test_add_at_add_at(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIs(
            p.ownedMembers.at('c2'),
            c2)
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertIs(
            p.ownedMembers.at('c1'),
            c1)
        self.assertIs(
            p.ownedMembers.at('c2'),
            c2)

    def test_get_empty(self):
        p = self.Package('p')
        self.assertIsNone(p.ownedMembers.get('c'))
        self.assertIs(
            p.ownedMembers.get('c', self),
            self)

    def test_add_get(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertIsNone(p.ownedMembers.get('d'))
        self.assertIs(
            p.ownedMembers.get('c'),
            c)

    def test_add_add_get(self):
        p = self.Package('p')
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIsNone(p.ownedMembers.get('d'))
        self.assertIs(
            p.ownedMembers.get('c1'),
            c1)
        self.assertIs(
            p.ownedMembers.get('c2'),
            c2)

    def test_add_get_add_get(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIs(
            p.ownedMembers.get('c2'),
            c2)
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertIs(
            p.ownedMembers.get('c1'),
            c1)
        self.assertIs(
            p.ownedMembers.get('c2'),
            c2)

    def test_names_empty(self):
        p = self.Package('p')
        self.assertEqual(
            list(p.ownedMembers.names),
            [])

    def test_add_names(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c'))
        self.assertEqual(
            list(p.ownedMembers.names),
            ['c'])

    def test_add_add_names(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c2'))
        p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            list(p.ownedMembers.names),
            ['c1', 'c2'])

    def test_add_names_add_names(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertEqual(
            list(p.ownedMembers.names),
            ['c2'])
        p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            list(p.ownedMembers.names),
            ['c1', 'c2'])

    def test_error_changed_on_names(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c1'))
        with self.assertRaisesRegex(
                RuntimeError,
                'dictionary changed size during iteration'):
            for _ in p.ownedMembers.names:
                p.packagedElements.add(self.ConcreteClass('c2'))


class Test_MutableMembers(AbstractTestCase):
    """
    Tests for direct instances of MutableMembers, which are never derived.
    
    Some tests may seem trivial or redundant. They are included to cover
    different cases w.r.t. the internal update mechanism of a model
    implementation. 
    """

    def test_private_init(self):
        self.assertRaisesRegex(
            TypeError,
            "A MutableMembers object cannot be created from user code.",
            lambda: self.MutableMembers(self.Package(name='spam'), self.Namespace.members))

    def test_identity(self):
        p = self.Package('p')
        self.assertIs(
            p.packagedElements,
            p.packagedElements)

    def test_gc(self):
        # Works in Python 3.12. May fail in other implementations with other
        # different behavior of garbage collector,
        p = self.Package('p')
        owned_members_ref = weakref.ref(p.ownedMembers)
        self.assertIsNone(owned_members_ref())

    def test_info(self):
        self.assertEqual(
            self.Package('p').packagedElements.info,
            "Package.packagedElements of Package 'p'")

    def test_repr(self):
        self.assertEqual(
            repr(self.Package('p').packagedElements),
            "<Package.packagedElements of Package 'p'>")

    def test_add(self):
        p = self.Package('p')
        c = self.ConcreteClass('c')
        self.assertIs(
            p.packagedElements.add(c),
            c)
        self.assertEqual(
            list(p.packagedElements),
            [c])
        self.assertIs(
            c.owner,
            p)

    def test_add_twice(self):
        p = self.Package('p')
        c = self.ConcreteClass('c')
        self.assertIs(
            p.packagedElements.add(c),
            c)
        self.assertIs(
            p.packagedElements.add(c),
            c)
        self.assertEqual(
            list(p.packagedElements),
            [c])

    def test_error_add_wrong_type(self):
        p = self.Package('p')
        c = self.ConcreteClass('c')
        cp = self.CompositionProperty('cp', 1, 1, c, True)
        with self.assertRaises(TypeError) as cm:
            p.packagedElements.add(cp)
        self.assertEqual(
            str(cm.exception),
            "<CompositionProperty 'cp'> cannot be added to <Package.packagedElements of Package "
                "'p'> because it is not a <PackageableElement>.")

    def test_error_add_name_in_same_property(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c'))
        self.assertRaisesRegex(
            TypeError,
            "<ConcreteClass 'c'> cannot be added to <Package.packagedElements "
            "of Package 'p'> because <Package.packagedElements of Package 'p'> "
            "already contains a member with this name.",
            lambda: p.packagedElements.add(self.ConcreteClass('c')))

    def _test_error_add_name_in_members(self):
        TODO

    def test_error_add_other_owner(self):
        p1 = self.Package('p1')
        c = p1.packagedElements.add(self.ConcreteClass('c'))
        p2 = self.Package('p2')
        self.assertRaisesRegex(
            TypeError,
            "<ConcreteClass 'p1.c'> is already owned by <Package 'p1'> and cannot "
                "be added to <Package.packagedElements of Package 'p2'>.",
            lambda: p2.packagedElements.add(c))

    def test_error_add_other_property(self):
        warn("TODO")

    def test_contains_empty(self):
        p = self.Package('p')
        self.assertNotIn('c', p.packagedElements)
        self.assertNotIn(self.ConcreteClass('c'), p.packagedElements)

    def test_add_contains(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertIn('c', p.packagedElements)
        self.assertIn(c, p.packagedElements)
        self.assertNotIn('d', p.packagedElements)
        self.assertNotIn(self.ConcreteClass('c'), p.packagedElements)

    def test_add_add_contains(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c1'))
        p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIn('c1', p.packagedElements)
        self.assertIn('c2', p.packagedElements)
        self.assertNotIn('c', p.packagedElements)
        self.assertNotIn(self.ConcreteClass('c'), p.packagedElements)

    def test_add_contains_add_contains(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIn('c2', p.packagedElements)
        self.assertIn(c2, p.packagedElements)
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertIn('c1', p.packagedElements)
        self.assertIn(c1, p.packagedElements)
        self.assertIn('c2', p.packagedElements)
        self.assertIn(c2, p.packagedElements)

    def test_getattr_empty(self):
        p = self.Package('p')
        self.assertRaisesRegex(
            AttributeError,
            "Package.packagedElements of Package 'p' has no attribute 'c'.",
            lambda: p.packagedElements.c)

    def test_add_getattr(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertRaisesRegex(
            AttributeError,
            "Package.packagedElements of Package 'p' has no attribute 'd'.",
            lambda: p.packagedElements.d)
        self.assertIs(
            p.packagedElements.c,
            c)

    def test_add_add_getattr(self):
        p = self.Package('p')
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertRaisesRegex(
            AttributeError,
            "Package.packagedElements of Package 'p' has no attribute 'd'.",
            lambda: p.packagedElements.d)
        self.assertIs(
            p.packagedElements.c1,
            c1)
        self.assertIs(
            p.packagedElements.c2,
            c2)

    def test_add_getattr_add_getattr(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIs(
            p.packagedElements.c2,
            c2)
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertIs(
            p.packagedElements.c1,
            c1)
        self.assertIs(
            p.packagedElements.c2,
            c2)

    def test_iter_empty(self):
        p = self.Package('p')
        self.assertEqual(
            list(p.packagedElements),
            [])

    def test_add_iter(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertEqual(
            list(p.packagedElements),
            [c])

    def test_add_add_iter(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            list(p.packagedElements),
            [c1, c2])

    def test_add_iter_add_iter(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertEqual(
            list(p.packagedElements),
            [c2])
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            list(p.packagedElements),
            [c1, c2])

    def test_error_changed_on_iter(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c1'))
        with self.assertRaisesRegex(
                RuntimeError,
                'dictionary changed size during iteration'):
            for _ in p.packagedElements:
                p.packagedElements.add(self.ConcreteClass('c2'))

    def test_len_empty(self):
        p = self.Package('p')
        self.assertEqual(
            len(p.packagedElements),
            0)

    def test_add_len(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c'))
        self.assertEqual(
            len(p.packagedElements),
            1)

    def test_add_add_len(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c2'))
        p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            len(p.packagedElements),
            2)

    def test_add_len_add_len(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertEqual(
            len(p.packagedElements),
            1)
        p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            len(p.packagedElements),
            2)

    def test_at_empty(self):
        p = self.Package('p')
        self.assertRaisesRegex(
            KeyError,
            "Package.packagedElements of Package 'p' has no member named 'c'.",
            lambda: p.packagedElements.at('c'))

    def test_add_at(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertRaisesRegex(
            KeyError,
            "Package.packagedElements of Package 'p' has no member named 'd'.",
            lambda: p.packagedElements.at('d'))
        self.assertIs(
            p.packagedElements.at('c'),
            c)

    def test_add_add_at(self):
        p = self.Package('p')
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertRaisesRegex(
            KeyError,
            "Package.packagedElements of Package 'p' has no member named 'd'.",
            lambda: p.packagedElements.at('d'))
        self.assertIs(
            p.packagedElements.at('c1'),
            c1)
        self.assertIs(
            p.packagedElements.at('c2'),
            c2)

    def test_add_at_add_at(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIs(
            p.packagedElements.at('c2'),
            c2)
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertIs(
            p.packagedElements.at('c1'),
            c1)
        self.assertIs(
            p.packagedElements.at('c2'),
            c2)

    def test_get_empty(self):
        p = self.Package('p')
        self.assertIsNone(p.packagedElements.get('c'))
        self.assertIs(
            p.packagedElements.get('c', self),
            self)

    def test_add_get(self):
        p = self.Package('p')
        c = p.packagedElements.add(self.ConcreteClass('c'))
        self.assertIsNone(p.packagedElements.get('d'))
        self.assertIs(
            p.packagedElements.get('c'),
            c)

    def test_add_add_get(self):
        p = self.Package('p')
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIsNone(p.packagedElements.get('d'))
        self.assertIs(
            p.packagedElements.get('c1'),
            c1)
        self.assertIs(
            p.packagedElements.get('c2'),
            c2)

    def test_add_get_add_get(self):
        p = self.Package('p')
        c2 = p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertIs(
            p.packagedElements.get('c2'),
            c2)
        c1 = p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertIs(
            p.packagedElements.get('c1'),
            c1)
        self.assertIs(
            p.packagedElements.get('c2'),
            c2)

    def test_names_empty(self):
        p = self.Package('p')
        self.assertEqual(
            list(p.packagedElements.names),
            [])

    def test_add_names(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c'))
        self.assertEqual(
            list(p.packagedElements.names),
            ['c'])

    def test_add_add_names(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c2'))
        p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            list(p.packagedElements.names),
            ['c1', 'c2'])

    def test_add_names_add_names(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c2'))
        self.assertEqual(
            list(p.packagedElements.names),
            ['c2'])
        p.packagedElements.add(self.ConcreteClass('c1'))
        self.assertEqual(
            list(p.packagedElements.names),
            ['c1', 'c2'])

    def test_error_changed_on_names(self):
        p = self.Package('p')
        p.packagedElements.add(self.ConcreteClass('c1'))
        with self.assertRaisesRegex(
                RuntimeError,
                'dictionary changed size during iteration'):
            for _ in p.packagedElements.names:
                p.packagedElements.add(self.ConcreteClass('c2'))
