"""
Standard implementation of pnb.mcl.metamodel.
"""

from __future__ import annotations

from abc import abstractmethod, ABC
import collections.abc
import itertools
import pickle
import types
import typing as T
import weakref

from pnb.mcl.utils import check_is_symbol, check_is_uri

# pylint: disable=invalid-name

# TODO: remove when fixed below
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-instance-attributes


DefaultType = T.TypeVar('DefaultType')
MemberType = T.TypeVar('MemberType', bound='NamedElement')

NO_DEFAULT = object()


class _InternalCall:
    """Auxiliary class to prevent user code calling "internal" functions or methods. It is mainly
    used to protect some classes that are not meant to be instantiated by user code."""

    def __init__(self):
        self.level = 0

    def __enter__(self):
        self.level += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self.level -= 1

    def __bool__(self):
        return self.level > 0

_INTERNAL_CALL = _InternalCall()


def _internal_init(cls: T.Type):
    """Decorator to disable class instantiation from user code."""

    init = vars(cls).get('__init__')

    if init:
        def new_init(self, *args, **kwargs):
            if not _INTERNAL_CALL:
                raise TypeError(f'A {type(self).__name__} object cannot be created from user code.')
            init(self, *args, **kwargs)
    else:
        def new_init(self, *args, **kwargs):
            if not _INTERNAL_CALL:
                raise TypeError(f'A {type(self).__name__} object cannot be created from user code.')

    cls.__init__ = new_init
    return cls


@_internal_init
class Members(
        T.Generic[MemberType],
        collections.abc.Sized,
        collections.abc.Iterable[MemberType]):
    """
    A container for the members of :class:`Namespace` objects.
    
    :code:`Members` objects cannot be created from user code; they are rather retrieved from a
    :code:`Namespace` object.
    
    *Example*
    
    .. execute_code::
        :linenos:
        
        from pnb.mcl.metamodel import standard as metamodel
    
        spam = metamodel.Model('spam', 'http://www.spam.org')
        spam.packagedElements.add(metamodel.Package('SubSpam'))
        for member in spam.members:
            print(member)
    
    - :code:`spam.packagedElements` is a :py:class:`MutableMembers` object that contains the
      :py:attr:`packagedElements <Model.packagedElements>` of :py:class:`Model` :code:`spam`. We
      call its :py:meth:`add() <MutableMembers.add>` method to add a :py:class:`Package` to the
      :code:`packagedElements`.
      
    - :code:`spam.members` is a (non-mutable) :py:class:`Members` object that contains all
      :py:attr:`members <Namespace.members>` of :py:class:`Model` :code:`spam`, including the
      :code:`packagedElements`. Here, we iterate over :code:`spam.members` (cf. 
      :py:meth:`__iter__ <Members.__iter__>`) and retrieve the :code:`Package` we have just added.
    """

    __slots__ = ['__weakref__', '_owner', '_members_property']

    def __init__(self, owner: 'Namespace', members_property: 'MembersProperty'):
        self._owner = owner
        self._members_property = members_property

    @property
    def info(self) -> str:
        """A short description of the :code:`Members` object that includes the names of the
        underlying :py:class:`MembersProperty` and :py:class:`Namespace` object.

        .. execute_code::
            
            from pnb.mcl.metamodel import standard as metamodel
            spam = metamodel.Model('spam', 'http://www.spam.org')
            print(spam.packagedElements.info)"""
        try:
            # TOFIX: remove Cython hack
            return str(f'{self._members_property.info} of {self._owner.info}')
        # pylint: disable=broad-exception-caught
        except Exception:
            return super().__repr__()

    def __repr__(self):
        """A short description of the :code:`Members` object that includes the names of the
        underlying :py:class:`MembersProperty` and :py:class:`Namespace` object.

        .. execute_code::
            
            from pnb.mcl.metamodel import standard as metamodel
            spam = metamodel.Model('spam', 'http://www.spam.org')
            print(repr(spam.packagedElements))"""
        return f'<{self.info}>'

    def __contains__(self, name_or_element: str | NamedElement) -> bool:
        """Check if the :code:`Members` object contains a name or an element.

        - If :code:`name_or_element` is a :code:`str`, returns :code:`True` if the :code:`Members`
          object contains an element with that name.

        - If :code:`name_or_element` is an :py:class:`Element`, returns :code:`True` if the
          :code:`Members` object contains the :code:`Element`.
        """
        return self._members_property._contains_(self._owner, name_or_element)

    def __getattr__(self, name: str) -> MemberType:
        """Get a member by its name.
        
        :code:`__getattr__` is overwritten in order to provide a more concise alternative for
        :py:meth:`at()`.  For instance, assume that :code:`spam` is some :py:class:`Model` object.
        Then
        
        .. code-block:: python
            
            spam.packagedElements.foo
            
        is the same as
        
        .. code-block:: python
            
            spam.packagedElements.at('foo')
            
        (except that the former code would raise a :py:exc:`AttributeError`, whereas the latter
        would raise a :py:exc:`KeyError` if :code:`spam` has no packaged element named :code:`foo`).

        .. warning::
        
            - Be aware that :code:`__getattr__` will only be called by Python as a last resort when
              'normal' attribute access has failed. For example, :code:`spam.packagedElements.info`
              will never retrieve a member element, but rather the value of the :py:attr:`info` 
              property defined in the :py:class:`Members` class.
            
            - Syntax restrictions may also prevent member access via :code:`__getattr__`. For
              example, :code:`"class"` is a valid :py:attr:`name <NamedElement.name>`, but it
              happens to be a Python keyword, and :code:`spam.packagedElements.class` will raise
              a :py:exc:`SyntaxError`.
            
            - :code:`__getattr__` is not intended for *dynamic* member retrieval, i.e., when the
              member name is not a hard-typed literal. Do not write
              
              .. code-block:: python
              
                  getattr(spam.packagedElements, some_variable)
                  
              or even
              
              .. code-block:: python
              
                  spam.packagedElements.__getattr__(some_variable)
                  
              Instead, use :py:meth:`at` or :py:meth:`get`."""
        return self._members_property._getattr_(self._owner, name)

    def __iter__(self) -> T.Iterator[MemberType]:
        """Iterate over the contained members.
        
        If not mentioned otherwise, iteration is in alphanumeric order w.r.t. the members' names.
        If applicable, unnamed members (i.e., :py:class:`NamedElements <NamedElement>` with
        :py:attr:`~NamedElement.name` :code:`== None`) are yielded after the named members in
        arbitrary order.
        """
        return self._members_property._iter_(self._owner)

    def __len__(self) -> int:
        """Get the number of contained members."""
        return self._members_property._len_(self._owner)

    def at(self, name: str) -> MemberType:
        """Get the member with the given name.
        
        Raises:
            KeyError: if there is no member with the given name"""
        return self._members_property._at_(self._owner, name)

    @T.overload
    def get(self, name: str) -> T.Optional[MemberType]:
        ...

    @T.overload
    def get(self, name: str, default: DefaultType) -> MemberType | DefaultType:
        ...

    def get(self, name, default=None):
        """Get the member with the given name, or default if there is no such member."""
        return self._members_property._get_(self._owner, name, default)

    @property
    def names(self) -> T.Iterator[str]:
        """Iterator over the names of the contained members. If not mentioned otherwise, iteration
        is in alphanumeric order."""
        return self._members_property._names_(self._owner)


