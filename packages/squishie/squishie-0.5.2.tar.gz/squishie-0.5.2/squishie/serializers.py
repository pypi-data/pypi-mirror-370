# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import typing

import cattrs
import yaml

from .models import Document, PageNode, TreeNode

_CONVERTER = cattrs.Converter()


def _structure_section(object, __):
    return _CONVERTER.structure(object, TreeNode if "sections" in object else PageNode)


_CONVERTER.register_structure_hook(
    typing.Union[TreeNode, PageNode],
    _structure_section,
)

_CONVERTER.register_structure_hook(
    typing.Union["TreeNode", PageNode],
    _structure_section,
)


def load_document(file: typing.IO):
    data = yaml.safe_load(file)
    return _CONVERTER.structure(data, Document)
