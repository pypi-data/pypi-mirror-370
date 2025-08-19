"""Loading nested configs for FMU"""

from __future__ import annotations

import os.path
from collections import OrderedDict
from typing import TYPE_CHECKING

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

if TYPE_CHECKING:
    from types_pyyaml import _Node, _ReadStream


class FmuLoader(yaml.Loader):
    """Class for making it possible to use nested YAML files.

    Code is borrowed from David Hall:
    https://davidchall.github.io/yaml-includes.html
    """

    # pylint: disable=too-many-ancestors

    def __init__(self, stream: _ReadStream) -> None:
        self._root = os.path.split(stream.name)[0]
        super(FmuLoader, self).__init__(stream)

        FmuLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, FmuLoader.construct_mapping
        )

        FmuLoader.add_constructor("!include", FmuLoader.include)
        FmuLoader.add_constructor("!import", FmuLoader.include)

    def include(self, node: _Node) -> list | dict | None:
        """Include method"""

        result: list | dict | None = None
        if isinstance(node, yaml.ScalarNode):
            scalar = self.construct_scalar(node)
            assert isinstance(scalar, str)
            result = self.extract_file(scalar)

        elif isinstance(node, yaml.SequenceNode):
            result = []
            for filename in self.construct_sequence(node):
                result += self.extract_file(filename)

        elif isinstance(node, yaml.MappingNode):
            result = {}
            for knum, val in self.construct_mapping(node).items():
                result[knum] = self.extract_file(val)

        else:
            print("Error:: unrecognised node type in !include statement")
            raise yaml.constructor.ConstructorError

        return result

    def extract_file(self, filename: str) -> dict:
        """Extract file method"""

        filepath = os.path.join(self._root, filename)
        with open(filepath, "r", encoding="utf-8") as yfile:
            return yaml.load(yfile, FmuLoader)

    # from https://gist.github.com/pypt/94d747fe5180851196eb
    def construct_mapping(self, node: _Node, deep: bool = False) -> dict:
        # but changed mapping to OrderedDict
        if not isinstance(node, MappingNode):
            raise ConstructorError(
                None,
                None,
                "Expected a mapping node, but found %s" % node.id,
                node.start_mark,
            )

        self.flatten_mapping(node)
        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise ConstructorError(
                    "While constructing a mapping",
                    node.start_mark,
                    "found unacceptable key (%s)" % exc,
                    key_node.start_mark,
                ) from exc
            # check for duplicate keys
            if key in mapping:
                raise ConstructorError(
                    "Found duplicate key <{}> ... {}".format(key, key_node.start_mark)
                )
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping
