from collections import namedtuple
from lxml import etree

from pnb.mcl.utils import SYMBOL_PATTERN, check_is_symbol




class XmlNamespace(str):
    def __getattr__(self, fragment):
        return f'{{{self}}}{fragment}'

XMI = XmlNamespace('http://schema.omg.org/spec/XMI/2.1')
NAMESPACES = {'xmi': XMI}



TypeInfo = namedtuple('TypeInfo', ['xmi_id', 'super_type_xmi_ids', 'xmi_element'])
ObjectInfo = namedtuple('ObjectInfo', ['xmi_id', 'xmi_element'])


def sorted_by_dependency(type_infos):
    """Iterate over type_infos such that each type_info precedes its sub types."""
    handled_xmi_ids = set()
    while type_infos:
        infos_to_handle = []
        progress_made = False
        for info in type_infos:
            if info.super_type_xmi_ids.issubset(handled_xmi_ids):
                progress_made = True
                handled_xmi_ids.add(info.xmi_id)
                yield info
            else:
                infos_to_handle.append(info)
        assert progress_made, 'no progress made (missing ids? cycle?)'
        type_infos = infos_to_handle


class XmiReader:
    
    def __init__(self, source, meta_model=None, check_primitive_generalizations=False):
        self.check_primitive_generalizations = check_primitive_generalizations
        if not meta_model:
            from pnb.mcl.metamodel import standard as meta_model
        self.meta_model = meta_model
        
        
        self.model_element_by_xmi_id = {}
        self.item_by_xmi_id = {}
        
        root = source[0]
        
        self._build_packaged_elements(root)

        
        
        
      
        
        self.package = self._build_package(source[0], self.meta_model.Model)
        
        self.type_info_by_id = {}
        

        
    def _get_type_infos(self, root_element):
        type_infos = []
        for xmi_element_tag in ['Class', 'DataType', 'Enumeration', 'PrimitiveType']:
            for xmi_element in root_element.xpath(
                    f'//*[@xmi:type="uml:{xmi_element_tag}"]', namespaces=NAMESPACES):
                xmi_id = xmi_element.attrib[XMI.id]
                super_type_xmi_ids = set(xmi_element.xpath(
                    f'generalization[@xmi:type="uml:Generalization"]/@general',
                    namespaces=NAMESPACES))
                type_infos.append(TypeInfo(xmi_id, super_type_xmi_ids, xmi_element))
                
                
        if self.check_primitive_generalizations:
            info_by_name = {info.xmi_element.attrib['name']: info for info in type_infos}

            
            for info in type_infos:
                if info.xmi_element.attrib[XMI.type] == 'uml:PrimitiveType':
                    name = info.xmi_element.attrib['name']
                    super_type_name = 'Nullable' + name
                    if super_type_name in info_by_name:
                        super_type_xmi_id = info_by_name[super_type_name].xmi_id
                        info.super_type_xmi_ids.add(super_type_xmi_id)
                      #  print("--- Add nullable supertype to ", name)
                     #   print(info_by_name['String'])

                    else:
                        
                        pass
                       # print("--- No nullable supertype for ", name)

  
        return list(sorted_by_dependency(type_infos))
    
    
      
    def _build_type(self, type_info):
        
        xmi_element = type_info.xmi_element
        xmi_type = xmi_element.attrib[XMI.type]
        name = xmi_element.attrib['name']
        is_abstract = xmi_element.get('isAbstract') == 'true'
        super_types = [self.item_by_xmi_id[xmi_id] for xmi_id in type_info.super_type_xmi_ids]

        match xmi_type:
            case 'uml:Class':
                if is_abstract:
                    meta_type = self.meta_model.AbstractClass
                else:
                    meta_type = self.meta_model.ConcreteClass
            case 'uml:DataType':
                if xmi_element.xpath('ownedAttribute'):
                    assert not is_abstract
                    meta_type = self.meta_model.AggregatedDataType
                else:
                    if is_abstract:
                        meta_type = self.meta_model.AbstractDataType
                    else:
                        # TODO: check instances element.xpath('//packagedElement[classifier="{type_id}"]')
                        meta_type = self.meta_model.SingletonType
            case 'uml:PrimitiveType':
                
                prim_prefix = 'Primitive'
                if name.startswith(prim_prefix):
                    name = name[len(prim_prefix):]

                
                if 1: # BUILTIN_PRIMS
                    
                    
                    type_name = name+'Type'
                    
                    type_name = {
                        'AnyURIType': 'StringType',
                        'IntegerType': 'IntegerType',
                        'UnsignedByteType': 'IntegerType'}.get(type_name, type_name)
                    
                    meta_type = getattr(self.meta_model, type_name)
                    
                    
                    
                    
                else:
                
                
                
                    # TODO: super types of primitives -> Union

                    if name == 'Integer':
                        name = 'Int'
                    type_ = getattr(self.meta_model, name)
                    self.item_by_xmi_id[type_info.xmi_id] = type_
                    return
            case 'uml:Enumeration':
                meta_type = self.meta_model.Enumeration
            case _:
                raise Exception(xmi_type)

            
        assert type_info.xmi_id not in self.item_by_xmi_id
        self.item_by_xmi_id[type_info.xmi_id] = meta_type(name, super_types)
        

        return
            
            
        type_ = type_class(name, (self.model_element_by_id[id_] for id_ in superType_ids))
        if type_id in self.model_element_by_id:
            ERROR
        self.model_element_by_id[type_id] = type_
        
        
        

        
        
    def _build_packaged_elements(self, root_element):

        type_infos = self._get_type_infos(root_element)
        for info in type_infos:
            self._build_type(info)
        

        opp_prop_by_prop_id = {}
        for association_element in root_element.xpath(f'//*[@xmi:type="uml:Association"]', namespaces=NAMESPACES):
            prop_ids = association_element.attrib['memberEnd'].split()
            props = association_element.xpath(f'*[@xmi:type="uml:Property"]', namespaces=NAMESPACES)
            assert len(props) == 1
            assert props[0].attrib[XMI.id] == prop_ids[1]
            opp_prop_by_prop_id[prop_ids[0]] = props[0]

        for info in type_infos:
            type_id, superType_ids, type_element = info

            
            for oa in type_element:

                if oa.tag != 'ownedAttribute':
                    continue
                
                prop_type_id = oa.attrib.get('type')
                if not prop_type_id:
                    continue # TODO, e.g. untyped value of CustomAttr
                
                type_ = self.item_by_xmi_id.get(oa.attrib['type'])
                if not type_:
                    continue # TODO
                

                aggregation = oa.attrib.get('aggregation')
                assert aggregation in ('none', 'composite', None)
                if not aggregation:
                    aggregation = 'none'
                    
                
                
                if aggregation == 'composite':
                    assert isinstance(type_, self.meta_model.Class)
                    
                    
                    name = oa.attrib['name']
                    
                    
                    isOrdered = oa.attrib.get('isOrdered')
                    
                    
                    if isOrdered is None:
                        isOrdered=False
                    elif isOrdered == 'true':
                        isOrdered = True
                    else:
                        raise Exception(isOrdered)
                    
                    lowerElements = oa.xpath('lowerValue')
                    if lowerElements:
                        assert len(lowerElements) == 1
                        lowerElement = lowerElements[0]
                        lower = lowerElement.attrib.get('value')
                        if lower is None:
                            lower = 0
                        else:
                            raise Exception(lower)
                    else:
                        lower = 1
                        
                    upperElements = oa.xpath('upperValue')
                    if upperElements:
                        assert len(upperElements) == 1
                        upperElement = upperElements[0]
                        upper = upperElement.attrib.get('value')
                        if upper is None:
                            raise Exception(upper)
                        elif upper == '*':
                            upper = None
                        else:
                            raise Exception(upper)
                        
                        
                    else:
                        upper = 1
                    
               #     print(name, lower, upper, type)
                    
                    
                    self.item_by_xmi_id[type_id].ownedAttributes.add(
                        self.meta_model.CompositionProperty(name, type_, lower, upper, isOrdered))
                    
                elif isinstance(type_, self.meta_model.Class):
                    

                    name = oa.attrib['name']
                    
                    
                    isOrdered = oa.attrib.get('isOrdered')
                    
                    if isOrdered is None:
                        isOrdered=False
                    elif isOrdered == 'true':
                        isOrdered = True
                    else:
                        raise Exception(isOrdered)
                    
                    
                    isUnique = oa.attrib.get('isUnique')
                    
                    if isUnique is None:
                        isUnique=False
                    elif isUnique == 'true':
                        isUnique = True
                    else:
                        raise Exception(isUnique)
                    
                    lowerElements = oa.xpath('lowerValue')
                    if lowerElements:
                        assert len(lowerElements) == 1
                        lowerElement = lowerElements[0]
                        lower = lowerElement.attrib.get('value')
                        if lower is None:
                            lower = 0
                        else:
                            raise Exception(lower)
                    else:
                        lower = 1

                    upperElements = oa.xpath('upperValue')
                    if upperElements:
                        assert len(upperElements) == 1
                        upperElement = upperElements[0]
                        upper = upperElement.attrib.get('value')
                        if upper is None:
                            raise Exception(upper)
                        elif upper == '*':
                            upper = None
                        else:
                            raise Exception(upper)
                    else:
                        upper = 1
                        
                    opp_propElement = opp_prop_by_prop_id[oa.attrib[XMI.id]]
                    oppLowerElements = opp_propElement.xpath('lowerValue')
                    if oppLowerElements:
                        assert len(oppLowerElements) == 1
                        oppLowerElement = oppLowerElements[0]
                        oppLower = oppLowerElement.attrib.get('value')
                        if oppLower is None:
                            oppLower = 0
                        else:
                            oppLower = int(oppLower)
                    else:
                        oppLower = 1
                        
                    oppUpperElements = opp_propElement.xpath('upperValue')
                    if oppUpperElements:
                        assert len(oppUpperElements) == 1
                        oppUpperElement = oppUpperElements[0]
                        oppUpper = oppUpperElement.attrib.get('value')
                        if oppUpper is None:
                            raise Exception(oppUpper)
                        elif oppUpper == '*':
                            oppUpper = None
                        else:
                            oppUpper = int(oppUpper)
                    else:
                        oppUpper = 1
                        

                    self.item_by_xmi_id[type_id].ownedAttributes.add(
                        self.meta_model.ReferenceProperty(name, type_, lower, upper, isOrdered, isUnique, oppLower, oppUpper))
         
                else:

                    name = oa.attrib['name']
                    
                    
                    isOrdered = oa.attrib.get('isOrdered')
                    
                    if isOrdered is None:
                        isOrdered=False
                    elif isOrdered == 'true':
                        isOrdered = True
                    else:
                        raise Exception(isOrdered)

                    isUnique = oa.attrib.get('isUnique')
                    
                    if isUnique is None:
                        isUnique=False
                    elif isUnique == 'true':
                        isUnique = True
                    else:
                        isUnique = False
                    
                    lowerElements = oa.xpath('lowerValue')
                    if lowerElements:
                        assert len(lowerElements) == 1
                        lowerElement = lowerElements[0]
                        lower = lowerElement.attrib.get('value')
                        if lower is None:
                            lower = 0
                        else:
                            lower = int(lower)
                    else:
                        lower = 1
                        
                    upperElements = oa.xpath('upperValue')
                    if upperElements:
                        assert len(upperElements) == 1
                        upperElement = upperElements[0]
                        upper = upperElement.attrib.get('value')
                        if upper is None:
                            raise Exception(upper)
                        elif upper == '*':
                            upper = None
                        else:
                            raise Exception(upper)
                    else:
                        upper = 1

                        
                    name = self.fix_name(name, 'DataProperty')

                    self.item_by_xmi_id[type_id].ownedAttributes.add(
                        self.meta_model.DataProperty(name, type_, lower, upper, isOrdered, isUnique))

            
            for el in type_element:

                if el.tag != 'ownedLiteral':
                    continue
                name = el.attrib['name']
                
                name = self.fix_name(name, 'EnumerationLiteral')
                
                self.meta_model.EnumerationLiteral(name, self.item_by_xmi_id[type_id])

        
        
        self._build_objects(root_element)
        
        
        
    def _get_object_infos(self, root_element):
        object_infos = []
        for xmi_element_tag in ['InstanceSpecification']:
            for xmi_element in root_element.xpath(
                    f'//*[@xmi:type="uml:{xmi_element_tag}"]', namespaces=NAMESPACES):
                xmi_id = xmi_element.attrib[XMI.id]
                object_infos.append(ObjectInfo(xmi_id, xmi_element))
        return object_infos
    
    
    def _build_object(self, object_info):
        
        xmi_element = object_info.xmi_element
        assert xmi_element.attrib[XMI.type] == 'uml:InstanceSpecification'
        name = xmi_element.attrib['name']
        classifier_xmi_id = xmi_element.attrib['classifier']
        classifier = self.item_by_xmi_id.get(classifier_xmi_id)
        assert isinstance(classifier, self.meta_model.SingletonType)
        self.item_by_xmi_id[object_info.xmi_id] = self.meta_model.SingletonValue(name, classifier)
        
        

        
    def _build_objects(self, root_element): 
        
        object_infos = self._get_object_infos(root_element)
        for info in object_infos:
            self._build_object(info)

            
            
            
       # type_infos = self._get_type_infos(root_element)
       # for info in type_infos:
       #     self._build_type(info)
        
        
    def fix_name(self, name, context):
        
        original_name = name
   
        name = name.replace('/', '_PER_')
        name = name.replace(',', '_COMMA_')
        name = name.replace('(', '_')
        name = name.replace(')', '_')
        
        if name != original_name:
            print(f"WARNING: {context} '{original_name}' renamed to '{name}'")
        check_is_symbol(name)
        
        return name

        
    def _build(self, element):
        
        
        
        xmi_id = element.get(XMI.id)
        
        
        if xmi_id == 'PrimitiveType0':
            ji=1
        
        built = self.item_by_xmi_id.get(xmi_id)
        if built:
            return built
         
        
        
        xmi_type = element.get(XMI.type)
       
        match xmi_type:
            case 'uml:Package':
                return self._build_package(element, self.meta_model.Package)
            case 'uml:Model':
                return self._build_package(element, self.meta_model.Model)
            

        
    def _build_package(self, package_element, package_class):
        name = package_element.attrib.get('name')
        
        if package_class is self.meta_model.Model:
            
            if 'process' in name.lower():
                
                package = package_class(name, 'http://dexpi.org/spec/process/1.0')
            else:
                package = package_class(name, 'http://dexpi.org/spec/plant/1.4')
        else:
            package = package_class(name)
            
        for child_element in package_element.findall('packagedElement'):
            built = self._build(child_element)
            if built is None:
                pass
            elif isinstance(built, self.meta_model.PackageableElement):
                if 1: # BUILTINS
                    package.packagedElements.add(built)
                    
                else:
                    if not isinstance(built, self.meta_model.PrimitiveType):
                        package.packagedElements.add(built)
            
        return package
    
    
    def _build_type_info(self, type_element, class_class):
        xmi_id = package_element.attrib.get(XMI.id)
        
        

        raise Exception(xmi_id)
        class_ = class_class(name)
        for child_element in package_element.findall('packagedElement'):
            built = self._build(child_element)
            if built is None:
                pass
            elif isinstance(built, self.meta_model.Package):
                package.packagedElements.add(built)
        return package


