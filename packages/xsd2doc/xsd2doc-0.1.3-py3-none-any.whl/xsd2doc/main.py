import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from rich import print
from jinja2 import Template

from xsd2doc.log import TermMessage
from xsd2doc.parse import validate_xsd, parse_xsd, XSDParsed
from xsd2doc.markdown import (
    generate_notes_stub,
    get_markdown_template_dynamic,
    render_markdown_template_dynamic,
    write_rendered_markdown_dynamic,
    get_static_existing,
    merge_notes,
    write_rendered_markdown_static,
)


def prog_exit(code: int = 0, message: Optional[str] = None):
    fmt = None
    # =====
    if message:
        if code == 0:
            fmt = '[sea_green1]Program exited successfully: [/sea_green1]"{}"'.format(
                message
            )
        elif code == 1:
            fmt = "[red]Error: [/red]{}".format(message)
    # =====
    if fmt:
        print(fmt)
    exit(code)


@dataclass
class ProgArgs:
    input_files: list["FileMap"]
    output_dir: Path
    fragment_dir: Path

    # =====
    @dataclass
    class FileMap:
        raw_input_file: Path
        fragment_file_static: Path
        fragment_file_dynamic: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="XSD to markdown docs generator")
    # ===== begin args
    groupio = parser.add_argument_group(title="I/O", description="Program Input/Output")
    groupio.add_argument(
        "--input",
        "-i",
        type=str,
        help="Path(s) to the input XSD file(s)",
        required=True,
        nargs="+",
    )
    groupio.add_argument(
        "--output", "-o", type=str, help="Path to the output directory", default="."
    )
    groupio.add_argument(
        "--fragment-dir",
        "-fd",
        type=str,
        help="Override the default fragment-dir name. (default={outputdir}/fragments)",
        default="fragments",
    )

    grouproutine = parser.add_argument_group(
        title="Routines", description="Program routines"
    )
    grouproutine.add_argument(
        "--generate-notes",
        "-gn",
        action="store_true",
        help="Generate note stubs to be hand-completed.",
    )
    grouproutine.add_argument(
        "--generate-docs",
        "-gd",
        action="store_true",
        help="Generate documentation from XSD files and notes.",
    )

    # ===== end args
    return parser.parse_args()


# ====================


def routine_generate_notes(prog_args: ProgArgs) -> int:
    for file in prog_args.input_files:
        TermMessage.write_msg(
            TermMessage.TYPE.INFO, f"Processing file: {file.raw_input_file}"
        )
        validate_res = validate_xsd(file_path=file.raw_input_file)
        if not validate_res:
            TermMessage.write_msg(
                TermMessage.TYPE.WARN,
                f"Skipping file {file.raw_input_file} due to validation errors.",
            )
            continue

        parse_res: Optional[XSDParsed] = parse_xsd(file_path=file.raw_input_file)
        if not parse_res:
            TermMessage.write_msg(
                TermMessage.TYPE.WARN,
                f"Skipping file {file.raw_input_file} due to parsing errors.",
            )
            continue

        # setup output dependencies
        if not prog_args.fragment_dir.is_dir():
            TermMessage.write_msg(
                TermMessage.TYPE.INFO,
                "Specified fragment directory ({}) does not exist; creating.".format(
                    prog_args.output_dir
                ),
            )
            prog_args.fragment_dir.mkdir(parents=True, exist_ok=True)

        if not file.fragment_file_static.exists():
            file.fragment_file_static.touch()
            TermMessage.write_msg(
                TermMessage.TYPE.INFO,
                f"Touched file: {file.fragment_file_static}.\n\t(This is where you should write notes)",
            )
        parsed_data: XSDParsed = parse_res
        existing = get_static_existing(file.fragment_file_static)
        stub = generate_notes_stub(parsed_data=parsed_data)
        merged = merge_notes(existing=existing, stub=stub)
        write_res = write_rendered_markdown_static(file.fragment_file_static, merged)
    return 0


