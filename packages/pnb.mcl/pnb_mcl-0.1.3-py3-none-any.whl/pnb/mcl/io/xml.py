from collections import namedtuple
import itertools
import sys

from pnb.mcl.io.xmi import read_xmi
from lxml import etree

from datetime import datetime


class XmlExporter:

    def __init__(self, model, metadata=None, metadata_prefix=None, metadata_uri=None):
        self.metamodel = sys.modules[model.__module__]
        self.model = model
        
        
        self.metadata = metadata
        self.metadata_prefix = metadata_prefix
        self.metadata_uri = metadata_uri
        
        self.reference_by_model = {model: ''}
        
        self._id_by_element = {}
        self._id_count_by_type_name = {}
        self.xml_by_item = {}
        self.xml = self.item_to_xml(model)

        for element, id_ in self._id_by_element.items():
            xml = self.xml_by_item[element]
            assert 'id' not in xml.attrib
            assert 'name' not in xml.attrib
            attributes = {'id': id_[1:]}
            attributes.update(xml.attrib)
            xml.attrib.clear()
            xml.attrib.update(attributes)

        for ref_model, prefix in self.reference_by_model.items():
            if ref_model in (model, self.metamodel.BUILTIN):
                continue
            self.xml.insert(0, etree.Element(
                'Import',
                source=ref_model.uri,
                prefix=prefix))
            
            
    def type_expression_to_xml(self, type_expression):
        if isinstance(type_expression, (self.metamodel.Type, self.metamodel.TypeParameter)):
            return etree.Element(
                'ClassReference' if isinstance(type_expression, self.metamodel.ClassExpression) else 'DataTypeReference',
                {'type': self.get_reference(type_expression)})
        elif isinstance(type_expression, self.metamodel.BoundType):
            xml = etree.Element(type_expression.get_meta_class_name())
            xml.append(self.type_expression_to_xml(type_expression.base))
            for binding in type_expression.bindings:

                if isinstance(binding, self.metamodel.DataTypeTemplateParameterBinding):
                    binding_name = 'DataTypeBinding'
                else:
                    assert isinstance(binding, self.metamodel.ClassTemplateParameterBinding)
                    binding_name = 'ClassBinding'
                
                
                
                binding_xml = etree.SubElement(xml, binding_name)
                binding_xml.attrib['parameter'] = self.get_reference(binding.parameter)
                binding_xml.append(self.type_expression_to_xml(binding.type))
            return xml
        elif isinstance(type_expression, self.metamodel.UnionType):
            xml = etree.Element(type_expression.get_meta_class_name())
            for base in type_expression.bases:
                xml.append(self.type_expression_to_xml(base))
            return xml
        else:
            raise TypeError(type_expression)


    def item_to_xml(self, item):
        attributes = {}
        children = []


        def add_children(members):
            children.extend(self.item_to_xml(member) for member in members)

        if isinstance(item, self.metamodel.NamedElement):
            attributes['name'] = item.name
        if isinstance(item, self.metamodel.Model):
            attributes['uri'] = item.uri
            add_children(item.packagedElements)
            add_children(item.unnamedObjects)
        if isinstance(item, self.metamodel.Package):
            add_children(item.packagedElements)
        if isinstance(item, self.metamodel.Type):
            if item.superTypes:
                st_string = ' '.join(self.get_reference(type_) for type_ in item.superTypes)
                attributes['superTypes'] = st_string
            add_children(getattr(item, 'ownedParameters', []))
            add_children(item.ownedAttributes)
        if isinstance(item, self.metamodel.ClassExtension):
            attributes['baseType'] = self.get_reference(item.baseType)
            add_children(item.ownedParameters)
            add_children(item.ownedAttributes)

        if isinstance(item, self.metamodel.TypeParameter):
            children.append(self.type_expression_to_xml(item.type))
    
        if isinstance(item, self.metamodel.Property):
            children.append(self.type_expression_to_xml(item.type))
            attributes['lower'] = str(item.lower)
            if item.upper is not None:
                attributes['upper'] = str(item.upper)
            attributes['isOrdered'] = 'true' if item.isOrdered else 'false'
            if not item.get_meta_class_name() == 'CompositionProperty':
                attributes['isUnique'] = 'true' if item.isUnique else 'false'
            if item.get_meta_class_name() == 'ReferenceProperty':
                attributes['oppositeLower'] = str(item.oppositeLower)
                if item.oppositeUpper is not None:
                    attributes['oppositeUpper'] = str(item.oppositeUpper)
        if isinstance(item, self.metamodel.Enumeration):
            add_children(item.orderedOwnedLiterals)
            
            
        if isinstance(item, self.metamodel.SingletonValue):
            attributes['type'] = self.get_reference(item.type)


        if isinstance(item, self.metamodel.Object):
            attributes['type'] = self.get_reference(item.type)
            for prop in item.type.attributes.values():
                values = prop._get_values_(item)
                if values:
                    match prop.get_meta_class_name():
                        case 'CompositionProperty':
                            child = etree.Element('Components')
                            child.extend(self.item_to_xml(value) for value in values)
                        case 'ReferenceProperty':
                            child = etree.Element('References')
                            child.attrib['objects'] = ' '.join(
                                self.get_reference(value) for value in values)
                        case 'DataProperty':
                            child = etree.Element('Data')
                            child.extend(self.data_to_xml(value) for value in values)
                        case _:
                            continue
                        
                    child.attrib['property'] = prop.name
                    children.append(child)
      
        sorted_attributes = {}
        if name:= attributes.pop('name', None):
            sorted_attributes['name'] = name
        if id_:= attributes.pop('id', None):
            sorted_attributes['id'] = id_
        sorted_attributes.update(sorted(attributes.items()))

        xml = etree.Element(
            item.get_meta_class_name(),
            sorted_attributes)
        xml.extend(children)
        
        self.xml_by_item[item] = xml
        
        if self.metadata:
            assert self.metadata_prefix
            assert self.metadata_uri
            element_data = self.metadata.for_element(item)
            
            for name, value in element_data.items():
                
                # TODO
                if not isinstance(value, (str, bool)):
                    continue
                
                #assert isinstance(value, (str, bool)), value
                
                
                meta_child = etree.SubElement(xml, 'Data')
                meta_child.attrib['property'] = f'{self.metadata_prefix}/{name}'
                
                if isinstance(value, str):
                    etree.SubElement(meta_child, 'String').text = value
                elif isinstance(value, bool):
                    etree.SubElement(meta_child, 'Boolean').text = str(value).lower()
                


        return xml
    
    
    def data_to_xml(self, value):
        attrs = {}
        children = []
        if isinstance(value, str):
            tag = 'String'
            text = value
        elif isinstance(value, self.metamodel.EnumerationLiteral):
            tag = 'DataReference'
            text = None
            attrs = {'data': self.get_reference(value)}
        elif isinstance(value, self.metamodel.SingletonValue):
            tag = 'DataReference'
            text = None
            attrs = {'data': self.get_reference(value)}
        elif isinstance(value, bool):
            tag = 'Boolean'
            text = str(value).lower()
        elif isinstance(value, int):
            # Keep this after bool!!!
            tag = 'Integer'
            text = str(value)
        elif isinstance(value, float):
            tag = 'Double'
            text = str(value)
        elif isinstance(value, datetime):
            tag = 'DateTime'
            text = value.isoformat()
        elif isinstance(value, self.metamodel.AggregatedDataValue):
            if 0 and TODO and value.type.name == 'Point':
                tag = 'Point2D'
                text = f'{value.X},{value.Y}'
            else:
                tag = 'AggregatedDataValue'
                attrs = {'type': self.get_reference(value.type)}
                for prop in value.type.attributes:
                    values = prop._get_values_(value)
                    if not values:
                        continue  
                    child = etree.Element('Data')
                    children.append(child)
                    child.extend(self.data_to_xml(value) for value in values)
                    child.attrib['property'] = prop.name
                text = None
        elif type(value) is object:
            tag = 'Undefined'
            text = None
        else:
            raise TypeError(value)
        
        xml = etree.Element(tag, attrs)
        xml.extend(children)
        xml.text = text
        return xml

    def get_reference(self, element):
        model, qname = element.get_model_and_qname()
        if qname is None:
            if model is not self.model:
                model, qname = element.get_model_and_qname()
                raise Exception('TODO', element, model, qname)
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
            return f'{self.get_model_reference(model)}/{qname}'

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