class MutableMembers(T.Generic[MemberType], Members[MemberType]):
    """
    A container for the members of :class:`Namespace` objects that can be directly modified by
    client code (see :py:meth:`add()`).
    """

    __slots__ = []

    _members_property: MutableMembersProperty

    def add(self, member: MemberType) -> MemberType:
        """Add a :code:`member` to the :code:`MutableMembers` container.
        
        This method returns the added :code:`member`:
        
        .. execute_code::
            :linenos:
            
            from pnb.mcl.metamodel import standard as metamodel
        
            spam = metamodel.Model('spam', 'http://www.spam.org')
            foo = spam.packagedElements.add(metamodel.Package('SubSpam'))
            print(foo)
        """
        self._members_property._add_(self._owner, member)
        return member


_UNNAMED_MEMBERS = object()

class MembersProperty(T.Generic[MemberType], ABC):

    _slot_number = 0

    @property
    @abstractmethod
    def _members_class(self):
        ...

    @staticmethod
    def _get_new_slot_name(slots) -> str:
        # TOFIX: remove Cython hack
        slot_name = str(f'_members_{MembersProperty._slot_number}')
        slots.append(slot_name)
        MembersProperty._slot_number += 1
        return slot_name

    def __init__(self,
            member_type: type[MemberType],
            sorting: T.Literal['alpha', 'none'],
            derived_properties: T.Iterable[DerivedMembersProperty[NamedElement]]):
        self._member_type = member_type
        self._sorting = sorting
        self._derived_properties_: set[DerivedMembersProperty] = set()
        self._derived_properties_by_type: dict[
            type[Namespace], tuple[DerivedMembersProperty, ...]] = {}
        self._members_by_owner: weakref.WeakValueDictionary[
            NamedElement, Members] = weakref.WeakValueDictionary()

        # Reset in __set_name__:
        self._owner_type: type[Namespace] = None # type: ignore
        self._info: str = None # type: ignore
        self._name: str = None  # type: ignore

        for prop in derived_properties:
            self._add_derived_property(prop)

    def __set_name__(self, owner_type, name: str):
        # Correct annotation of _owner_type would be Type[Namespace]. However, this method is called
        # during the creation of the Namespace class, i.e., the Namespace class has not yet been
        # added to the module namespace at this time. We omit the annotation because typeguard
        # cannot handle this.
        self._owner_type = owner_type
        self._name = name
        self._info = f'{owner_type.__name__}.{name}'

    @property
    def info(self) -> str:
        return self._info

    @property
    def member_type(self) -> type[MemberType]:
        return self._member_type

    @property
    def owner_type(self) -> type[Namespace]:
        return self._owner_type

    def __repr__(self):
        return f'<{self.info}>'

    def _add_derived_property(self, prop: 'DerivedMembersProperty'):
        prop._do_add_direct_base_property_(self)
        for derived_prop in prop._derived_properties_:
            derived_prop._do_add_base_property_(self)
        self._do_add_derived_property_(prop)

    def _do_add_derived_property_(self, prop):
        if prop not in self._derived_properties_:
            self._derived_properties_.add(prop)
            for derived_prop in prop._derived_properties_:
                self._do_add_derived_property_(derived_prop)

    def _get_derived_properties(self, owner_type: type[Namespace]):
        derived_properties = self._derived_properties_by_type.get(owner_type)
        if derived_properties is None:
            derived_properties = tuple(
                prop for prop in self._derived_properties_
                if issubclass(owner_type, prop.owner_type))
            self._derived_properties_by_type[owner_type] = derived_properties
            # TOFIX: If this still holds when all member props are implemented:
            #   remove this method, instead use self._derived_properties_ directly
            assert len(derived_properties) == len(self._derived_properties_)
        return derived_properties

    def _get_members(self, owner) -> Members[MemberType]:
        members = self._members_by_owner.get(owner)
        if members is None:
            with _INTERNAL_CALL:
                members = self._members_class(owner, self)
            self._members_by_owner[owner] = members
        return members

    @T.overload
    def __get__(
            self,
            obj: MemberType,
            objtype: type[MemberType]) -> Members[MemberType]:
        ...

    @T.overload
    def __get__(self,
            obj: None,
            objtype: type[MemberType]) -> MembersProperty[MemberType]:
        ...

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            return self._get_members(obj)

    @abstractmethod
    def _get_members_dict_(
            self, owner: 'Namespace', sorting_required: bool) -> dict[str, MemberType]:
        ...

    def _contains_(self, owner, name_or_element) -> bool:
        members_dict = self._get_members_dict_(owner, False)
        if isinstance(name_or_element, str):
            return name_or_element in members_dict
        else:
            return members_dict.get(name_or_element.name) is name_or_element

    def _getattr_(self, owner: 'Namespace', name: str) -> MemberType:
        member = self._get_members_dict_(owner, False).get(name)
        if member is None:
            raise AttributeError(
                f"{self._get_members(owner).info} has no attribute '{name}'.")
        return member

    def _iter_(self, owner: 'Namespace') -> T.Iterator[MemberType]:
        members_dict = self._get_members_dict_(owner, True)
        yield from members_dict.values()


    def _len_(self, owner: 'Namespace') -> int:
        return len(self._get_members_dict_(owner, False))

    def _at_(self, owner: 'Namespace', name: str) -> MemberType:
        member = self._get_members_dict_(owner, False).get(name)
        if member is None:
            raise KeyError(f"{self._get_members(owner).info} has no member named '{name}'.")
        return member

    def _get_(
            self,
            owner: Namespace,
            name: str, default: DefaultType) -> MemberType | DefaultType:
        return self._get_members_dict_(owner, False).get(name, default)

    def _names_(self, owner) -> T.Iterator[str]:
        return iter(self._get_members_dict_(owner, True))


