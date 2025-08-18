# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from squishie.builder import build_document, clamp_header_level
from squishie.serializers import load_document

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_clamp_header_level():
    assert clamp_header_level(-2) == 1
    assert clamp_header_level(0) == 1
    assert clamp_header_level(1) == 1
    assert clamp_header_level(3) == 3
    assert clamp_header_level(6) == 6
    assert clamp_header_level(7) == 6


def test_load_document():
    document_file = FIXTURE_DIR / "minimal" / "squishie.yaml"
    document = load_document(open(document_file))
    assert document.title == "My squished document"
    assert document.version == "1.2.3"
    assert document.sections[0].file == "doc1.md"
    assert document.sections[1].file == "doc2.md"


def test_build_document():
    document_file = FIXTURE_DIR / "minimal" / "squishie.yaml"
    document = load_document(open(document_file))
    output = build_document(FIXTURE_DIR / "minimal", document)
    expected = """---
title: My squished document
version: 1.2.3

# metadata
baz: true
foo: bar
---

# [My Title](#different-title) {#different-title}

This is some text.

## A header

More text.

# Doc 2

This is different text.

## More header

This is text.

# [Subsection](#subanchor) {#subanchor .text-red}

## Doc 3 {.text-blue}

### Header

#### Header

##### Header

###### Header

###### Header

###### Header

More text.

## [Subsubsection](#subsubanchor) {#subsubanchor}

### Doc 4

#### Header

##### Header

###### Header

More text.

# Doc 5

## Header

More text.
"""
    assert output == expected
