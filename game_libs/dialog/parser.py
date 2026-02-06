#-*- coding: utf-8 -*-

"""dialog.parser
___________________________________________________________________________________________________
Parser for the dialog XML-like format.
___________________________________________________________________________________________________
(c) Lafiteau Franck 2026
"""

# import built-in modules
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, TypeAlias
import re

# import game_libs
from game_libs.dialog.component import Dialog, DialogParagraph, DialogOption, DialogGoto


DIALOG_OPEN_RE = re.compile(r"<dialog\s+\"([^\"]+)\">\s*")
DIALOG_CLOSE = "</dialog>"
PARAGRAPH_OPEN = "<paragraph>"
PARAGRAPH_CLOSE = "</paragraph>"
CHOICE_OPEN = "<choice>"
CHOICE_CLOSE = "</choice>"
OPTION_OPEN_RE = re.compile(r"<option\s+\"([^\"]+)\">\s*")
OPTION_CLOSE = "</option>"
GOTO_RE = re.compile(r"<goto\s+\"([^\"]+)\"\s*/>\s*")


@dataclass
class ParagraphBlock:
    lines: list[str]


@dataclass
class GotoBlock:
    target: str


@dataclass
class OptionBlock:
    name: str
    blocks: list[Block]


@dataclass
class ChoiceBlock:
    prompt: Optional[ParagraphBlock]
    options: list[OptionBlock]


Block: TypeAlias = ParagraphBlock | ChoiceBlock | GotoBlock


def parse_dialog_file(file_path: str) -> dict[str, Dialog]:
    """
    Parse dialogs from a file and return a dict of dialog name to Dialog tree.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return parse_dialogs(content)


def parse_dialogs(content: str) -> dict[str, Dialog]:
    """
    Parse dialogs from a string and return a dict of dialog name to Dialog tree.
    """
    lines = content.splitlines()
    dialog_blocks: dict[str, list[Block]] = {}
    index = 0

    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        match = DIALOG_OPEN_RE.match(line)
        if match:
            name = match.group(1)
            index += 1
            blocks, index = _parse_blocks(lines, index, DIALOG_CLOSE)
            dialog_blocks[name] = blocks
            continue
        raise ValueError(f"Unexpected line outside dialog: {line}")

    return _build_dialogs(dialog_blocks)


def _parse_blocks(lines: list[str], start_index: int, end_tag: str) -> tuple[list[Block], int]:
    blocks: list[Block] = []
    index = start_index

    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == end_tag:
            return blocks, index + 1
        if line == PARAGRAPH_OPEN:
            paragraph, index = _parse_paragraph(lines, index + 1)
            blocks.append(paragraph)
            continue
        if line == CHOICE_OPEN:
            choice, index = _parse_choice(lines, index + 1)
            blocks.append(choice)
            continue
        goto_match = GOTO_RE.match(line)
        if goto_match:
            blocks.append(GotoBlock(goto_match.group(1)))
            index += 1
            continue
        raise ValueError(f"Unexpected line: {line}")

    raise ValueError(f"Missing end tag: {end_tag}")


def _parse_paragraph(lines: list[str], start_index: int) -> tuple[ParagraphBlock, int]:
    paragraph_lines: list[str] = []
    index = start_index

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped == PARAGRAPH_CLOSE:
            return ParagraphBlock(paragraph_lines), index + 1
        paragraph_lines.append(stripped)
        index += 1

    raise ValueError("Missing </paragraph> tag")


def _parse_choice(lines: list[str], start_index: int) -> tuple[ChoiceBlock, int]:
    prompt: Optional[ParagraphBlock] = None
    options: list[OptionBlock] = []
    index = start_index

    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line == CHOICE_CLOSE:
            return ChoiceBlock(prompt, options), index + 1
        if line == PARAGRAPH_OPEN:
            if prompt is not None:
                raise ValueError("Choice block cannot contain more than one paragraph.")
            prompt, index = _parse_paragraph(lines, index + 1)
            continue
        option_match = OPTION_OPEN_RE.match(line)
        if option_match:
            name = option_match.group(1)
            blocks, index = _parse_blocks(lines, index + 1, OPTION_CLOSE)
            options.append(OptionBlock(name, blocks))
            continue
        raise ValueError(f"Unexpected line in choice: {line}")

    raise ValueError("Missing </choice> tag")


def _build_dialogs(dialog_blocks: dict[str, list[Block]]) -> dict[str, Dialog]:
    """Build dialogs using DialogGoto nodes for references."""
    built: dict[str, Dialog] = {}

    def build_dialog(name: str) -> Dialog:
        if name in built:
            return built[name]
        if name not in dialog_blocks:
            raise ValueError(f"Unknown dialog referenced: {name}")
        
        dialog = _build_sequence(dialog_blocks[name])
        built[name] = dialog
        return dialog

    # Build all dialogs
    for dialog_name in dialog_blocks:
        build_dialog(dialog_name)

    return built


def _build_sequence(blocks: list[Block]) -> Dialog:
    current: Optional[Dialog] = None

    for block in blocks:
        next_dialog = _build_block(block)
        if current is None:
            current = next_dialog
        else:
            current = current >> next_dialog

    return current if current is not None else Dialog(None, [])


def _build_block(block: Block) -> Dialog:
    if isinstance(block, ParagraphBlock):
        return Dialog(DialogParagraph(block.lines), [])
    if isinstance(block, ChoiceBlock):
        prompt_lines = block.prompt.lines if block.prompt else []
        option_names = [option.name for option in block.options]
        option_node = DialogParagraph(prompt_lines) @ option_names
        branches: list[Dialog] = []
        for option in block.options:
            if not option.blocks:
                branches.append(Dialog(None, []))
                continue
            branches.append(_build_sequence(option.blocks))
        return option_node // branches
    if isinstance(block, GotoBlock):
        # Create a DialogGoto node instead of cloning
        return Dialog(DialogGoto(block.target), [])
    raise TypeError(f"Unsupported block type: {type(block)}")