class MutableMembersProperty(
        T.Generic[MemberType], MembersProperty[MemberType]):
    """A MembersProperty that can be directly modified. It does not depend
    on any other MembersProperty.
    """

    _members_class = MutableMembers

    def __init__(self,
            slots: list[str],
            member_type: type[MemberType],
            is_composition: bool,
            sorting: T.Literal['alpha', 'none']='alpha',
            derived_properties: T.Iterable[DerivedMembersProperty]=()):
        super().__init__(
            member_type, sorting, derived_properties=derived_properties)
        self._is_composition = is_composition
        self._members_dict_slot_name = self._get_new_slot_name(slots)
        self._is_sorted_slot_name = self._get_new_slot_name(slots)

        # Reset in __set_name__.
        self._members_dict_descriptor: types.MemberDescriptorType = None
        self._is_sorted_descriptor: types.MemberDescriptorType = None

    def __set_name__(self, owner, name: str) -> None:
        # See comment at __set_name__ in superclass.
        super().__set_name__(owner, name)
        self._members_dict_descriptor = getattr(owner, self._members_dict_slot_name)
        # TOFIX: check removal
        self._is_sorted_descriptor = getattr(owner, self._is_sorted_slot_name)

    @T.overload
    def __get__(
            self,
            obj: MemberType,
            objtype: type[MemberType]) -> MutableMembers[MemberType]:
        ...

    @T.overload
    def __get__(self,
            obj: None,
            objtype: type[MemberType]) -> MutableMembersProperty[MemberType]:
        ...

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            return self._get_members(obj)

    def _get_members_dict_(self, owner: Namespace, sorting_required: bool) -> dict[str, MemberType]:
        try:
            # pylint: disable=unnecessary-dunder-call
            members_dict = self._members_dict_descriptor.__get__(owner)
        except AttributeError:
            members_dict = {}
            self._members_dict_descriptor.__set__(owner, members_dict)
            return members_dict

        if sorting_required:
            try:
                # pylint: disable=unnecessary-dunder-call
                is_sorted = self._is_sorted_descriptor.__get__(owner)
            except AttributeError:
                is_sorted = True
            if not is_sorted:
                assert self._sorting == 'alpha'
                items = sorted(members_dict.items())
                members_dict.clear()
                members_dict.update(items)
                    
        return members_dict

    def _add_(self, owner: Namespace, member: MemberType):
        name = member.name
        members_dict = self._get_members_dict_(owner, False)
        if name:
            name_is_registered = Namespace.members.get_name_is_registered(owner, name)
            if name_is_registered:
                own_member = members_dict.get(name)
                if member is own_member:
                    return
                elif own_member is not None:
                    raise TypeError(
                        f'{member!r} cannot be added to {self._get_members(owner)!r} because '
                        f'{self._get_members(owner)!r} already contains a member with this name.')
                else:
                    raise TypeError(
                        f'{member!r} cannot be added to {self._get_members(owner)!r} because '
                        f'{owner!r} already has a member with this name.')
    
            assert name not in members_dict
            
        else:
            unnamed_members = members_dict.get(_UNNAMED_MEMBERS)
            if unnamed_members and member in unnamed_members:
                return
            
        if not isinstance(member, self._member_type):
            raise TypeError(
                f'{member!r} cannot be added to {self._get_members(owner)!r} because it is not a '
                f'<{self._member_type.get_meta_class_name()}>.')
        if self._is_composition:
            if member.owner is not None:
                raise TypeError(
                    f'{member!r} is already owned by {member.owner!r} and cannot be added to '
                    f'{self._get_members(owner)!r}.')
            member._set_owner_(owner)
            
        if name:
            Namespace.members.register_name(owner, name)
            members_dict[name] = member

            if self._sorting == 'alpha':
                # pylint: disable=unnecessary-dunder-call
                self._is_sorted_descriptor.__set__(owner, False)
            else:
                assert self._sorting == 'none'
        else:
            if unnamed_members is None:
                members_dict[unnamed_members] = set((member, ))
            else:
                unnamed_members.add(member)

        for prop in self._get_derived_properties(type(owner)):
            prop._invalidate_(owner)


class DerivedMembersProperty(T.Generic[MemberType], MembersProperty[MemberType]):
    """A MembersProperty that depends on a single other MembersProperty.
    """

    _members_class = Members

    def __init__(self,
            slots: list[str],
            member_type: type[MemberType],
            sorting: T.Literal['alpha', 'none']='alpha',
            derived_properties: T.Iterable[DerivedMembersProperty]=(),
            base_properties: T.Iterable[MembersProperty]=()):
        super().__init__(member_type, sorting, derived_properties)

        self._base_properties: set[MembersProperty] = set()
        self._direct_base_properties: set[MembersProperty] = set()
        self._direct_base_properties_by_owner: dict[
            type[Namespace], tuple[MembersProperty, ...]] = {}
        for base_prop in base_properties:
            base_prop._add_derived_property(self)

        self._members_dict_slot_name = self._get_new_slot_name(slots)

        # Reset in __set_name__
        self._members_dict_descriptor: types.MemberDescriptorType = None

    def __set_name__(self, owner, name) -> None:
        super().__set_name__(owner, name)
        self._members_dict_descriptor = getattr(owner, self._members_dict_slot_name)

    def _do_add_direct_base_property_(self, prop):
        assert not self._direct_base_properties or self._sorting != 'none'
        self._direct_base_properties.add(prop)
        self._do_add_base_property_(prop)

    def _do_add_base_property_(self, prop):
        self._base_properties.add(prop)

    def _get_members_dict_(self, owner: Namespace, sorting_required: bool) -> dict[str, MemberType]:
        try:
            # pylint: disable=unnecessary-dunder-call
            members_dict = self._members_dict_descriptor.__get__(owner)
        except AttributeError:
            members_dict = None

        if members_dict is None:
            members_dict = self._make_members_dict(owner)
            # pylint: disable=unnecessary-dunder-call
            self._members_dict_descriptor.__set__(owner, members_dict)
        elif None in members_dict:
            members_dict.clear()
            members_dict.update(self._make_members_dict(owner))
        return members_dict

    def _invalidate_(self, owner):
        try:
            # pylint: disable=unnecessary-dunder-call
            members_dict = self._members_dict_descriptor.__get__(owner)
        except AttributeError:
            return
        members_dict[None] = None

    @abstractmethod
    def _make_members_dict(self, owner: Namespace) -> dict[str, MemberType]:
        ...

    def _get_direct_base_properties(self, owner_type: type[Namespace]):
        direct_base_properties = self._direct_base_properties_by_owner.get(owner_type)
        if direct_base_properties is None:
            direct_base_properties = tuple(
                prop for prop in self._direct_base_properties
                if issubclass(owner_type, prop.owner_type))
            self._direct_base_properties_by_owner[owner_type] = direct_base_properties
        return direct_base_properties


