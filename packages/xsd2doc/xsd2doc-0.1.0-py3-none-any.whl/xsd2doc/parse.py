from lxml import etree  # type: ignore
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import io
from rich import print

from xsd2doc.log import TermMessage


XSDNAMESPACES = {"xs": "http://www.w3.org/2001/XMLSchema"}

TAG_IS_ELEMENT = f"{{{XSDNAMESPACES['xs']}}}element"


@dataclass
class XSDNode:
    name: str
    node_type: str
    min_occurs: str = "1"
    max_occurs: str = "1"
    children: List[Any] = field(default_factory=list)
    children_groups: List[Any] = field(default_factory=list)
    attributes: List["XSDAttribute"] = field(default_factory=list)
    attribute_groups: List[Any] = field(default_factory=list)


@dataclass
class XSDAttribute:
    name: str
    attr_type: str
    use: str
    default: Optional[str] = None


# =====


@dataclass
class GroupInfo:
    name: str
    definition: str
    referenced_by: List[str] = field(default_factory=list)
    vals: List[XSDNode] = field(default_factory=list)


@dataclass
class AttributeGroupInfo:
    name: str
    definition: str
    referenced_by: List[str] = field(default_factory=list)
    vals: List[XSDAttribute] = field(default_factory=list)


# =====


@dataclass
class XSDParsed:
    all_elements: Dict[str, XSDNode] = field(default_factory=dict)
    all_element_groups: Dict[str, GroupInfo] = field(default_factory=dict)
    all_attribute_groups: Dict[str, AttributeGroupInfo] = field(default_factory=dict)


# ====================


def build_lookup_tables(root: etree._Element, namespaces: Dict[str, str]):
    global_elements = {
        elem.get("name"): elem
        for elem in root.xpath("//xs:element[@name]", namespaces=namespaces)
    }
    global_complex_types = {
        ct.get("name"): ct
        for ct in root.xpath("//xs:complexType[@name]", namespaces=namespaces)
    }
    global_groups = {
        group.get("name"): group
        for group in root.xpath("//xs:group[@name]", namespaces=namespaces)
    }
    global_attribute_groups = {
        ag.get("name"): ag
        for ag in root.xpath("//xs:attributeGroup[@name]", namespaces=namespaces)
    }
    return global_elements, global_complex_types, global_groups, global_attribute_groups


def parse_attributes(parent_element, namespaces, global_attribute_groups):
    attributes = []
    for attr in parent_element.xpath(".//xs:attribute", namespaces=namespaces):
        attributes.append(
            XSDAttribute(
                name=attr.get("name"),
                attr_type=attr.get("type"),
                use=attr.get("use"),
                default=attr.get("default"),
            )
        )
    for attr_group_ref in parent_element.xpath(
        "./xs:attributeGroup[@ref]", namespaces=namespaces
    ):
        ref_name = attr_group_ref.get("ref")
        if ref_name in global_attribute_groups:
            attributes.extend(
                parse_attributes(
                    global_attribute_groups[ref_name],
                    namespaces,
                    global_attribute_groups,
                )
            )
    return attributes


