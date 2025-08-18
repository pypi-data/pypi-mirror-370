import itertools
import sys

import rdflib
from rdflib import Literal, RDF, BNode


class RdfExporter:

    def __init__(self, model, metamodel_namespace = 'http://www.plants-and-bytes.de/mcl/meta/'):
        
        self.model = model
        
        self.meta_model = sys.modules[model.__module__]
        self.graph = rdflib.Graph()
        self.node_by_element = {}
        self.meta_model_namespace = rdflib.Namespace(metamodel_namespace)
        self.graph.bind('meta', self.meta_model_namespace)
        self.add_element(model)

        
    def get_element_node(self, element):
        
        assert isinstance(element, self.meta_model.Element), element
        
        node = self.node_by_element.get(element)
        if node is None:
            if isinstance(element, self.meta_model.Model):
                if element.uri is None:
                    assert element.name == 'builtin'
                    uri = 'http://www.plants-and-bytes.de/mcl/builtin'
                else:
                    uri = element.uri
                node = rdflib.URIRef(uri)
                self.graph.bind(element.name, node+'/')
            elif isinstance(element, self.meta_model.Object):
                name = element.name
                if name:
                    node = rdflib.URIRef(self.get_element_node(element.model) + '/' + name) # TODO: check unique
                else:
                    model = element.model
                    assert model is self.model
                    node = BNode()
            else:
                owner = element.owner
                owner_node = self.get_element_node(owner)
                if isinstance(owner, self.meta_model.Model):
                    intro = owner_node + '/'
                else:
                    intro = owner_node + '.'
                node = rdflib.URIRef(intro + element.name)

            
            self.node_by_element[element] = node
            
        return node

    def add(self, s, p, o):
        triple = s, p, o
        if None not in triple:
            self.graph.add(triple)
            
            
    def extend(self, node, values, property_):
        
        for value in values:
            assert isinstance(value, rdflib.Node)
            self.add(node, property_, value)
            
            
    def extend_with_list(self, node, elements, property_):
        self.extend(node, elements, property_) # TODO
        
        
    def add_element(self, element):
        
        assert isinstance(element, self.meta_model.Element), element

        node = self.get_element_node(element)
        self.add(node, RDF.type, self.meta_model_namespace.term(element.get_meta_class_name()))

        if isinstance(element, self.meta_model.NamedElement):
            if element.name:
                self.add(node, self.meta_model_namespace.name, Literal(element.name))

        if isinstance(element, self.meta_model.Package):
            self.extend(node, [self.add_element(pe) for pe in element.packagedElements], self.meta_model_namespace.packagedElement)
            
        if isinstance(element, self.meta_model.Model):
            self.extend(node, [self.add_element(pe) for pe in element.packagedElements], self.meta_model_namespace.packagedElement)
            self.extend(node, [self.add_element(pe) for pe in element.unnamedObjects], self.meta_model_namespace.packagedElement)

        if isinstance(element, self.meta_model.Type):
            self.extend(node, [self.get_element_node(st) for st in element.superTypes], self.meta_model_namespace.superType)
            self.extend(node, [self.add_element(at) for at in element.ownedAttributes], self.meta_model_namespace.ownedAttribute)

        if isinstance(element, self.meta_model.Property):
            self.add(node, self.meta_model_namespace.type, self.get_element_node(element.type))
            self.add(node, self.meta_model_namespace.term('lower'), Literal(element.lower))
            if element.upper is not None:
                self.add(node, self.meta_model_namespace.term('upper'), Literal(element.upper))
            self.add(node, self.meta_model_namespace.isOrdered, Literal(element.isOrdered))
            if isinstance(
                    element, (self.meta_model.ReferenceProperty, self.meta_model.DataProperty)):
                self.add(node, self.meta_model_namespace.isUnique, Literal(element.isUnique))
            if isinstance(element, self.meta_model.ReferenceProperty):
                self.add(node, self.meta_model_namespace.term('oppositeLower'),
                    Literal(element.oppositeLower))
                if element.oppositeUpper is not None:
                    self.add(node, self.meta_model_namespace.term('oppositeUpper'),
                        Literal(element.oppositeUpper))

        if isinstance(element, self.meta_model.Enumeration):
            if 0:
             self.extend(node, [self.add_element(lit) for lit in element.packagedElements], self.meta_model_namespace.packagedElement)
             raise Exception('enums not yet supported')
             # TODO
             add_children(item.orderedOwnedLiterals)


        if isinstance(element, self.meta_model.Object):
            self.add(node, self.meta_model_namespace.type, self.get_element_node(element.type))
            
            #attributes['type'] = self.get_reference(item.type)
            for prop in element.type.attributes.values():
                values = prop._get_values_(element)
                if values:
                    if prop.isUnique and not prop.isOrdered:
                        add_values = self.extend
                    else:
                        # better choice in some cases?
                        add_values = self.extend_with_list
                    if isinstance(prop, self.meta_model.DataProperty):
                        handle_value = lambda value: self.add_data_value(prop.type, value)
                    elif isinstance(prop, self.meta_model.CompositionProperty):
                        handle_value = self.add_element # TODO: check model
                    else:
                        handle_value = self.get_element_node

                    add_values(node, [handle_value(value) for value in values], self.get_element_node(prop))

        return node

    def add_data_value(self, data_type, value):
        if isinstance(value, (bool, str, int, float)):
            return rdflib.Literal(value)

        elif isinstance(value, self.meta_model.EnumerationLiteral):
            return self.get_reference(value)
        elif isinstance(value, self.meta_model.AggregatedDataValue):
            node = rdflib.BNode()
            self.add(node, self.meta_model_namespace.type, self.get_reference(value.type))
            
            for prop in value.type.attributes:
                values = prop._get_values_(value)
                if values:
                    if prop.isUnique and not prop.isOrdered:
                        add_values = self.extend
                    else:
                        # better choice in some cases?
                        add_values = self.extend_with_list
                    
                    handle_value = lambda value: self.add_data_value(prop.type, value)

                    add_values(node, [handle_value(value) for value in values], self.get_element_node(prop))
            
            
            # TODO props
            return node
        elif isinstance(value, self.meta_model.SingletonValue):
            return self.get_reference(value)
            
            
        else:
            raise TypeError(f'{type(value)} is not yet supported ({value})')

    def get_reference(self, element):
        model, qname = element.get_model_and_qname()
        if qname is None:
            if model is not self.model:
                model, qname = element.get_model_and_qname()
                raise Exception('TODO')
            id_ = self._id_by_element.get(element)
            if id_ is None:
                try:
                    type_name = element.type.name
                except AttributeError:
                    raise # TODO
                nr = self._id_count_by_type_name.get(type_name, 0) + 1
                self._id_count_by_type_name[type_name] = nr
                id_ = f'#{type_name}{nr}'
                self._id_by_element[element] = id_
            return id_
        else:
            return rdflib.Literal(model.uri + '/' + qname)


    def get_model_reference(self, model):
        reference = self.reference_by_model.get(model)
        if reference is None:
            reference = self._find_free_prefix(model.name)
            self.reference_by_model[model] = reference
        return reference

    def _find_free_prefix(self, prefix):

        def suffixes():
            yield ''
            for nr in itertools.count():
                yield str(nr)
        for suffix in suffixes():
            candidate = prefix + suffix
            if candidate not in self.reference_by_model.values():
                return candidate

