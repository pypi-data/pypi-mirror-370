import abc
import inspect
import pathlib
from unittest import SkipTest, TestCase, TestSuite

THIS_DIR = pathlib.Path(__file__).parent

class AbstractTestCase(TestCase):

    _is_abstract = True

    @classmethod
    def setUpClass(cls):
        if cls._is_abstract:
            raise SkipTest(f'{cls} is an abstract base class')
        super().setUpClass()
        model = cls.get_model()
        cls.CompositionProperty = model.CompositionProperty
        cls.ConcreteClass = model.ConcreteClass
        cls.Enumeration = model.Enumeration
        cls.EnumerationLiteral = model.EnumerationLiteral
        cls.Members = model.Members
        cls.MutableMembers = model.MutableMembers
        cls.Namespace = model.Namespace
        cls.ReferenceProperty = model.ReferenceProperty
        cls.Package = model.Package

    @classmethod
    @abc.abstractmethod
    def get_model(cls):
        ...


def find_abstract_test_classes(suite):
    return [cls for cls in set(iter_test_classes(suite))
            if issubclass(cls, AbstractTestCase) and cls._is_abstract]

def iter_test_classes(suite):
    for test in suite._tests:
        if isinstance(test, TestSuite):
            yield from iter_test_classes(test)
        elif isinstance(test, TestCase):
            yield type(test)
        else:
            raise TypeError(test)


def get_suite(loader, model):
    # TODO
    # - better way to find abstract test classes
    #   (loader.discover creates instances!) -> check private methods of loader
    # - pattern from call???
    api_suite = loader.discover(str(THIS_DIR), pattern='*.py')
    suite = TestSuite()
    for cls in find_abstract_test_classes(api_suite):
        ConreteTest = type(
            f'{cls.__name__}_{model.__name__.rsplit(".", 1)[-1]}',
            (cls, ),
            dict(_is_abstract=False, get_model=classmethod(lambda cls: model)))
        suite.addTests(loader.loadTestsFromTestCase(ConreteTest))
    return suite


def load_suite(model):
    def load_tests(loader, tests, pattern):
        return get_suite(loader, model)
    return load_tests