def routine_generate_docs(prog_args: ProgArgs) -> int:

    # =====
    for file in prog_args.input_files:
        # collect and format into types
        TermMessage.write_msg(
            TermMessage.TYPE.INFO, f"Processing file: {file.raw_input_file}"
        )
        validate_res = validate_xsd(file_path=file.raw_input_file)
        if not validate_res:
            TermMessage.write_msg(
                TermMessage.TYPE.WARN,
                f"Skipping file {file.raw_input_file} due to validation errors.",
            )
            continue

        parse_res: Optional[XSDParsed] = parse_xsd(file_path=file.raw_input_file)
        if not parse_res:
            TermMessage.write_msg(
                TermMessage.TYPE.WARN,
                f"Skipping file {file.raw_input_file} due to parsing errors.",
            )
            continue

        # setup output dependencies
        if not prog_args.output_dir.is_dir():
            TermMessage.write_msg(
                TermMessage.TYPE.INFO,
                "Specified output directory ({}) does not exist; creating.".format(
                    prog_args.output_dir
                ),
            )
            prog_args.output_dir.mkdir(parents=True, exist_ok=True)
        if not prog_args.fragment_dir.is_dir():
            TermMessage.write_msg(
                TermMessage.TYPE.INFO,
                "Specified fragment directory ({}) does not exist; creating.".format(
                    prog_args.output_dir
                ),
            )
            prog_args.fragment_dir.mkdir(parents=True, exist_ok=True)
        if file.fragment_file_dynamic.exists():
            TermMessage.write_msg(
                TermMessage.TYPE.INFO,
                f"File: '{file.fragment_file_dynamic}' already exists. Contents will be overwritten.",
            )
        else:
            file.fragment_file_dynamic.touch()
            TermMessage.write_msg(
                TermMessage.TYPE.INFO, f"Touched file: {file.fragment_file_dynamic}"
            )
        if not file.fragment_file_static.exists():
            file.fragment_file_static.touch()
            TermMessage.write_msg(
                TermMessage.TYPE.INFO,
                f"Touched file: {file.fragment_file_static}.\n\t(This is where you should write notes)",
            )


        parsed_data: XSDParsed = parse_res
        dynamic_template: Template = get_markdown_template_dynamic()
        
        existing = get_static_existing(file.fragment_file_static)
        if not existing:
            TermMessage.write_msg(TermMessage.TYPE.WARN, f"No notes could be found for file: {file.fragment_file_static}")
        static_parts = existing or {}
        markdown_str = render_markdown_template_dynamic(
            template=dynamic_template, parsed_data=parsed_data, static_parts=static_parts
        )
        write_dynamic_res = write_rendered_markdown_dynamic(
            file_path=file.fragment_file_dynamic, rendered_markdown=markdown_str
        )

    return 0


# ====================
def main():
    args = parse_args()
    # ===== arg sanitization
    input_files: list[Path] = [Path(f) for f in args.input]
    for f in input_files:
        if not f.exists():
            prog_exit(message=f"Input file '{f}' does not exist", code=1)
    output_dir: Path = Path(args.output).resolve()
    if not output_dir.exists():
        prog_exit(message=f"Output directory '{output_dir}' does not exist", code=1)

    fragment_dir = args.output / Path(args.fragment_dir).resolve()
    output_maps: List[ProgArgs.FileMap] = []
    for f in input_files:
        file_static = (fragment_dir / f.stem).with_suffix(".static.md")
        file_dynamic = (fragment_dir / f.stem).with_suffix(".dynamic.md")
        output_maps.append(
            ProgArgs.FileMap(
                raw_input_file=f,
                fragment_file_static=file_static,
                fragment_file_dynamic=file_dynamic,
            )
        )
    # =====
    prog_args = ProgArgs(
        input_files=output_maps,
        output_dir=output_dir,
        fragment_dir=fragment_dir,
    )
    # =====
    if args.generate_notes:
        TermMessage.write_msg(
            TermMessage.TYPE.INFO, "Generating note stubs from XSD files..."
        )
        res: int = routine_generate_notes(prog_args=prog_args)
        if res == 0:
            prog_exit(message="Documentation generation completed succesfully.", code=0)
    elif args.generate_docs:
        TermMessage.write_msg(
            TermMessage.TYPE.INFO, "Generating documentation from XSD files..."
        )
        res: int = routine_generate_docs(prog_args=prog_args)
        if res == 0:
            prog_exit(
                message="Documentation generation completed successfully.", code=0
            )


if __name__ == "__main__":
    main()