def collect_group_references(
    root: etree._Element, namespaces: Dict[str, str], lookup_tables
):
    global_elements, global_complex_types, global_groups, global_attribute_groups = (
        lookup_tables
    )
    # ===== element group data
    element_group_references = {}
    for name, group in global_groups.items():
        elements = group.xpath(
            ".//xs:element[@ref] | .//xs:element[@name]", namespaces=namespaces
        )
        nodes = []
        for elem in elements:
            nodes.append(
                XSDNode(
                    name=elem.get("ref") or elem.get("name"),
                    node_type=elem.tag,
                    min_occurs=elem.get("min_occurs"),
                    max_occurs=elem.get("max_occurs"),
                )
            )
        element_group_references[name] = GroupInfo(
            name=name, definition=global_groups[name], referenced_by=[], vals=nodes
        )

    # ===== attribute group data
    attribute_group_references = {}
    for name, group in global_attribute_groups.items():
        elements = group.xpath(
            ".//xs:attribute[@ref] | .//xs:attribute[@name]", namespaces=namespaces
        )
        nodes = []
        for elem in elements:
            nodes.append(
                XSDAttribute(
                    name=elem.get("ref") or elem.get("name"),
                    attr_type=elem.get("type"),
                    use=elem.get("use"),
                    default=elem.get("default")
                )
            )
        attribute_group_references[name] = AttributeGroupInfo(
            name=name, definition=global_attribute_groups[name], referenced_by=[], vals=nodes
        )




    for ref_element in root.xpath("//xs:group[@ref]", namespaces=namespaces):
        ref_name = ref_element.get("ref")
        parent_elem = ref_element.xpath(
            "ancestor::xs:element[1]", namespaces=namespaces
        )[0]
        if parent_elem is not None:
            parent_name = parent_elem.get("name")
            if ref_name in element_group_references and parent_name:
                element_group_references[ref_name].referenced_by.append(parent_name)

    for ref_attribute_group in root.xpath(
        "//xs:attributeGroup[@ref]", namespaces=namespaces
    ):
        ref_name = ref_attribute_group.get("ref")
        parent_elem = ref_attribute_group.xpath(
            "ancestor::xs:element[1]", namespaces=namespaces
        )[0]
        if parent_elem is not None:
            parent_name = parent_elem.get("name")
            if ref_name in attribute_group_references and parent_name:
                attribute_group_references[ref_name].referenced_by.append(parent_name)

    return element_group_references, attribute_group_references


# ====================


def validate_xsd(file_path: Path) -> bool:
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()
        assert tree is not None, "Parsed tree is None"
        return True
    except etree.XMLSyntaxError as e:
        TermMessage.write_msg(
            TermMessage.TYPE.ERROR, f"XML Syntax Error in {file_path}: {e}"
        )
        return False
    except Exception as e:
        TermMessage.write_msg(
            TermMessage.TYPE.ERROR, f"Error processing {file_path}: {e}"
        )
        return False


def parse_xsd(file_path: Path) -> Optional[XSDParsed]:
    try:
        namespaces = XSDNAMESPACES
        tree = etree.parse(file_path)
        root = tree.getroot()
        lookup_tables = build_lookup_tables(root=tree, namespaces=namespaces)
        (
            global_elements,
            global_complex_types,
            global_groups,
            global_attribute_groups,
        ) = lookup_tables
        group_refs, attr_group_refs = collect_group_references(
            tree, namespaces, lookup_tables
        )
        # =====
        # build up all of the individual elements and attributes.
        all_elements: Dict[str, XSDNode] = {}
        for elem in root.xpath("//xs:element", namespaces=namespaces):
            name = elem.get("name")
            if not name:
                continue

            # ===== children
            child_elems = elem.xpath(
                ".//xs:element[not(@name=$parent_name)]",
                namespaces=namespaces,
                parent_name=name,
            )
            child_names = [child.get("name") or child.get("ref") for child in child_elems]
            child_groups = elem.xpath(
                "./xs:complexType//xs:group[@ref] | ./xs:simpleType//xs:group[@ref]",
                namespaces=namespaces,
            )
            xsd_child_groups = [
                g.get("ref") for g in child_groups if g.get("ref") in global_groups
            ]

            # ===== attributes
            direct_attrs = elem.xpath(
                "./xs:complexType/xs:attribute",
                namespaces=namespaces,
            )
            xsd_attrs = []
            for attr in direct_attrs:
                xsd_attrs.append(
                    XSDAttribute(
                        name=attr.get("name"),
                        attr_type=attr.get("type"),
                        use=attr.get("use"),
                    )
                )
            attribute_groups = elem.xpath(
                "./xs:complexType/xs:attributeGroup", namespaces=namespaces
            )
            xsd_attr_groups = [
                g.get("ref")
                for g in attribute_groups
                if g.get("ref") in global_attribute_groups
            ]
            # =====
            all_elements[name] = XSDNode(
                name=name,
                node_type=elem.tag,
                children=child_names,
                children_groups=xsd_child_groups,
                attributes=xsd_attrs,
                attribute_groups=xsd_attr_groups,
            )
        # ======
        return XSDParsed(
            all_elements=all_elements,
            all_element_groups=group_refs,
            all_attribute_groups=attr_group_refs,
        )
    except Exception as e:
        TermMessage.write_msg(TermMessage.TYPE.ERROR, f"Error parsing {file_path}: {e}")
        raise (e)