class UnionMembersProperty(T.Generic[MemberType], DerivedMembersProperty[MemberType]):

    def _make_members_dict(self, owner: Namespace) -> dict[str, MemberType]:
        members_dict = {}
        if self._sorting == 'none':
            for base_prop in self._get_direct_base_properties(type(owner)):
                members_dict.update(base_prop._get_members_dict_(owner, True))
        else: # 'alpha'
            for base_prop in self._get_direct_base_properties(type(owner)):
                members_dict.update(base_prop._get_members_dict_(owner, False))
            members_dict = dict(sorted(members_dict.items()))
        return members_dict


class _RootMembersProperty(T.Generic[MemberType], UnionMembersProperty[MemberType]):

    def __init__(self,
            slots: list[str],
            member_type: type[MemberType],
            derived_properties: T.Iterable[DerivedMembersProperty]=()):
        super().__init__(slots, member_type, derived_properties=derived_properties)
        self._names_slot_name = self._get_new_slot_name(slots)

        # Reset in __set_name__
        self._names_descriptor: types.MemberDescriptorType = None

    def __set_name__(self, owner, name) -> None:
        super().__set_name__(owner, name)
        self._names_descriptor = getattr(owner, self._names_slot_name)

    def _get_names(self, owner):
        try:
            # pylint: disable=unnecessary-dunder-call
            return self._names_descriptor.__get__(owner)
        except AttributeError:
            names = set()
            # pylint: disable=unnecessary-dunder-call
            self._names_descriptor.__set__(owner, names)
            return names

    def get_name_is_registered(self, owner, name):
        return name in self._get_names(owner)

    def register_name(self, owner, name):
        self._get_names(owner).add(name)


def _abstract(cls):
    # TOFIX: in-/dedent
    doc = cls.__doc__
    if doc:
        doc = '\n\n' + doc
    else:
        doc = ''
    cls.__doc__ = '*This class is abstract.*' + doc
    cls._is_abstract_meta_class = True
    return cls


@_abstract
class Element:

    __slots__: list[str] = ['__weakref__', '_owner_ref']

    @classmethod
    def get_meta_class_name(cls) -> str:
        return cls.__name__

    def __init__(self, **kwargs) -> None:
        if vars(type(self)).get('_is_abstract_meta_class'):
            raise TypeError(f'{type(self)} is abstract')
        super().__init__(**kwargs)
        self._owner_ref: T.Optional[weakref.ref] = None

    @property
    def info(self):
        return super().__repr__() # TODO

    def __repr__(self):
        return f'<{self.info}>'

    @property
    def owner(self) -> T.Optional[Element]:
        ref = self._owner_ref
        if ref is None:
            return None
        owner = ref()
        if owner is None:
            raise Exception('TODO')
        return owner

    def _set_owner_(self, owner):
        assert self.owner is None
        self._owner_ref = weakref.ref(owner)

    @property
    def model(self):
        owner = self
        while True:
            if isinstance(owner, Model):
                return owner
            owner = owner.owner
            if owner is None:
                return None


@_abstract
class NamedElement(Element):

    __slots__ = ['_name']
    
    _name_required = True # TODO: better default False

    def __init__(self, name: str | None, **kwargs):
        """
        Args:
            name: the name
        """
        super().__init__(**kwargs)
        
        if name is None:
            if self._name_required:
                raise TypeError(f'A {self.get_meta_class_name()} must have a name.')
        else:
            check_is_symbol(name, 'name')
        self._name = name

    @property
    def name(self) -> str | None:
        return self._name
    
    @property
    def qualifiedName(self) -> str | None:
        assert self.name
        if self.owner:
            return '.'.join((self.owner.qualifiedName, self.name)) # TODO None
        else:
            return self._name
        
        
    qualifiedName_chained = qualifiedName
        

    @property
    def info(self):
        try:
            qualifiedName = self.qualifiedName
        except Exception:
            qualifiedName = '???'

        return f"{type(self).__name__} '{qualifiedName}'"

    def get_model_and_qname(self) -> tuple[Model, str]:
        model = self.model

        if not model:
            raise Exception('no model', self)
        try:
            name = self.name
        except AttributeError:
            name = None
            
        if name:
            parts: list[str] = []
            
            element = self
            # for now, assume model imports all packages
            
            if isinstance(element, Model):
                pass
            else: 
                element = self
                while True:
                    assert element.name
                    parts.append(element.name)
                    element = element.owner
                    assert element
                    if isinstance(element, (Model, Object)):
                        break
                    
            return model, '.'.join(reversed(parts))
        
        else:
            return model, None


@_abstract
class PackageableElement(NamedElement):
    __slots__ = []


@_abstract
class Namespace(NamedElement):
    """
    Attributes:
        members: All members of the Namespace.
        
        ownedMembers: The owned members of the Namespace.
        
        importedMembers: The imported members of the Namespace.
    """

    __slots__ = []

    def __init__(self, members=(), **kwargs):
        super().__init__(**kwargs)
        for member in members:
            self.add(member)

    members = _RootMembersProperty[NamedElement](
        __slots__, NamedElement)

    ownedMembers = UnionMembersProperty[NamedElement](
        __slots__, NamedElement,
        derived_properties=[members])

    importedMembers = UnionMembersProperty[NamedElement](
        __slots__, PackageableElement,
        derived_properties=[members])

    def __iter__(self) -> T.Iterator[NamedElement]:
        return iter(self.members)

    def __getattr__(self, name) -> NamedElement:
        return getattr(self.members, name)
    
    def search_iter(self, name: str, type: T.Type[NamedElement]=NamedElement):
        for member in self:
            if member.name == name and isinstance(member, type):
                yield member
            if isinstance(member, Namespace):
                yield from member.search_iter(name, type)
                
    def search_unique(self, name: str, type: T.Type[NamedElement]=NamedElement, default=NO_DEFAULT):
        members = list(self.search_iter(name, type))
        if not members:
            if default is NO_DEFAULT:
                raise KeyError(f'{self!r} has no descendant {name}')
            else:
                return default
        if len(members) > 1:
            raise KeyError(f'{self!r} has more than one descendant {name}')
        return members[0]
        

# TODO: remove?
@_abstract
class InstanceSpecification(NamedElement): 
    __slots__ = []
    
    
@_abstract
class TypeExpression(Element):
    pass

@_abstract
class ClassExpression(TypeExpression):
    pass

@_abstract
class DataTypeExpression(TypeExpression):
    pass


@_abstract
class Type(Namespace, PackageableElement, TypeExpression):
    
    """
    cf. Classifier
    7.5.3.1 All Types in UML are Classifiers 
    """
    
    __slots__ = ['_superTypes', '_allSuperTypes', '_subTypes', '_allSubTypes']
    
    _name_required = True
    name: string
   
    
    
    @property
    def isAbstract(self):
        rek
    
    ownedAttributes = []
    

    
    @property
    def allSubTypes(self):
        result = set()
        for st in self.subTypes:
            result.add(st)
            result.update(st.allSubTypes)
        return result
    
    def _add_supertype_(self, supertype):
        assert not self._subTypes
        assert not self._superTypes
        self._superTypes = self._superTypes + (supertype, )
        self._allSuperTypes = frozenset([supertype]).union(supertype._allSuperTypes)
        supertype._subTypes.append(self)

    @property
    def subTypes(self):
        return self._subTypes
    
    def has_value(self, value):
        if isinstance(value, Element):
            return value.type is self or value.type in self.allSubTypes
    
    def __init__(self, name: str, superTypes: T.Iterable[Type], subTypes: T.Iterable[Type]=(), **kwargs):
        if name is None:
            raise TypeError(f'A {self.get_meta_class_name()} must have a name.')
        super().__init__(name=name, **kwargs)
        self._subTypes = []
        self._superTypes = tuple(superTypes)
        self._allSuperTypes = frozenset(itertools.chain(
            self._superTypes,
            itertools.chain.from_iterable(
                st.allSuperTypes for st in self._superTypes)))
        for superType in self._superTypes:
            superType._subTypes.append(self)
            
        for subType in subTypes:
            pass
        
        
    @property
    def superTypes(self) -> tuple[Type, ...]:
        return self._superTypes
    
    @property
    def allSuperTypes(self) -> frozenset[Type]:
        return self._allSuperTypes
        
  # TODO: chekc if useful here
  # readonly subTypes: readonly Type[];
  # readonly allSubTypes: ReadonlySet<Type>;
  # readonly isAbstract: boolean;
  # readonly ownedAttributes: ReadonlyAtMap<string, Property>;
  # readonly ownedDataAttributes: ReadonlyAtMap<string, DataProperty>;
  # readonly ownedObjectAttributes: ReadonlyAtMap<string, ObjectProperty>;
  # readonly ownedCompositionAttributes: ReadonlyAtMap<string, CompositionProperty>;
  # readonly ownedReferenceAttributes: ReadonlyAtMap<string, ReferenceProperty>;
  # readonly attributes: ReadonlyAtMap<string, Property>;
  # readonly dataAttributes: ReadonlyAtMap<string, DataProperty>;
  # readonly objectAttributes: ReadonlyAtMap<string, ObjectProperty>;
  # readonly compositionAttributes: ReadonlyAtMap<string, CompositionProperty>;
  # readonly referenceAttributes: ReadonlyAtMap<string, ReferenceProperty>;



class Package(Namespace, PackageableElement):
    """
    
    """

    __slots__ = []

    def __init__(self, name: str, members=()):
        super().__init__(name=name, members=members)

    def add(self, element):
        return self.packagedElements.add(element)

    packagedElements = (
        MutableMembersProperty[PackageableElement](
            __slots__, PackageableElement, True,
            derived_properties=[Namespace.ownedMembers]))

    # TODO: filter
    ownedTypes: Members[Type] = (
        UnionMembersProperty(
            __slots__, Type,
             base_properties=[packagedElements]))                               # type: ignore


class Model(Namespace):
    __slots__ = ['_uri', '_unnamedObjects']
    
    @property
    def unnamedObjects(self):
        return self._unnamedObjects


    def add(self, element):
        if isinstance(element, Object) and not element.name:
            element._set_owner_(self)
            self._unnamedObjects.add(element)
        else:
            self.packagedElements.add(element)
        return element

    packagedElements = (
        MutableMembersProperty[PackageableElement](
            __slots__, PackageableElement, True,
            derived_properties=[Namespace.ownedMembers]))

    # TODO: filter
    ownedTypes: Members[Type] = (
        UnionMembersProperty(
            __slots__, Type,
            base_properties=[packagedElements]))                               # type: ignore

    def __init__(self, name: str, uri: str, members=()):
        super().__init__(name=name)
        check_is_uri(uri, 'uri')
        self._uri = uri
        self._unnamedObjects = set()
        for member in members:
            self.add(member)
        
    @property
    def uri(self):
        return self._uri
        
    @property
    def info(self):
        return f'{super().info} ({self.uri})'


