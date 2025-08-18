# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Union

import attrs


@attrs.frozen
class PageNode:
    file: str

    title: str = ""
    anchor: str = ""
    attributes: str = ""

    show_title: bool = True


@attrs.frozen
class TreeNode:
    title: str

    anchor: str = ""
    attributes: str = ""

    sections: List[Union["TreeNode", PageNode]] = attrs.Factory(list)

    show_title: bool = True


@attrs.frozen
class Document:
    title: str
    version: str

    metadata: Dict[str, Any] = attrs.Factory(dict)

    sections: List[Union[TreeNode, PageNode]] = attrs.Factory(list)