ModelInfo = namedtuple('ModelInfo', ['uri', 'xml_element', 'import_uris_by_prefix'])
ObjectInfo = namedtuple('ObjectInfo', ['built_object', 'xml_element'])
TypeInfo = namedtuple('TypeInfo', ['global_id', 'global_super_type_ids', 'xml_element'])
# separator symbols
ID_SEP_SYMBOL = '#'
SUB_ELEMENT_SEP_SYMBOL = '.'
URI_SEP_SYMBOL = '/'
# all types except PrimitiveTypes which are builtin mcl types
ALL_TYPES = ['AbstractClass', 'ConcreteClass',
             'AbstractDataType', 'AggregatedDataType', 'SingletonType',
             'Enumeration', 'StringType', 'BooleanType', 'DateTimeType', 'DoubleType', 'IntegerType']

def sorted_by_dependency(type_infos):
    """Iterate over type_infos such that each type_info precedes its sub types."""
    handled_global_ids = set()
    while type_infos:
        infos_to_handle = {}
        progress_made = False
        for global_id, info in type_infos.items():
            if info.global_super_type_ids.issubset(handled_global_ids):
                progress_made = True
                handled_global_ids.add(global_id)
                yield info
            else:
                infos_to_handle[global_id] = info
        assert progress_made, 'no progress made (missing ids? cycle?)'
        type_infos = infos_to_handle

