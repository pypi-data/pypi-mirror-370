from unittest import TestCase
from lxml import etree
from pnb.mcl.metamodel import standard
from pnb.mcl.io.xml import XmlExporter, XmlImporter
from pnb.mcl.test.examples import ex_1, ex_primitive_types



def _test_importer(test_case, uri):
    messages = []
    importer = XmlImporter(test_case.xml_loader, uri)
    for model in importer.model_by_uri.values():
        reexported_xml_code = etree.tostring(
            XmlExporter(model).xml, encoding='unicode', pretty_print=True)
        expected_xml_code = etree.tostring(
            test_case.xml_by_uri[model.uri], encoding='unicode', pretty_print=True)
        if reexported_xml_code != expected_xml_code:
            messages += [
                f'-------- {model.uri} --------\n\n--- reexported ---\n',
                reexported_xml_code,
                '--- expected ---\n',
                expected_xml_code]
    if messages:
        print(f'\n\n########## {test_case} ##########\n')
        print('\n'.join(messages))
        test_case.fail()


class Test_XmlImporter_ex_1(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_by_uri = ex_1.make_model_by_uri(standard)
        cls.xml_by_uri = {uri: XmlExporter(model).xml for uri, model in cls.model_by_uri.items()}
        cls.xml_loader = staticmethod(lambda uri: cls.xml_by_uri[uri])

    def test_ModelCore(self):
        _test_importer(self, 'http://ModelCore')

    def test_ModelProcess(self):
        _test_importer(self, 'http://ModelProcess')

    def test_ModelInstance1(self):
        _test_importer(self, 'http://ModelInstance1')

    def test_ModelInstance2a(self):
        _test_importer(self, 'http://ModelInstance2a')

    def test_ModelInstance2b(self):
        _test_importer(self, 'http://ModelInstance2b')

    def test_ModelInstance3(self):
        _test_importer(self, 'http://ModelInstance3')


class Test_XmlImporter_ex_primitive_types(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_by_uri = ex_primitive_types.make_model_by_uri(standard)
        cls.xml_by_uri = {uri: XmlExporter(model).xml for uri, model in cls.model_by_uri.items()}
        cls.xml_loader = staticmethod(lambda uri: cls.xml_by_uri[uri])

    def test_Model(self):
        _test_importer(self, 'http://Model')
