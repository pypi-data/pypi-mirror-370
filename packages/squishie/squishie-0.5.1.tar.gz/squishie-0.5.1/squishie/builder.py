# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import re
import typing
from pathlib import Path

import frontmatter
import yaml

from .models import Document, PageNode, TreeNode

RE_HEADER = re.compile(r"^(?P<header>[#]+)[ ]+(?P<text>.+)$")


def clamp_header_level(header_level: int) -> int:
    return max(1, min(6, header_level))


def build_header(level: int, title: str, anchor: str = "", attributes: str = "") -> str:
    header = "#" * level

    if anchor:
        text = f"[{title}](#{anchor})"
        if attributes:
            attributes = f"#{anchor} {attributes}"
        else:
            attributes = f"#{anchor}"
    else:
        text = title

    if attributes:
        text += " {" + attributes + "}"

    return f"{header} {text}"


def compute_header_level_adjustment(
    lines: typing.List[str], starting_level: int = 1
) -> int:
    minimum_header_level = None
    for line in lines:
        if line.startswith("#"):
            match = RE_HEADER.match(line)
            if match:
                header_level = clamp_header_level(len(match.group("header")))
                if minimum_header_level is None:
                    minimum_header_level = header_level
                else:
                    minimum_header_level = min(minimum_header_level, header_level)

    if minimum_header_level is None:
        minimum_header_level = starting_level

    target_level = starting_level + 1
    level_adjustment = target_level - minimum_header_level
    return level_adjustment


def adjust_header_level(content: str, starting_level: int = 1) -> str:
    lines = content.splitlines()

    level_adjustment = compute_header_level_adjustment(
        lines=lines, starting_level=starting_level
    )

    newlines = []
    for line in lines:
        newline = line
        if line.startswith("#"):
            match = RE_HEADER.match(line)
            if match:
                header_level = clamp_header_level(
                    len(match.group("header")) + level_adjustment
                )
                newline = build_header(level=header_level, title=match.group("text"))
        newlines.append(newline)
    return "\n".join(newlines)


def build_page_blocks(
    doc_dir: Path, page: PageNode, starting_level: int = 1
) -> typing.List[str]:
    text = open(doc_dir / page.file).read()
    metadata, content = frontmatter.parse(text)

    blocks = []

    title = page.title or metadata.get("title")
    if title and page.show_title:
        blocks.append(
            build_header(
                level=starting_level,
                title=title,
                anchor=page.anchor,
                attributes=page.attributes,
            )
        )
    else:
        starting_level -= 1

    content = adjust_header_level(content, starting_level=starting_level)

    blocks.append(content.rstrip())
    return blocks


def build_tree_blocks(
    doc_dir: Path, tree: TreeNode, starting_level: int = 1
) -> typing.List[str]:
    blocks = []
    if tree.title and tree.show_title:
        blocks.append(
            build_header(
                level=starting_level,
                title=tree.title,
                anchor=tree.anchor,
                attributes=tree.attributes,
            )
        )
    else:
        starting_level -= 1
    for section in tree.sections:
        blocks.extend(
            build_node_blocks(doc_dir, section, starting_level=starting_level + 1)
        )
    return blocks


def filter_metadata(
    metadata: typing.Dict[str, typing.Any],
) -> typing.Dict[str, typing.Any]:
    return {
        key: value
        for key, value in metadata.items()
        if key
        not in (
            "title",
            "version",
        )
    }


def build_node_blocks(
    doc_dir: Path, node: typing.Union[PageNode, TreeNode], starting_level: int = 1
) -> typing.List[str]:
    print(type(node), node)
    return {
        PageNode: build_page_blocks,
        TreeNode: build_tree_blocks,
    }[
        type(node)
    ](doc_dir, node, starting_level=starting_level)


def build_document(doc_dir: Path, document: Document) -> str:
    content = "\n\n".join(
        [
            block
            for section in document.sections
            for block in build_node_blocks(doc_dir, section)
        ]
    )

    metadata = filter_metadata(document.metadata)

    output = ""
    output += "---\n"

    output += yaml.dump(
        dict(
            title=document.title,
            version=document.version,
        )
    )

    if metadata:
        output += "\n# metadata\n"
        output += yaml.dump(metadata)

    output += "---\n\n"

    output += content + "\n"

    return output
