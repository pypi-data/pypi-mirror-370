"""Java language plugin."""

from tree_sitter import Node

from .base import ChunkRule, LanguageConfig, language_config_registry
from .plugin_base import LanguagePlugin


class JavaPlugin(LanguagePlugin):
    """Plugin for Java language support."""

    @property
    def language_name(self) -> str:
        return "java"

    @property
    def file_extensions(self) -> list[str]:
        return [".java"]

    @staticmethod
    def get_chunk_node_types() -> set[str]:
        return {
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "annotation_type_declaration",
            "record_declaration",
            "method_declaration",
            "constructor_declaration",
            "field_declaration",
            "static_initializer",
        }

    @staticmethod
    def get_scope_node_types() -> set[str]:
        return {
            "program",
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "method_declaration",
            "constructor_declaration",
            "block",
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement",
            "switch_expression",
            "lambda_expression",
        }

    def should_chunk_node(self, node: Node) -> bool:
        """Determine if node should be chunked."""
        if node.type not in self.get_chunk_node_types():
            return False
        if node.type == "static_initializer":
            body = node.child_by_field_name("body")
            if body and body.child_count <= 2:
                return False
        if node.type == "constructor_declaration":
            body = node.child_by_field_name("body")
            if body and body.child_count <= 2:
                return False
        return True

    @staticmethod
    def extract_display_name(node: Node, _source: bytes) -> str:
        """Extract display name for chunk."""
        extractors = {
            "class_declaration": JavaPlugin._extract_class_name,
            "interface_declaration": JavaPlugin._extract_interface_name,
            "enum_declaration": JavaPlugin._extract_enum_name,
            "method_declaration": JavaPlugin._extract_method_name,
            "constructor_declaration": JavaPlugin._extract_constructor_name,
            "field_declaration": JavaPlugin._extract_field_name,
            "static_initializer": lambda _: "static { ... }",
            "annotation_declaration": JavaPlugin._extract_annotation_name,
        }

        extractor = extractors.get(node.type)
        if extractor:
            return extractor(node)

        return node.type

    @staticmethod
    def _extract_class_name(node: Node) -> str:
        """Extract class declaration name."""
        name_node = node.child_by_field_name("name")
        if name_node:
            name = name_node.text.decode("utf-8")
            superclass = node.child_by_field_name("superclass")
            if superclass:
                return f"{name} extends {superclass.text.decode('utf-8')}"
            return name
        return "class"

    @staticmethod
    def _extract_interface_name(node: Node) -> str:
        """Extract interface declaration name."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return f"interface {name_node.text.decode('utf-8')}"
        return "interface"

    @staticmethod
    def _extract_enum_name(node: Node) -> str:
        """Extract enum declaration name."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return f"enum {name_node.text.decode('utf-8')}"
        return "enum"

    @staticmethod
    def _extract_method_name(node: Node) -> str:
        """Extract method declaration name."""
        name_node = node.child_by_field_name("name")
        if name_node:
            method_name = name_node.text.decode("utf-8")
            type_node = node.child_by_field_name("type")
            if type_node:
                return f"{type_node.text.decode('utf-8')} {method_name}(...)"
            return f"{method_name}(...)"
        return "method"

    @staticmethod
    def _extract_constructor_name(node: Node) -> str:
        """Extract constructor declaration name."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return f"{name_node.text.decode('utf-8')}(...)"
        return "constructor"

    @staticmethod
    def _extract_field_name(node: Node) -> str:
        """Extract field declaration name."""
        type_node = node.child_by_field_name("type")
        type_str = type_node.text.decode("utf-8") if type_node else "?"
        field_names = []
        for child in node.children:
            if child.type == "variable_declarator":
                name = child.child_by_field_name("name")
                if name:
                    field_names.append(name.text.decode("utf-8"))
        if field_names:
            return f"{type_str} {', '.join(field_names)}"
        return node.text.decode("utf-8")[:50]

    @staticmethod
    def _extract_annotation_name(node: Node) -> str:
        """Extract annotation declaration name."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return f"@interface {name_node.text.decode('utf-8')}"
        return "@interface"


class JavaConfig(LanguageConfig):
    """Java language configuration."""

    def __init__(self):
        super().__init__()
        self._chunk_rules = [
            ChunkRule(
                node_types={
                    "class_declaration",
                    "interface_declaration",
                    "enum_declaration",
                    "annotation_type_declaration",
                    "record_declaration",
                },
                include_children=True,
                priority=1,
                metadata={"name": "classes", "min_lines": 1, "max_lines": 2000},
            ),
            ChunkRule(
                node_types={"method_declaration", "constructor_declaration"},
                include_children=True,
                priority=1,
                metadata={"name": "methods", "min_lines": 1, "max_lines": 500},
            ),
            ChunkRule(
                node_types={"field_declaration"},
                include_children=True,
                priority=1,
                metadata={"name": "fields", "min_lines": 1, "max_lines": 50},
            ),
            ChunkRule(
                node_types={"static_initializer"},
                include_children=True,
                priority=1,
                metadata={"name": "static_blocks", "min_lines": 2, "max_lines": 200},
            ),
        ]
        self._scope_node_types = {
            "program",
            "class_declaration",
            "interface_declaration",
            "enum_declaration",
            "method_declaration",
            "constructor_declaration",
            "block",
        }
        self._file_extensions = {".java"}

    @property
    def language_id(self) -> str:
        """Return the Java language identifier."""
        return "java"

    @property
    def chunk_types(self) -> set[str]:
        """Return the set of node types that should be treated as chunks."""
        chunk_types = set()
        for rule in self._chunk_rules:
            chunk_types.update(rule.node_types)
        return chunk_types

    @property
    def file_extensions(self) -> set[str]:
        """Return Java file extensions."""
        return self._file_extensions


java_config = JavaConfig()
language_config_registry.register(java_config)
