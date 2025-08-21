"""
Support for Python language.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ChunkRule, LanguageConfig
from .plugin_base import LanguagePlugin

if TYPE_CHECKING:
    from tree_sitter import Node


class PythonConfig(LanguageConfig):
    """Language configuration for Python."""

    @property
    def language_id(self) -> str:
        return "python"

    @property
    def chunk_types(self) -> set[str]:
        """Python-specific chunk types."""
        return {"function_definition", "class_definition", "decorated_definition"}

    @property
    def file_extensions(self) -> set[str]:
        return {".py", ".pyw", ".pyi"}

    def __init__(self):
        super().__init__()
        self.add_chunk_rule(
            ChunkRule(
                node_types={"lambda"},
                include_children=False,
                priority=5,
                metadata={"type": "lambda_function"},
            ),
        )
        self.add_ignore_type("comment")
        self.add_ignore_type("string")


# Register the Python configuration
from .base import language_config_registry

python_config = PythonConfig()
language_config_registry.register(python_config, aliases=["py", "python3"])


class PythonPlugin(LanguagePlugin):
    """Plugin for Python language chunking."""

    @property
    def language_name(self) -> str:
        return "python"

    @property
    def supported_extensions(self) -> set[str]:
        return {".py", ".pyi"}

    @property
    def default_chunk_types(self) -> set[str]:
        return {
            "function_definition",
            "async_function_definition",
            "class_definition",
            "decorated_definition",
        }

    @staticmethod
    def get_node_name(node: Node, source: bytes) -> str | None:
        """Extract the name from a Python node."""
        for child in node.children:
            if child.type == "identifier":
                return source[child.start_byte : child.end_byte].decode("utf-8")
        return None

    def get_context_for_children(self, node: Node, chunk) -> str:
        """Build context string for nested definitions."""
        name = self.get_node_name(node, chunk.content.encode("utf-8"))
        if not name:
            return chunk.parent_context
        if chunk.parent_context:
            return f"{chunk.parent_context}.{name}"
        return name

    def process_node(
        self,
        node: Node,
        source: bytes,
        file_path: str,
        parent_context: str | None = None,
    ):
        """Process Python nodes with special handling for decorated definitions."""
        if node.type == "decorated_definition":
            for child in node.children:
                if child.type in {
                    "function_definition",
                    "async_function_definition",
                    "class_definition",
                }:
                    chunk = self.create_chunk(node, source, file_path, parent_context)
                    if chunk and self.should_include_chunk(chunk):
                        chunk.node_type = f"decorated_{child.type}"
                        return chunk
            return None
        if (
            node.type == "async_function_definition"
            and self.config.custom_options.get(
                "include_docstrings",
                True,
            )
            and PythonPlugin._has_docstring(node)
        ):
            chunk = self.create_chunk(node, source, file_path, parent_context)
            if chunk:
                chunk.node_type = "async_function_with_docstring"
                return chunk if self.should_include_chunk(chunk) else None
        return super().process_node(node, source, file_path, parent_context)

    @staticmethod
    def _has_docstring(node: Node) -> bool:
        """Check if a function or class has a docstring."""
        body = PythonPlugin._get_body_node(node)
        if not body or not body.children:
            return False

        first_stmt = body.children[0]
        if first_stmt.type != "expression_statement":
            return False

        return any(child.type == "string" for child in first_stmt.children)

    @staticmethod
    def _get_body_node(node: Node) -> Node | None:
        """Get the body node from a function or class."""
        for child in node.children:
            if child.type == "block":
                return child
        return None