@_abstract
class TypedElement(NamedElement):
    """
    merged with UML MultiplicityElement
    """
    __slots__ = ['_lower', '_upper', '_type', '_isOrdered']

    def __init__(
            self, lower: int, upper: T.Optional[int], type_: Type, isOrdered=bool, **kwargs):
        super().__init__(**kwargs)
        self._lower = lower
        self._upper = upper
        self._type = type_
        self._isOrdered = isOrdered

    @property
    def lower(self) -> int:
        return self._lower

    @property
    def upper(self) -> T.Optional[int]:
        return self._upper

    @property
    def type(self) -> TypeExpression:
        return self._type

    @property
    def isOrdered(self) -> bool:
        return self._isOrdered;

    @property
    @abstractmethod
    def isUnique(self) -> bool:
        pass


@_abstract
class Property(TypedElement):
    
    __slots__ = []

    def _set_(self, owner, value):
        if self.upper in [0, 1]:
            if value is None:
                values = []
            else:
                values = [value]
        else:
            if isinstance(value, str):
                RAISE
            try:
                values = list(value)
            except TypeError:
                print(self.qualifiedName, value)
                RAISE
            
        if self.upper is not None and len(values) > self.upper:
            ERROR
        for value in values:
            pass

        # TODO check type
        # TODO ref if appl.
        # TODO set owner if appl.
        # TODO handle old values

        if isinstance(self, CompositionProperty):
            for value in values:
                value._set_owner_(owner)

        owner._attribute_values_[self] = values

    def _set_values_(self, owner, values):
        if isinstance(self, CompositionProperty):
            for value in values:
                value._set_owner_(owner)

        owner._attribute_values_[self] = values

    def _get_(self, owner):
        values = owner._attribute_values_.get(self)
        
        if self.upper in [0, 1]:
            if values is None:
                return None
            assert len(values) <= 1
            if not values:
                return None
            else:
                return values[0]
        else:
            return list(values)
        
        
    def _get_values_(self, owner):
        values = owner._attribute_values_.get(self)
        if values is None:
            values = []
        return values
   
    
@_abstract
class ObjectProperty(Property):
    
    __slots__ = []
    
    type: Class
    
    oppositeLower: int
    oppositeUpper: T.Optional[int]


class CompositionProperty(ObjectProperty):
    
    __slots__ = ['_isUnique', '_oppositeLower', '_oppositeUpper']
    
    def __init__(self, name: str, type_: Class, lower: int, upper: T.Optional[int], isOrdered: bool, redefines: T.Iterable[ObjectProperty]=()):
        
        super().__init__(name=name, lower=lower, upper=upper, type_=type_, isOrdered=isOrdered)
        # TODO: redefines

    @property
    def isUnique(self):
        return True

    @property
    def oppositeLower(self):
        return 0

    @property
    def oppositeUpper(self):
        return 1


class ReferenceProperty(ObjectProperty):
    
    __slots__ = ['_isUnique', '_oppositeLower', '_oppositeUpper']
    
    def __init__(self, name: str, type_: Class, lower: int, upper: T.Optional[int], isOrdered: bool, isUnique: bool, oppositeLower: int=0, oppositeUpper: T.Optional[int]=None, redefines: T.Iterable[ReferenceProperty]=()):
        
        super().__init__(name=name, lower=lower, upper=upper, type_=type_, isOrdered=isOrdered)
      
        # TODO: check ints
        self._isUnique = isUnique
        self._oppositeLower = oppositeLower
        self._oppositeUpper = oppositeUpper
        # TODO: redefines

    @property
    def isUnique(self):
        return self._isUnique

    @property
    def oppositeLower(self):
        return self._oppositeLower

    @property
    def oppositeUpper(self):
        return self._oppositeUpper
    
    

class DataProperty(Property):
    
    __slots__ = ['_isUnique']
    
    def __init__(self, name: str, type_: DataType, lower: int=1, upper: T.Optional[int | str]='lower', isOrdered: bool=False, isUnique: bool=False, redefines: T.Iterable[ReferenceProperty]=()):
        
        if upper == 'lower':
            upper = lower
        type_ = {
            str: String,
            float: Double,
            int: Integer}.get(type_, type_)
        assert isinstance(type_, DataTypeExpression)
        # TODO owned vs not owned
        super().__init__(name=name, lower=lower, upper=upper, type_=type_, isOrdered=isOrdered)
      
        # TODO: check ints
        self._isUnique = isUnique
        # TODO: redefines

    @property
    def isUnique(self):
        return self._isUnique
    
    
@_abstract
class TypeParameter(NamedElement, TypeExpression):
    
    _name_required = True
    name: str
    
    def __init__(self, name: str, type: TypeExpression):
        super().__init__(name=name)
        self.type = type



@_abstract
class Class(Type, ClassExpression):
    
    # TODO: _attributes -> Conc and Abs

    __slots__ = ['_attributes', '_extensions']

    ownedAttributes = (
        MutableMembersProperty[Property](
            __slots__, Property, True,
            derived_properties=[Namespace.ownedMembers]))
    
    
    ownedParameters = (
        MutableMembersProperty[Property](
            __slots__, TypeParameter, True,
            derived_properties=[Namespace.ownedMembers]))
    
    @property
    def attributes(self):
        
        attributes = self._attributes
        if attributes is None:
            attributes = {}
            for type_ in self.superTypes:
                attributes.update(type_.attributes)
                

            attributes.update({prop.name: prop for prop in self.ownedAttributes})
            
            attributes = dict(sorted(attributes.items()))
            self._attributes = attributes
 
        return attributes

    def __init__(self, name: str, superTypes: T.Iterable[Class]=(), members=()):
        super().__init__(name=name, superTypes=superTypes, members=members)
        self._attributes = None
        self._extensions = []
        
    def __call__(self, **kwargs):
        return Object(self, **kwargs)
    
    def add(self, element):
        if isinstance(element, Property):
            self.ownedAttributes.add(element)
        elif isinstance(element, TypeParameter):
            self.ownedParameters.add(element)
        else:
            raise TypeError(element)
        return element
    
    
    
    
    

    
class ClassExtension(Namespace, PackageableElement):
    
    __slots__ = ['baseType']
    
    ownedAttributes = (
        MutableMembersProperty[Property](
            __slots__, Property, True,
            derived_properties=[Namespace.ownedMembers]))

    ownedParameters = (
        MutableMembersProperty[Property](
            __slots__, TypeParameter, True,
            derived_properties=[Namespace.ownedMembers]))

    def __init__(self, name: str, baseType: Class, members=()):
        self.baseType = baseType
        baseType._extensions.append(self)
        super().__init__(name=name, members=members)
        
        
    
    def add(self, element):
        if isinstance(element, Property):
            self.ownedAttributes.add(element)
        elif isinstance(element, TypeParameter):
            self.ownedParameters.add(element)
        else:
            raise TypeError(element)
        return element
    
    
    
    
    
    
    


