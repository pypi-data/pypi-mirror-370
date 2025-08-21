"""Go language plugin."""

from tree_sitter import Node

from .base import ChunkRule, LanguageConfig, language_config_registry
from .plugin_base import LanguagePlugin


class GoPlugin(LanguagePlugin):
    """Plugin for Go language support."""

    @property
    def language_name(self) -> str:
        return "go"

    @property
    def file_extensions(self) -> list[str]:
        return [".go"]

    @staticmethod
    def get_chunk_node_types() -> set[str]:
        return {
            "function_declaration",
            "method_declaration",
            "type_declaration",
            "type_spec",
            "const_declaration",
            "var_declaration",
        }

    @staticmethod
    def get_scope_node_types() -> set[str]:
        return {
            "source_file",
            "function_declaration",
            "method_declaration",
            "block",
            "if_statement",
            "for_statement",
            "switch_statement",
        }

    def should_chunk_node(self, node: Node) -> bool:
        """Determine if node should be chunked."""
        if node.type not in self.get_chunk_node_types():
            return False
        if node.type == "function_declaration":
            name_node = node.child_by_field_name("name")
            if not name_node or not name_node.text:
                return False
        if node.type == "type_spec":
            for child in node.children:
                if child.type in {"struct_type", "interface_type"}:
                    return True
            return False
        return True

    @staticmethod
    def extract_display_name(node: Node, _source: bytes) -> str:
        """Extract display name for chunk."""
        if node.type in {"function_declaration", "method_declaration"}:
            return GoPlugin._extract_function_display_name(node)
        if node.type in {"type_declaration", "type_spec"}:
            return GoPlugin._extract_type_display_name(node)
        return node.text.decode("utf-8")[:50]

    @staticmethod
    def _extract_function_display_name(node: Node) -> str:
        """Extract display name for function or method."""
        name_node = node.child_by_field_name("name")
        if not name_node:
            return node.text.decode("utf-8")[:50]

        name = name_node.text.decode("utf-8")
        if node.type != "method_declaration":
            return name

        # Extract receiver type for methods
        receiver_type = GoPlugin._extract_receiver_type(node)
        if receiver_type:
            return f"({receiver_type}) {name}"
        return name

    @staticmethod
    def _extract_receiver_type(node: Node) -> str | None:
        """Extract receiver type from method declaration."""
        params = node.child_by_field_name("parameters")
        if not params or params.child_count == 0:
            return None

        receiver = params.children[0]
        if receiver.type != "parameter_declaration":
            return None

        type_node = receiver.child_by_field_name("type")
        if type_node:
            return type_node.text.decode("utf-8")
        return None

    @staticmethod
    def _extract_type_display_name(node: Node) -> str:
        """Extract display name for type declaration."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return name_node.text.decode("utf-8")
        return node.text.decode("utf-8")[:50]


class GoConfig(LanguageConfig):
    """Go language configuration."""

    def __init__(self):
        super().__init__()
        self._chunk_rules = [
            ChunkRule(
                node_types={"function_declaration", "method_declaration"},
                include_children=True,
                priority=1,
                metadata={
                    "name": "functions",
                    "min_lines": 1,
                    "max_lines": 500,
                },
            ),
            ChunkRule(
                node_types={"type_declaration", "type_spec"},
                include_children=True,
                priority=1,
                metadata={"name": "types", "min_lines": 1, "max_lines": 300},
            ),
            ChunkRule(
                node_types={"const_declaration"},
                include_children=True,
                priority=1,
                metadata={
                    "name": "constants",
                    "min_lines": 1,
                    "max_lines": 100,
                },
            ),
            ChunkRule(
                node_types={"var_declaration"},
                include_children=True,
                priority=1,
                metadata={"name": "variables", "min_lines": 1, "max_lines": 50},
            ),
        ]
        self._scope_node_types = {
            "source_file",
            "function_declaration",
            "method_declaration",
            "block",
        }
        self._file_extensions = {".go"}

    @property
    def language_id(self) -> str:
        """Return the Go language identifier."""
        return "go"

    @property
    def chunk_types(self) -> set[str]:
        """Return the set of node types that should be treated as chunks."""
        chunk_types = set()
        for rule in self._chunk_rules:
            chunk_types.update(rule.node_types)
        return chunk_types

    @property
    def file_extensions(self) -> set[str]:
        """Return Go file extensions."""
        return self._file_extensions


go_config = GoConfig()
language_config_registry.register(go_config)
