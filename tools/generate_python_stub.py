#!/usr/bin/env python3
#
# Copyright (C) 2019 Simmo Saan <simmo.saan@gmail.com>
# Copyright (C) 2021-2024 Sébastien Helleu <flashcode@flashtux.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""
Generate Python stub: API constants and functions, with type annotations.

This script requires Python 3.6+.
"""

from pathlib import Path
from textwrap import indent

import re

DOC_DIR = Path(__file__).resolve().parent.parent / "doc" / "en"
SRC_DIR = Path(__file__).resolve().parent.parent / "src"

STUB_HEADER = """\
#
# WeeChat Python stub file, auto-generated by generate_python_stub.py.
# DO NOT EDIT BY HAND!
#

from typing import Dict, Union
"""

CONSTANT_RE = (
    r"WEECHAT_SCRIPT_CONST_(?P<type>(INT|STR))\((?P<constant>WEECHAT_[A-Z0-9_]+)\)"
)

FUNCTION_RE = r"""\[source,python\]
----
# prototype
def (?P<function>\w+)(?P<args>[^)]*)(?P<return>\) -> [^:]+:) \.\.\.(?P<example>.*?)
----"""


def print_stub_constants() -> None:
    """Print constants, extracted from the plugin-script.c."""
    constant_pattern = re.compile(CONSTANT_RE)
    with open(
        SRC_DIR / "plugins" / "plugin-script.c", encoding="utf-8"
    ) as plugin_script_file, open(
        SRC_DIR / "plugins" / "weechat-plugin.h", encoding="utf-8"
    ) as plugin_public_header_file:
        plugin_script = plugin_script_file.read()
        plugin_public_header = plugin_public_header_file.read()
        for match in constant_pattern.finditer(plugin_script):
            value_re = rf'^#define {match["constant"]} +(?P<value>[\w"-]+)$'
            value_match = re.search(value_re, plugin_public_header, re.MULTILINE)
            value = f' = {value_match["value"]}' if value_match else ""
            print(f'{match["constant"]}: {match["type"].lower()}{value}')


def print_stub_functions() -> None:
    """Print function prototypes, extracted from the Plugin API reference."""
    function_pattern = re.compile(FUNCTION_RE, re.DOTALL)
    with open(DOC_DIR / "weechat_plugin_api.en.adoc",
              encoding="utf-8") as api_doc_file:
        api_doc = api_doc_file.read()
        for match in function_pattern.finditer(api_doc):
            url = f'https://weechat.org/doc/weechat/api/#_{match["function"]}'
            example = (
                f'\n    ::\n\n{indent(match["example"].lstrip(), " " * 8)}'
                if match["example"]
                else ""
            )
            print(
                f"""\n
def {match["function"]}{match["args"]}{match["return"]}
    \"""`{match["function"]} in WeeChat plugin API reference <{url}>`_{example}
    \"""
    ..."""
            )


def stub_api() -> None:
    """Write Python stub file."""
    print(STUB_HEADER)
    print_stub_constants()
    print_stub_functions()


if __name__ == "__main__":
    stub_api()