class AbstractClass(Class):
    """
    bla.
    
    blub
    ====
    
    mimi.
    """
    
    
    
    __slots__ = []

    isAbstract = True


class ConcreteClass(Class):
    __slots__ = []
    
    isAbstract = False
    
    def __call__(self, name=None, **kwargs):
        return Object(self, name=name, **kwargs)
    
    

@_abstract    
class DataType(Type, DataTypeExpression):
    __slots__ = []
    
    isAbstract = False
    
    def __init__(self, name: str, superTypes: T.Iterable[AbstractDataType]=()):
        super().__init__(name=name, superTypes=superTypes)







class ClassParameter(ClassExpression, TypeParameter):
    pass



class DataTypeParameter(DataTypeExpression, TypeParameter):
    pass

















    
class AbstractDataType(DataType):
    __slots__ = []
    
    isAbstract = True
   
   
class SingletonType(DataType):
    __slots__ = ['_value_ref'] 
    
    def __init__(self, name: str, superTypes: T.Iterable[AbstractDataType]=()):
        super().__init__(name=name, superTypes=superTypes)
        self._value_ref = None
        
    @property
    def value(self):
        value_ref = self._value_ref
        if value_ref is None:
            return None
        value = value_ref()
        if value is None:
            ERROR
        return value

    
class SingletonValue(PackageableElement):
    __slots__ = ['_type'] 
    
    def __init__(self, name, type_: SingletonType):
        if type_.value:
            ERROR
        super().__init__(name=name)
        type_._value_ref = weakref.ref(self)
        self._type = type_
        
    @property
    def type(self):
        return self._type


class AggregatedDataType(DataType):
    __slots__ = []
    
    # TODO: Property->DataProperty?
    ownedAttributes = (
        MutableMembersProperty[Property](
            __slots__, Property, True,
            derived_properties=[Namespace.ownedMembers]))
    
    ownedParameters = (
        MutableMembersProperty[Property](
            __slots__, DataTypeParameter, True,
            derived_properties=[Namespace.ownedMembers]))
    
    @property
    def attributes(self):
        return self.ownedAttributes
    
    
    def add(self, element):
        if isinstance(element, Property):
            self.ownedAttributes.add(element)
        elif isinstance(element, DataTypeParameter):
            self.ownedParameters.add(element)
        else:
            raise TypeError(element)
        return element
    
    def __call__(self, name=None, **kwargs):
        return AggregatedDataValue(self, name=name, **kwargs)
        
        
class EnumerationLiteral(NamedElement):  # TODO superclass value or similar?

    @property
    def type(self):
        return self._enumeration
    
    def __init__(self, name: str, enumeration: Enumeration):
        super().__init__(name=name)
        self._enumeration = enumeration
        enumeration._orderedOwnedLiterals_.add(self)
 

class Enumeration(DataType):
    __slots__ = []
    

    _orderedOwnedLiterals_ = MutableMembersProperty[EnumerationLiteral](
        __slots__, EnumerationLiteral, True,
        sorting='none',
        derived_properties=[Namespace.ownedMembers])

    orderedOwnedLiterals = UnionMembersProperty[EnumerationLiteral](
        __slots__, EnumerationLiteral,
        sorting='none',
        base_properties=[_orderedOwnedLiterals_])

    ownedLiterals = UnionMembersProperty[EnumerationLiteral](
        __slots__, EnumerationLiteral,
        base_properties=[_orderedOwnedLiterals_])

    def __init__(self, name: str, superTypes: T.Iterable[AbstractDataType]=()):
        super().__init__(name=name, superTypes=superTypes)
        



@_abstract
class PrimitiveType(DataType):
    __slots__ = []
    

class BooleanType(PrimitiveType):
    __slots__ = []



UNDEFINED = object()

class UndefinedType(PrimitiveType):
    __slots__ = []
    
    def __call__(self):
        return UNDEFINED
  
    
class StringType(PrimitiveType):
    __slots__ = []
    


class DoubleType(PrimitiveType):
    __slots__ = []


class IntegerType(PrimitiveType):
    __slots__ = []



class DateTimeType(PrimitiveType):
    __slots__ = []
    


class Object(PackageableElement):
    
    # TODO: name optional
    __slots__ = ['_type_ref', '_attribute_values_']
    
    _name_required = False
    
    @property
    def qualifiedName_chained(self):
        assert self.name
        if self.owner:
            return '.'.join((self.owner.qualifiedName_chained, self.name)) # TODO None
        else:
            return self._name
        

    def __init__(self, type_: ConcreteClass, name=None, **kwargs):
            
        super().__init__(name=name)
        
        self._attribute_values_ = {} # TODO: delay?
        self._type_ref = weakref.ref(type_)
        for name, value in sorted(kwargs.items()):
            prop = type_.attributes.get(name)
            prop._set_(self, value)

    @property
    def type(self) -> ConcreteClass:
        type_ = self._type_ref()
        if not type_:
            raise TypeError()
        return type_
    
    
    def __getattr__(self, name):
        prop = self.type.attributes.get(name)
        if not prop:
            raise AttributeError(name)
        return prop._get_(self)
    
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            prop = self.type.attributes.get(name)
            prop._set_(self, value)
            
    @property
    def info(self):
        try:
            qualifiedName = f"'{self.qualifiedName}'"  
        except Exception:
            qualifiedName = f'#{id(self)}'

        return f"{type(self).__name__} '{qualifiedName}' a {self.type.qualifiedName}"
    
    
    
