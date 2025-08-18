from unittest import TestCase

from rdflib import Graph
from rdflib.compare import graph_diff, to_isomorphic

from pnb.mcl.metamodel import standard
from pnb.mcl.io.rdf import RdfExporter
from pnb.mcl.test.examples import ex_1

def assertGraphsEqual(test, graph_1, turtle_2):
    iso_1 = to_isomorphic(graph_1)
    iso_2 = to_isomorphic(Graph().parse(format='turtle', data=turtle_2))
    _, in_iso_1, in_iso_2 = graph_diff(iso_1, iso_2)
    message_parts = []
    if in_iso_1:
        message_parts.append(' *** only in 1 *** ')
        message_parts.extend(repr(triple) for triple in in_iso_1)
    if in_iso_2:
        message_parts.append(' *** only in 2 *** ')
        message_parts.extend(repr(triple) for triple in in_iso_2)
    if message_parts:
        test.fail('\n'.join(message_parts))


class Test_XmlExporter_ex_1(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_by_uri = ex_1.make_model_by_uri(standard)

    def test_ModelCore(self):
        exporter = RdfExporter(self.model_by_uri['http://ModelCore'])
        assertGraphsEqual(self, exporter.graph, '''
            @prefix ModelCore: <http://ModelCore/> .
            @prefix meta: <http://www.plants-and-bytes.de/mcl/meta/> .

            <http://ModelCore> a meta:Model ;
                meta:name "ModelCore" ;
                meta:packagedElement ModelCore:ConceptualModel .

            ModelCore:ConceptualModel a meta:AbstractClass ;
                meta:name "ConceptualModel" .''')

    def test_ModelProcess(self):
        exporter = RdfExporter(self.model_by_uri['http://ModelProcess'])
        assertGraphsEqual(self, exporter.graph, '''
            @prefix ModelCore: <http://ModelCore/> .
            @prefix ModelProcess: <http://ModelProcess/> .
            @prefix builtin: <http://www.plants-and-bytes.de/mcl/builtin/> .
            @prefix meta: <http://www.plants-and-bytes.de/mcl/meta/> .

            <http://ModelProcess> a meta:Model ;
                meta:name "ModelProcess" ;
                meta:packagedElement ModelProcess:Base,
                    ModelProcess:Steps .

            ModelProcess:Base a meta:Package ;
                meta:name "Base" ;
                meta:packagedElement ModelProcess:Base.ProcessStep .

            ModelProcess:Base.ProcessStep a meta:ConcreteClass ;
                meta:name "ProcessStep" ;
                meta:ownedAttribute ModelProcess:Base.ProcessStep.RelatedSteps,
                    ModelProcess:Base.ProcessStep.StepNumber,
                    ModelProcess:Base.ProcessStep.SubSteps ;
                meta:superType ModelCore:ConceptualModel .

            ModelProcess:Base.ProcessStep.RelatedSteps a meta:ReferenceProperty ;
                meta:name "RelatedSteps" ;
                meta:type ModelProcess:Base.ProcessStep ;
                meta:lower 0 ;
                meta:isOrdered false ;
                meta:isUnique true ;
                meta:oppositeLower 0 .

            ModelProcess:Base.ProcessStep.StepNumber a meta:DataProperty ;
                meta:name "StepNumber" ;
                meta:type builtin:String ;
                meta:lower 0 ;
                meta:upper 1 ;
                meta:isOrdered false ;
                meta:isUnique false .         

            ModelProcess:Base.ProcessStep.SubSteps a meta:CompositionProperty ;
                meta:name "SubSteps" ;
                meta:type ModelProcess:Base.ProcessStep ;
                meta:lower 0 ;
                meta:isOrdered false .

            ModelProcess:Steps a meta:Package ;
                meta:name "Steps" ;
                meta:packagedElement ModelProcess:Steps.Pumping .

            ModelProcess:Steps.Pumping a meta:ConcreteClass ;
                meta:name "Pumping" ;
                meta:superType ModelProcess:Base.ProcessStep .''')

    def test_ModelInstance1(self):
        exporter = RdfExporter(self.model_by_uri['http://ModelInstance1'])
        assertGraphsEqual(self, exporter.graph, '''
            @prefix ModelInstance2: <http://ModelInstance2a/> .
            @prefix ModelInstance21: <http://ModelInstance2b/> .
            @prefix ModelProcess: <http://ModelProcess/> .
            @prefix meta: <http://www.plants-and-bytes.de/mcl/meta/> .

            <http://ModelInstance1> a meta:Model ;
                meta:name "ModelInstance1" ;
                meta:packagedElement [ a meta:Object ;
                        ModelProcess:Base.ProcessStep.RelatedSteps ModelInstance2:Step1,
                            ModelInstance21:Step ;
                        ModelProcess:Base.ProcessStep.StepNumber "step1" ;
                        meta:type ModelProcess:Steps.Pumping ] .''')

    def test_ModelInstance2a(self):
        exporter = RdfExporter(self.model_by_uri['http://ModelInstance2a'])
        assertGraphsEqual(self, exporter.graph, '''
            @prefix ModelInstance2: <http://ModelInstance2a/> .
            @prefix ModelInstance3: <http://ModelInstance3/> .
            @prefix ModelProcess: <http://ModelProcess/> .
            @prefix meta: <http://www.plants-and-bytes.de/mcl/meta/> .
            
            <http://ModelInstance2a> a meta:Model ;
                meta:name "ModelInstance2" ;
                meta:packagedElement _:Pumping1,
                    ModelInstance2:Step1 .
            
            ModelInstance2:Step1 a meta:Object ;
                ModelProcess:Base.ProcessStep.RelatedSteps _:Pumping1,
                    ModelInstance3:Step ;
                ModelProcess:Base.ProcessStep.StepNumber "step2a1" ;
                meta:name "Step1" ;
                meta:type ModelProcess:Steps.Pumping .
            
            _:Pumping1 a meta:Object ;
                ModelProcess:Base.ProcessStep.StepNumber "step2a2" ;
                meta:type ModelProcess:Steps.Pumping .''')

    def test_ModelInstance2b(self):
        exporter = RdfExporter(self.model_by_uri['http://ModelInstance2b'])
        assertGraphsEqual(self, exporter.graph, '''
            @prefix ModelInstance2: <http://ModelInstance2b/> .
            @prefix ModelInstance21: <http://ModelInstance2a/> .
            @prefix ModelProcess: <http://ModelProcess/> .
            @prefix meta: <http://www.plants-and-bytes.de/mcl/meta/> .

            <http://ModelInstance2b> a meta:Model ;
                meta:name "ModelInstance2" ;
                meta:packagedElement ModelInstance2:Step .

            ModelInstance2:Step a meta:Object ;
                ModelProcess:Base.ProcessStep.RelatedSteps ModelInstance21:Step1 ;
                ModelProcess:Base.ProcessStep.StepNumber "step2b" ;
                meta:name "Step" ;
                meta:type ModelProcess:Steps.Pumping .''')

    def test_ModelInstance3(self):
        exporter = RdfExporter(self.model_by_uri['http://ModelInstance3'])
        assertGraphsEqual(self, exporter.graph, '''
            @prefix ModelInstance3: <http://ModelInstance3/> .
            @prefix ModelProcess: <http://ModelProcess/> .
            @prefix meta: <http://www.plants-and-bytes.de/mcl/meta/> .
            
            <http://ModelInstance3> a meta:Model ;
                meta:name "ModelInstance3" ;
                meta:packagedElement [ a meta:Object ;
                        ModelProcess:Base.ProcessStep.StepNumber "step31" ;
                        ModelProcess:Base.ProcessStep.SubSteps ModelInstance3:Step ;
                        meta:type ModelProcess:Steps.Pumping ] .
            
            ModelInstance3:Step a meta:Object ;
                ModelProcess:Base.ProcessStep.StepNumber "step32" ;
                meta:name "Step" ;
                meta:type ModelProcess:Steps.Pumping .''')
