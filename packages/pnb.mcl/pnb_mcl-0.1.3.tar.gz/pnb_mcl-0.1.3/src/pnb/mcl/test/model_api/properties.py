from pnb.mcl.test.model_api import AbstractTestCase

class Test_CompositionProperty(AbstractTestCase):

    def test_init(self):
        city = self.ConcreteClass('City')
        cities = self.CompositionProperty('cities', city, 0, 5, False)
        self.assertEqual(cities.name, 'cities')
        self.assertEqual(cities.lower, 0)
        self.assertEqual(cities.upper, 5)
        self.assertIs(cities.type, city)
        self.assertFalse(cities.isOrdered)
        self.assertTrue(cities.isUnique)
        self.assertEqual(cities.oppositeLower, 0)
        self.assertEqual(cities.oppositeUpper, 1)


class Test_ReferenceProperty(AbstractTestCase):

    def test_init(self):
        city = self.ConcreteClass('City')
        cities = self.ReferenceProperty(
            'cities', city, 0, 5, False, True, 3, 7)
        self.assertEqual(cities.name, 'cities')
        self.assertEqual(cities.lower, 0)
        self.assertEqual(cities.upper, 5)
        self.assertIs(cities.type, city)
        self.assertFalse(cities.isOrdered)
        self.assertTrue(cities.isUnique)
        self.assertEqual(cities.oppositeLower, 3)
        self.assertEqual(cities.oppositeUpper, 7)

    def test_owner(self):
        city = self.ConcreteClass('City')
        cities = self.ReferenceProperty(
            'cities', 0, 5, city, False, True, 3, 7)
        self.assertIsNone(cities.owner)

    def test_owner_after_add(self):
        city = self.ConcreteClass('City')
        cities = self.ReferenceProperty(
            'cities', 0, 5, city, False, True, 3, 7)
        city.ownedAttributes.add(cities)
        self.assertIs(cities.owner, city)

    def _test_upper_greater_equal_lower(self):
        # TODO
        city = self.ConcreteClass('City')
        self.ReferenceProperty('cities', 5, 5, city, False, True, 3, 7)
        self.ReferenceProperty('cities', 10, None, city, False, True, 3, 7)
        self.assertRaisesRegex(
            ValueError,
            'mimi',
            lambda:
                self.ReferenceProperty('cities', 5, 4, city, False, True, 3, 7))

        
        
        
        


