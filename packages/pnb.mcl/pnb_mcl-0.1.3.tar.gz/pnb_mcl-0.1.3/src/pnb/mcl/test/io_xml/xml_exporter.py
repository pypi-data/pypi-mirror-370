from unittest import TestCase
from lxml import etree
from pnb.mcl.metamodel import standard
from pnb.mcl.io.xml import XmlExporter
from pnb.mcl.test.examples import ex_1, ex_primitive_types

def normalize_xml_code(code):
    return ''.join(row.strip() for row in code.splitlines())

class Test_XmlExporter_ex_1(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_by_uri = ex_1.make_model_by_uri(standard)

    def test_ModelCore(self):
        exporter = XmlExporter(self.model_by_uri['http://ModelCore'])
        self.assertEqual(
            etree.tostring(exporter.xml, encoding='unicode'),
            normalize_xml_code('''
                <Model name="ModelCore" uri="http://ModelCore">
                  <AbstractClass name="ConceptualModel"/>
                </Model>'''))

    def test_ModelProcess(self):
        exporter = XmlExporter(self.model_by_uri['http://ModelProcess'])
        self.assertEqual(
            etree.tostring(exporter.xml, encoding='unicode'),
            normalize_xml_code('''
                <Model name="ModelProcess" uri="http://ModelProcess">
                  <Import source="http://ModelCore" prefix="ModelCore"/>
                  <Package name="Base">
                    <ConcreteClass name="ProcessStep" superTypes="ModelCore/ConceptualModel">
                      <ReferenceProperty name="RelatedSteps" isOrdered="false" isUnique="true" lower="0" oppositeLower="0" oppositeUpper="*" type="/Base.ProcessStep" upper="*"/>
                      <DataProperty name="StepNumber" isOrdered="false" isUnique="false" lower="0" type="builtin/String" upper="1"/>
                      <CompositionProperty name="SubSteps" isOrdered="false" lower="0" type="/Base.ProcessStep" upper="*"/>
                    </ConcreteClass>
                  </Package>
                  <Package name="Steps">
                    <ConcreteClass name="Pumping" superTypes="/Base.ProcessStep"/>
                  </Package>
                </Model>'''))

    def test_ModelInstance1(self):
        exporter = XmlExporter(self.model_by_uri['http://ModelInstance1'])
        self.assertEqual(
            etree.tostring(exporter.xml, encoding='unicode'),
            normalize_xml_code('''
                <Model name="ModelInstance1" uri="http://ModelInstance1">
                  <Import source="http://ModelInstance2b" prefix="ModelInstance20"/>
                  <Import source="http://ModelInstance2a" prefix="ModelInstance2"/>
                  <Import source="http://ModelProcess" prefix="ModelProcess"/>
                  <Object type="ModelProcess/Steps.Pumping">
                    <References refs="ModelInstance2/Step1 ModelInstance20/Step" property="RelatedSteps"/>
                    <Data property="StepNumber">
                      <String>step1</String>
                    </Data>
                  </Object>
                </Model>'''))

    def test_ModelInstance2a(self):
        exporter = XmlExporter(self.model_by_uri['http://ModelInstance2a'])
        self.assertEqual(
            etree.tostring(exporter.xml, encoding='unicode'),
            normalize_xml_code('''
                <Model name="ModelInstance2" uri="http://ModelInstance2a">
                  <Import source="http://ModelInstance3" prefix="ModelInstance3"/>
                  <Import source="http://ModelProcess" prefix="ModelProcess"/>
                  <Object name="Step1" type="ModelProcess/Steps.Pumping">
                    <References refs="#Pumping1 ModelInstance3/Step" property="RelatedSteps"/>
                    <Data property="StepNumber">
                      <String>step2a1</String>
                    </Data>
                  </Object>
                  <Object id="Pumping1" type="ModelProcess/Steps.Pumping">
                    <Data property="StepNumber">
                      <String>step2a2</String>
                    </Data>
                  </Object>
                </Model>'''))

    def test_ModelInstance2b(self):
        exporter = XmlExporter(self.model_by_uri['http://ModelInstance2b'])
        self.assertEqual(
            etree.tostring(exporter.xml, encoding='unicode'),
            normalize_xml_code('''
                <Model name="ModelInstance2" uri="http://ModelInstance2b">
                  <Import source="http://ModelInstance2a" prefix="ModelInstance2"/>
                  <Import source="http://ModelProcess" prefix="ModelProcess"/>
                  <Object name="Step" type="ModelProcess/Steps.Pumping">
                    <References refs="ModelInstance2/Step1" property="RelatedSteps"/>
                    <Data property="StepNumber">
                      <String>step2b</String>
                    </Data>
                  </Object>
                </Model>'''))

    def test_ModelInstance3(self):
        exporter = XmlExporter(self.model_by_uri['http://ModelInstance3'])
        self.assertEqual(
            etree.tostring(exporter.xml, encoding='unicode'),
            normalize_xml_code('''
                <Model name="ModelInstance3" uri="http://ModelInstance3">
                  <Import source="http://ModelProcess" prefix="ModelProcess"/>
                  <Object type="ModelProcess/Steps.Pumping">
                    <Data property="StepNumber">
                      <String>step31</String>
                    </Data>
                    <Components property="SubSteps">
                      <Object name="Step" type="ModelProcess/Steps.Pumping">
                        <Data property="StepNumber">
                          <String>step32</String>
                        </Data>
                      </Object>
                    </Components>
                  </Object>
                </Model>'''))
        

class Test_XmlExporter_ex_primitive_types(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_by_uri = ex_primitive_types.make_model_by_uri(standard)

    def test_Model(self):
        exporter = XmlExporter(self.model_by_uri['http://Model'])
        print(etree.tostring(exporter.xml, encoding='unicode', pretty_print=True))
        self.assertEqual(
            etree.tostring(exporter.xml, encoding='unicode'),
            normalize_xml_code('''
                <Model name="Model" uri="http://Model">
                  <ConcreteClass name="Class">
                    <DataProperty name="any_uri" isOrdered="false" isUnique="false" lower="1" type="builtin/AnyURI" upper="1"/>
                    <DataProperty name="boolean" isOrdered="false" isUnique="false" lower="1" type="builtin/Boolean" upper="1"/>
                    <DataProperty name="date_time" isOrdered="false" isUnique="false" lower="1" type="builtin/DateTime" upper="1"/>
                    <DataProperty name="double" isOrdered="false" isUnique="false" lower="1" type="builtin/Double" upper="1"/>
                    <DataProperty name="integer" isOrdered="false" isUnique="false" lower="1" type="builtin/Integer" upper="1"/>
                    <DataProperty name="string" isOrdered="false" isUnique="false" lower="1" type="builtin/String" upper="1"/>
                    <DataProperty name="unsigned_byte" isOrdered="false" isUnique="false" lower="1" type="builtin/UnsignedByte" upper="1"/>
                  </ConcreteClass>
                  <Object name="InstanceA" type="/Class">
                    <Data property="any_uri">
                      <String>http://www.example.org</String>
                    </Data>
                    <Data property="boolean">
                      <Boolean>false</Boolean>
                    </Data>
                    <Data property="date_time">
                      <DateTime>2020-12-07T15:32:42</DateTime>
                    </Data>
                    <Data property="double">
                      <Double>-0.3</Double>
                    </Data>
                    <Data property="integer">
                      <Integer>42</Integer>
                    </Data>
                    <Data property="string">
                      <String>Hello world!</String>
                    </Data>
                    <Data property="unsigned_byte">
                      <Integer>255</Integer>
                    </Data>
                  </Object>
                  <Object name="InstanceB" type="/Class">
                    <Data property="any_uri">
                      <String>http://www.example.org</String>
                    </Data>
                    <Data property="boolean">
                      <Boolean>true</Boolean>
                    </Data>
                    <Data property="date_time">
                      <DateTime>2020-12-07T15:32:42</DateTime>
                    </Data>
                    <Data property="double">
                      <Double>1000000.0</Double>
                    </Data>
                    <Data property="integer">
                      <Integer>-42</Integer>
                    </Data>
                    <Data property="string">
                      <String>Hello world!</String>
                    </Data>
                    <Data property="unsigned_byte">
                      <Integer>0</Integer>
                    </Data>
                  </Object>
                </Model>'''))