def read_xmi(source, meta_model=None, check_primitive_generalizations=False):
    
    reader = XmiReader(etree.parse(source).getroot(),meta_model=meta_model, check_primitive_generalizations=check_primitive_generalizations)
    return reader.package



from pnb.mcl.metamodel import standard as metamodel


class XmiWriter:
    
    def __init__(self, model_by_name, mode=None):
        
        if 1 or mode == 'modelio':
            self.root = etree.Element('{http://www.omg.org/spec/UML/20110701}Model', nsmap={'uml': 'http://www.omg.org/spec/UML/20110701', 'xmi': 'http://schema.omg.org/spec/XMI/2.1'})
        else:
            self.root = etree.Element(XMI.XMI, nsmap={'uml': 'http://www.omg.org/spec/UML/20161101', 'xmi': 'http://schema.omg.org/spec/XMI/2.1'})
        self.root.attrib[XMI.version] = '2.1'
        self.id_by_element = {}
        
        for name, model in sorted(model_by_name.items()):
            self.root.extend(self.on_element(model, 'packagedElement'))
            
            
    def get_id(self, element):
        id_ = self.id_by_element.get(element)
        if id_ is None:
            id_ = f'ID{len(self.id_by_element)}'
            self.id_by_element[element] = id_
        return id_
            
            
            
    def on_element(self, element, tag):
        if isinstance(element, (metamodel.Package, metamodel.Model)):
            xml = etree.Element(tag, {
                XMI.type: f'uml:{element.get_meta_class_name()}',
                XMI.id: self.get_id(element),
                'name': element.name})
            
            for member in element.packagedElements:
                xml.extend(self.on_element(member, 'packagedElement'))
            return [xml]
        if isinstance(element, metamodel.Class):
            xml = etree.Element(tag, {
                XMI.type: f'uml:Class',
                XMI.id: self.get_id(element),
                'name': element.name})
            if isinstance(element, metamodel.AbstractClass):
                xml.attrib['isAbstract'] = 'true'
            for st in element.superTypes:
                etree.SubElement(xml, 'generalization', {
                    XMI.type: f'uml:Generalization',
                    XMI.id: self.get_id(element),
                    'general': self.get_id(st)})
            return [xml]

        return []
