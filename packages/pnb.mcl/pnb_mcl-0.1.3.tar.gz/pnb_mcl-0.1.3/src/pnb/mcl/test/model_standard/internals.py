from unittest import TestCase
from pnb.mcl.metamodel.standard import *


class Test_MembersProperty(TestCase):

    def test_Namespace_members(self):
        self.assertEqual(
            Namespace.members._derived_properties_,
            set())
        self.assertEqual(
            Namespace.members._direct_base_properties,
            {Namespace.importedMembers, Namespace.ownedMembers})
        self.assertEqual(
            Namespace.members._base_properties,
            {Namespace.importedMembers, Namespace.ownedMembers,
             Package.packagedElements,
             Model.packagedElements,
             Enumeration._orderedOwnedLiterals_,
             Class.ownedAttributes,
             AggregatedDataType.ownedAttributes})

    def test_Namespace_ownedMembers(self):
        self.assertEqual(
            Namespace.ownedMembers._derived_properties_,
            {Namespace.members})
        self.assertEqual(
            Namespace.ownedMembers._direct_base_properties,
            {Package.packagedElements,
             Model.packagedElements,
             Enumeration._orderedOwnedLiterals_,
             Class.ownedAttributes,
             AggregatedDataType.ownedAttributes})
        self.assertEqual(
            Namespace.ownedMembers._base_properties,
            {Package.packagedElements,
             Model.packagedElements,
             Enumeration._orderedOwnedLiterals_,
             Class.ownedAttributes,
             AggregatedDataType.ownedAttributes})

    def test_Package_ownedTypes(self):
        self.assertEqual(
            Package.ownedTypes._derived_properties_,
            set())
        self.assertEqual(
            Package.ownedTypes._direct_base_properties,
            {Package.packagedElements})
        self.assertEqual(
            Package.ownedTypes._base_properties,
            {Package.packagedElements})

    def test_Package_packagedElements(self):
        self.assertEqual(
            Package.packagedElements._derived_properties_,
            {Namespace.members, Namespace.ownedMembers,
             Package.ownedTypes})
