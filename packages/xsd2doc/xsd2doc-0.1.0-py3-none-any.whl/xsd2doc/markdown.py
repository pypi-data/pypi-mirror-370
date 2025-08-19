from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import importlib.resources as resources

from xsd2doc.parse import XSDParsed
from xsd2doc.log import TermMessage


# ====================

def generate_notes_stub(parsed_data: XSDParsed) -> Dict[str, Any]:
    stub: Dict[str, Any] = {}
    for elem_name, elem in parsed_data.all_elements.items():
        stub.setdefault(elem_name, {})
        for c in elem.children:
            stub[elem_name].setdefault(c, "")
        for attr in elem.attributes:
            stub[elem_name].setdefault(attr.name, "")
    for group_name, group_info in parsed_data.all_element_groups.items():
        stub.setdefault(group_name, {})
        for val in group_info.vals:
            stub[group_name].setdefault(val.name, "")
    for attr_group_name, attr_group_info in parsed_data.all_attribute_groups.items():
        stub.setdefault(attr_group_name, {})
        for attr in attr_group_info.vals:
            stub[attr_group_name].setdefault(attr.name, "")

    return stub

def generate_notes_stub_old(parsed_data: XSDParsed, static_file: Path) -> Dict[str, Any]:
    notes: Dict[str, Any] = {}
    for elem_name, elem in parsed_data.all_elements.items():
        notes[elem_name] = {}
        for attr in elem.attributes:
            notes[elem_name][attr.name] = "TODO: describe this attribute."

        for group_name in elem.attribute_groups:
            notes[elem_name][group_name] = "TODO: describe this attribute group."

    for group_name, group in parsed_data.all_element_groups.items():
        notes[group_name] = {}
        for val in group.vals:
            notes[group_name][val.name] = "TODO: describe this group element."

    for attr_group_name, attr_group in parsed_data.all_attribute_groups.items():
        notes[attr_group_name] = {}
        for attr in attr_group.vals:
            notes[attr_group_name][attr.name] = "TODO: describe this group attribute."


    return notes

def get_static_existing(static_file: Path) -> Optional[Dict[str, Any]]:
    if not static_file.exists():
        return None
    try:
        with open(static_file, "r") as f:
            existing = yaml.safe_load(f)
        return existing
    except Exception as e:
        TermMessage.write_msg(TermMessage.TYPE.ERROR, f"Error opening existing .static file: {e}")
        return None

def merge_notes(existing, stub: Dict[str, Any]) -> Dict[str, Any]:
    for key, val in stub.items():
        if key not in existing:
            existing[key] = val
        else:
            for sub_key, sub_val in val.items():
                existing[key].setdefault(sub_key, sub_val)
    return existing

def write_rendered_markdown_static(static_file: Path, data: Dict[str, Any]):
    with open(static_file, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

# ====================

def get_markdown_template_dynamic() -> Template:
    templates_pkg = "xsd2doc.templates"
    filename="template-dynamic.md.j2"

    with resources.as_file(resources.files(templates_pkg)) as templates_path:
        env = Environment(
            loader = FileSystemLoader(str(templates_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template(filename)
        return template

def render_markdown_template_dynamic(template: Template, parsed_data: XSDParsed, static_parts: Dict[str, Any]) -> str:
    return template.render(parsed_data=parsed_data, notes=static_parts)


def write_rendered_markdown_dynamic(file_path: Path, rendered_markdown: str) -> bool:
    try:
        file_path.write_text(rendered_markdown, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error writing markdown to {file_path}: {e}")
        return False


# ====================