class AggregatedDataValue(PackageableElement):
    
    # TODO: name optional
    __slots__ = ['_type_ref', '_attribute_values_']
    
    _name_required = False

    def __init__(self, type_: AggregatedDataType, name=None, **kwargs):
            
        super().__init__(name=name)
        
        self._attribute_values_ = {} # TODO: delay?
        self._type_ref = weakref.ref(type_)
        for name, value in sorted(kwargs.items()):
            prop = type_.attributes.get(name)
            prop._set_(self, value)

    @property
    def type(self) -> AggregatedDataType:
        type_ = self._type_ref()
        if not type_:
            raise TypeError()
        return type_
    
    
    def __getattr__(self, name):
        prop = self.type.attributes.get(name)
        if not prop:
            raise AttributeError(name)
        return prop._get_(self)
    
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            prop = self.type.attributes.get(name)
            prop._set_(self, value)
            
    @property
    def info(self):
        try:
            qualifiedName = f"'{self.qualifiedName}'"  
        except Exception:
            qualifiedName = f'#{id(self)}'

        return f"{type(self).__name__} '{qualifiedName}' a {self.type.qualifiedName}"

  
BUILTIN = MCL = Model('Builtin', 'http://www.dexpi.org/dexpiml/1.0/Builtin')

# AnyURI = MCL.packagedElements.add(StringType('AnyURI'))
# Boolean = MCL.packagedElements.add(BooleanType('Boolean'))
# DateTime = MCL.packagedElements.add(DateTimeType('DateTime'))
# Double = MCL.packagedElements.add(DoubleType('Double'))
# Integer = MCL.packagedElements.add(IntegerType('Integer'))
# String = MCL.packagedElements.add(StringType('String'))
# UnsignedByte = MCL.packagedElements.add(IntegerType('UnsignedByte'))


Undefined = BUILTIN.add(UndefinedType('Undefined'))


AnyURI = BUILTIN.add(StringType('AnyURI'))
Boolean = BUILTIN.add(BooleanType('Boolean'))
DateTime = BUILTIN.add(DateTimeType('DateTime'))
Double = BUILTIN.add(DoubleType('Double'))
Integer = BUILTIN.add(IntegerType('Integer'))
String = BUILTIN.add(StringType('String'))
UnsignedByte =BUILTIN.add(IntegerType('UnsignedByte'))




class MetaData:

    def __init__(self):
        self.data_by_prop_by_element: dict[Element, dict[str, object]] = {}
        
    def for_element(self, element):
        return self.data_by_prop_by_element.get(element, {})

    def set(self, element, prop, value):
        data_by_prop = self.data_by_prop_by_element.setdefault(element, {})
        data_by_prop[prop] = value

    def get(self, element, prop, default=NO_DEFAULT):
        data = self.data_by_prop_by_element.get(element, {}).get(prop, default)
        if data is NO_DEFAULT:
            raise KeyError(element, prop)
        return data
    
    def write(self, path):
        data_by_prop_by_qname = {element.qualifiedName: data_by_prop for element, data_by_prop in self.data_by_prop_by_element.items()}
        assert None not in data_by_prop_by_qname
        with path.open('wb') as file_out:
            pickle.dump(data_by_prop_by_qname, file_out)
        
    @staticmethod
    def read(path, model_by_name):
        with path.open('rb') as file_in:
            data_by_prop_by_qname = pickle.load(file_in)

        def get_element(qname: str):
            model_name, *sub_names = qname.split('.')
            element = model_by_name.get(model_name)
            if not element:
                raise Exception(f'no member "{model_name}"')
            for name in sub_names:
                child = element.get(name)
                if not child:
                    raise Exception(f'{element} has no member "{name}"')
                element = child
            return element

        metadata = MetaData()
        metadata.data_by_prop_by_element = {
            get_element(qname): data_by_prop
            for qname, data_by_prop in data_by_prop_by_qname.items()}
        return metadata









@_abstract
class UnionType(TypeExpression):
    
    def __init__(self, bases):
        self.bases = bases
        
    def __repr__(self):
        return '<' + ' | '.join(repr(b) for b in self.bases) + '>'

class UnionClass(ClassExpression, UnionType):
    pass

class UnionDataType(DataTypeExpression, UnionType):
    pass


@_abstract
class TypeTemplateParameterBinding(Element):
    
    def __init__(self, parameter, type: TypeExpression):
        super().__init__()
        self.parameter = parameter
        self.type = type
        
        
    @property
    def info(self):
        parts = [self.parameter.name, '=', repr(self.type)]
        return ''.join(parts)



class ClassTemplateParameterBinding(TypeTemplateParameterBinding):
    pass
    


class DataTypeTemplateParameterBinding(TypeTemplateParameterBinding):
    pass




@_abstract
class BoundType(TypeExpression):
    
    def __init__(self, base: Type, bindings: T.Iterable[TypeTemplateParameterBinding]):
        super().__init__()
        self.base = base
        self.bindings = tuple(bindings)
        
    @property
    def info(self):
        bindings_info = ', '.join(binding.info for binding in self.bindings)
        return f'{self.base.info} with {bindings_info}'
    
    
    def __hash__(self):
        return hash(self.info)
    
    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return False
        return self.info == other.info



class BoundClass(BoundType, ClassExpression):
    pass


class BoundDataType(BoundType, DataTypeExpression):
    pass
    






def type_conjunction(type_expressions):
    if all(isinstance(type_expression, DataTypeExpression) for type_expression in type_expressions):
        union_type = UnionDataType
    else:
        TODO
        
    base_types = []
    for type_expr in type_expressions:
        if isinstance(type_expr, union_type):
            base_types.extend(type_expr.bases)
        else:
            base_types.append(type_expr)
            
    return union_type(base_types)

            
            
    
class ModelSet:
    
    def __init__(self):
        self._model_by_name = {}
        
        
    def __iter__(self):
        return iter(self._model_by_name.values())
    
    def __getitem__(self, name):
        return self._model_by_name[name]
        
    def add(self, model: Model):
        if model.name in self._model_by_name:
            raise Exception(f'model with name {model.name} already added')
        self._model_by_name[model.name] = model
        
    
    def search_iter(self, name: str, type: T.Type[NamedElement]=NamedElement):
        # TODO: better depth-first? check also in Namespace.search_iter
        for model in self._model_by_name.values():
            if model.name == name and isinstance(model, type):
                yield model
            yield from model.search_iter(name, type)
                
    def search_unique(self, name: str, type: T.Type[NamedElement]=NamedElement, default=NO_DEFAULT):
        members = list(self.search_iter(name, type))
        if not members:
            if default is NO_DEFAULT:
                raise KeyError(f'no model has a descendant {name}')
            else:
                return default
        if len(members) > 1:
            raise KeyError(f'models contain more than one descendant {name}')
        return members[0]