class XmlImporter:
    """
    loader: callable with one arg (uri) that returns the XML root element corresponding to
        the model with the given uri
    """

    def __init__(self, loader, uris, metamodel=None):
        if not metamodel:
            from pnb.mcl.metamodel import standard as metamodel

        self.metamodel = metamodel
        self.model_info_by_uri = {}
        self.model_by_uri = {}
        self.type_info_by_global_id = {}

        self.built_type_by_global_id = {}
        self.built_object_infos = []
        self.built_object_by_global_id = {}
        
        if isinstance(uris, str):
            self.uris_to_handle = {uris}
        else:
            self.uris_to_handle = set(uris)
            

        # import all xml models
        while self.uris_to_handle:
            uri = self.uris_to_handle.pop()
            assert uri not in self.model_info_by_uri
            self.model_info_by_uri[uri] = self._get_model_infos(loader, uri)

        # generate type infos from all xml models
        for model_info in self.model_info_by_uri.values():
            self._generate_type_infos(model_info.xml_element)

        # build mcl types from sorted type infos
        sorted_type_infos = list(sorted_by_dependency(self.type_info_by_global_id))
        for info in sorted_type_infos:
            self._build_type(info)

        # build mcl properties for types
        for global_id, type_info in self.type_info_by_global_id.items():
            self._build_type_properties(global_id, type_info.xml_element)

        # for each xml model: build mcl model with all sub packages and packaged elements
        for model_info in self.model_info_by_uri.values():
            model = self._build_package(model_info.xml_element)
            self.model_by_uri[model.uri] = model

        # build mcl properties for objects
        for object_info in self.built_object_infos:
            self._build_object_properties(
                object_info.built_object, object_info.xml_element)
            
        if isinstance(uris, str):

            self.model = self.model_by_uri[uris]

    def _get_model_infos(self, loader, uri):
        xml_element = loader(uri)
        import_uris_by_prefix = {}

        for xml_import in xml_element.iterchildren('Import'):
            import_uri = xml_import.attrib.get('source')
            assert import_uri != uri
            if import_uri not in self.model_info_by_uri:
                self.uris_to_handle.add(import_uri)
            import_prefix = xml_import.attrib.get('prefix')
            assert import_prefix is not None, xml_import
            assert import_prefix not in import_uris_by_prefix
            import_uris_by_prefix[import_prefix] = import_uri

        return ModelInfo(uri, xml_element, import_uris_by_prefix)

    def _get_global_item_ids(self, xml_element, xml_attribute):
        global_item_ids = []
        item_ids_str = xml_element.attrib.get(xml_attribute)
        if item_ids_str is not None:
            item_ids = item_ids_str.split()
        else:
            return set()

        xml_parent = xml_element.getparent()
        while xml_parent.tag != 'Model':
            xml_parent = xml_parent.getparent()
        xml_model_uri = xml_parent.attrib.get('uri')

        for item_id in item_ids:
            if item_id.startswith('builtin'):
                global_item_ids.append(item_id)
                continue
            if item_id.startswith(URI_SEP_SYMBOL):
                global_item_id = xml_model_uri + item_id
            elif item_id.startswith(ID_SEP_SYMBOL):
                global_item_id = xml_model_uri + URI_SEP_SYMBOL + item_id[1:]
            else:
                prefix = item_id.split(URI_SEP_SYMBOL)[0]
                xml_model_info = self.model_info_by_uri[xml_model_uri]
                import_uri = xml_model_info.import_uris_by_prefix[prefix]
                suffix = item_id[len(prefix):]
                global_item_id = import_uri + suffix

            global_item_ids.append(global_item_id)

        return global_item_ids

    def _get_xml_id_and_sep_symbol(self, xml_element, parent_id):
        xml_id = xml_element.attrib.get('name')
        sep_symbol = SUB_ELEMENT_SEP_SYMBOL
        if xml_id is None:
            xml_id = xml_element.attrib.get('id')
        if parent_id is not None and parent_id[-1] == URI_SEP_SYMBOL:
            sep_symbol = ''
        return xml_id, sep_symbol

    def _get_converted_data_values(self, xml_data_element):
        converted_values = []
        for child_element in xml_data_element:
            value_str = child_element.text
            match child_element.tag:
                case 'String':
                    converted_values.append(value_str)
                case 'Boolean':
                    assert value_str in {'false', 'true'}
                    if value_str == 'false':
                        converted_values.append(False)
                    else:
                        converted_values.append(True)
                case 'Double':
                    converted_values.append(float(value_str))
                case 'Integer':
                    converted_values.append(int(value_str))
                case 'DateTime':
                    # fromisoformat should work adequately for python >= 3.11
                    converted_values.append(datetime.fromisoformat(value_str))

        return converted_values

    def _generate_type_infos(self, xml_element, parent_id=None):
        xml_id, sep_symbol = self._get_xml_id_and_sep_symbol(xml_element, parent_id)

        match xml_element.tag:
            case 'Model':
                uri = xml_element.attrib.get('uri')
                assert uri is not None
                assert xml_id is not None
                for child_element in xml_element.iterchildren():
                    self._generate_type_infos(child_element, uri + URI_SEP_SYMBOL)
            case 'Package':
                assert xml_id is not None
                for child_element in xml_element.iterchildren():
                    self._generate_type_infos(
                        child_element,
                        parent_id + sep_symbol + xml_id)
            case 'Import':
                return
            case 'Object':
                return
            case _:
                assert xml_element.tag in ALL_TYPES, xml_element.tag
                global_id = parent_id + sep_symbol + xml_id
                assert global_id not in self.type_info_by_global_id
                assert xml_id is not None
                super_type_xml_ids = self._get_global_item_ids(xml_element, 'superTypes')
                self.type_info_by_global_id[global_id] = TypeInfo(
                    global_id, set(super_type_xml_ids), xml_element)

    def _build_type(self, type_info):
        xml_element = type_info.xml_element
        xml_tag = xml_element.tag
        name = xml_element.attrib['name']
        super_types = [self.built_type_by_global_id[id] for id in type_info.global_super_type_ids]

        assert xml_tag in ALL_TYPES
        meta_type = getattr(self.metamodel, xml_tag)

        assert type_info.global_id not in self.built_type_by_global_id
        self.built_type_by_global_id[type_info.global_id] = meta_type(name, super_types)

        return

    def _build_type_properties(self, global_id, xml_element):
        for xml_prop in xml_element:
            
            if xml_prop.tag not in ('CompositionProperty', 'DataProperty', 'ReferenceProperty'):
                continue
            
            name = xml_prop.attrib.get('name')
            is_ordered_str = xml_prop.attrib.get('isOrdered')
            if is_ordered_str == 'false':
                is_ordered = False
            else:
                is_ordered = True
            print(xml_prop)
            lower = int(xml_prop.attrib.get('lower'))
            global_type_id = self._get_global_item_ids(xml_prop, 'type').pop()
            if global_type_id.startswith('builtin'):
                type_ = getattr(self.metamodel, global_type_id[len('builtin')+1:])
            else:
                type_ = self.built_type_by_global_id[global_type_id]
            upper_str = xml_prop.attrib.get('upper')
            if upper_str is None:
                upper = None
            else:
                upper = int(upper_str)

            match xml_prop.tag:
                case 'CompositionProperty':
                    self.built_type_by_global_id[global_id].ownedAttributes.add(
                        self.metamodel.CompositionProperty(
                            name, type_, lower, upper, is_ordered))
                case 'DataProperty':
                    is_unique_str = xml_prop.attrib.get('isUnique')
                    if is_unique_str == 'false':
                        is_unique = False
                    else:
                        is_unique = True
                    self.built_type_by_global_id[global_id].ownedAttributes.add(
                        self.metamodel.DataProperty(
                            name, type_, lower, upper, is_ordered, is_unique))
                case 'ReferenceProperty':
                    is_unique_str = xml_prop.attrib.get('isUnique')
                    if is_unique_str == 'false':
                        is_unique = False
                    else:
                        is_unique = True
                    opp_lower = int(xml_prop.attrib.get('oppositeLower'))
                    opp_upper_str = xml_prop.attrib.get('oppositeUpper')
                    if opp_upper_str is None:
                        opp_upper = None
                    else:
                        opp_upper = int(opp_upper_str)
                    self.built_type_by_global_id[global_id].ownedAttributes.add(
                        self.metamodel.ReferenceProperty(
                            name, type_, lower, upper, is_ordered, is_unique,
                            opp_lower, opp_upper))
        return

    def _build_object(self, xml_element, parent_id):
        # build mcl object with all sub objects
        global_type_id = self._get_global_item_ids(xml_element, 'type').pop()
        type_ = self.built_type_by_global_id[global_type_id]
        name = xml_element.attrib.get('name')

        object_ = self.metamodel.Object(type_, name)
        object_info = ObjectInfo(object_, xml_element)
        self.built_object_infos.append(object_info)

        # check whether object has id for referencing
        xml_id, sep_symbol = self._get_xml_id_and_sep_symbol(xml_element, parent_id)
        if xml_id is not None:
            global_object_id = parent_id + sep_symbol + xml_id
            self.built_object_by_global_id[global_object_id] = object_
            child_parent_id = global_object_id
        else:
            child_parent_id = parent_id

        # check for sub objects
        for child_element in xml_element:
            if child_element.tag == 'Components':
                # composition property
                prop_name = child_element.attrib.get('property')
                prop = type_.attributes.get(prop_name)
                assert isinstance(prop, self.metamodel.CompositionProperty), prop
                values = []
                for sub_element in child_element:
                    assert sub_element.tag == 'Object'
                    values.append(self._build_object(sub_element, child_parent_id))
                prop._set_values_(object_, values)
            else:
                # data and reference properties
                pass

        return object_

    def _build_object_properties(self, built_object, xml_element):
        global_type_id = self._get_global_item_ids(xml_element, 'type').pop()
        type_ = self.built_type_by_global_id[global_type_id]
        for child_element in xml_element:
            match child_element.tag:
                case 'Components':
                    # sub objects already built
                    pass
                case 'Data':
                    prop_name = child_element.attrib.get('property')
                    prop = type_.attributes.get(prop_name)
                    assert isinstance(prop, self.metamodel.DataProperty), prop
                    values = self._get_converted_data_values(child_element)
                    prop._set_values_(built_object, values)
                case 'References':
                    prop_name = child_element.attrib.get('property')
                    prop = type_.attributes.get(prop_name)
                    assert isinstance(prop, self.metamodel.ReferenceProperty), prop
                    values = []
                    global_object_ids = self._get_global_item_ids(child_element, 'refs')
                    for global_object_id in global_object_ids:
                        values.append(self.built_object_by_global_id[global_object_id])
                    prop._set_values_(built_object, values)
                case _:
                    raise TypeError(child_element)

        return

    def _build_package(self, xml_package_element, parent_id=None):
        # build mcl package with all sub packages and all packaged elements
        # use already built mcl types
        name = xml_package_element.attrib.get('name')
        xml_tag = xml_package_element.tag

        if xml_tag == 'Model':
            uri = xml_package_element.attrib.get('uri')
            package = self.metamodel.Model(name, uri)
            assert parent_id is None
            parent_id = uri + URI_SEP_SYMBOL
        else:
            assert xml_tag == 'Package'
            package = self.metamodel.Package(name)

        for child_element in xml_package_element:
            match child_element.tag:
                case 'Package':
                    xml_id, sep_symbol = self._get_xml_id_and_sep_symbol(child_element, parent_id)
                    sub_package = self._build_package(
                        child_element,
                        parent_id + sep_symbol + xml_id)
                    package.packagedElements.add(sub_package)
                case type_ if type_ in ALL_TYPES:
                    xml_id, sep_symbol = self._get_xml_id_and_sep_symbol(child_element, parent_id)
                    global_id = parent_id + sep_symbol + xml_id
                    built_type = self.built_type_by_global_id[global_id]
                    package.packagedElements.add(built_type)
                case 'Object':
                    object_ = self._build_object(child_element, parent_id)
                    package.add(object_)
                case _:
                    assert child_element.tag == 'Import'
                    continue

        return package

def read_xml(path, uri):
    reader = XmlImporter(path, uri)
    return reader.model


def read_xmls(xml_paths):
    
    xml_root_by_uri = {}
    for path in xml_paths:
        xml_root = etree.parse(path).getroot()
        uris = xml_root.xpath('/Model/@uri')
        assert len(uris) == 1, uris
        uri = uris[0]
        assert uri not in xml_root_by_uri
        xml_root_by_uri[uri] = xml_root
        
    importer = XmlImporter(xml_root_by_uri.get, xml_root_by_uri)

    model_by_name = {}
    for model in importer.model_by_uri.values():
        assert model.name not in model_by_name
        model_by_name[model.name] = model

    return model_by_name

