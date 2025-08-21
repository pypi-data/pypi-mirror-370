"""
Support for OCaml language.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from chunker.contracts.language_plugin_contract import ExtendedLanguagePluginContract

from .base import ChunkRule, LanguageConfig
from .plugin_base import LanguagePlugin

if TYPE_CHECKING:
    from tree_sitter import Node


class OCamlConfig(LanguageConfig):
    """Language configuration for OCaml."""

    @property
    def language_id(self) -> str:
        return "ocaml"

    @property
    def chunk_types(self) -> set[str]:
        """OCaml-specific chunk types."""
        return {
            "value_definition",
            "let_binding",
            "type_definition",
            "type_binding",
            "module_definition",
            "module_binding",
            "exception_definition",
            "class_definition",
            "class_binding",
            "comment",
            "fun_expression",
            "function_expression",
        }

    @property
    def file_extensions(self) -> set[str]:
        return {".ml", ".mli"}

    def __init__(self):
        super().__init__()
        self.add_chunk_rule(
            ChunkRule(
                node_types={"match_expression", "function_expression"},
                include_children=True,
                priority=5,
                metadata={"type": "pattern_matching"},
            ),
        )
        self.add_ignore_type("string")
        self.add_ignore_type("number")
        self.add_ignore_type("constructor")


# Register the OCaml configuration
ocaml_config = OCamlConfig()
from .base import language_config_registry

language_config_registry.register(ocaml_config)


class OCamlPlugin(LanguagePlugin, ExtendedLanguagePluginContract):
    """Plugin for OCaml language chunking."""

    @property
    def language_name(self) -> str:
        return "ocaml"

    @property
    def supported_extensions(self) -> set[str]:
        return {".ml", ".mli"}

    @property
    def default_chunk_types(self) -> set[str]:
        return {
            "value_definition",
            "let_binding",
            "type_definition",
            "type_binding",
            "module_definition",
            "module_binding",
            "exception_definition",
            "class_definition",
            "class_binding",
            "comment",
            "fun_expression",
            "function_expression",
        }

    @staticmethod
    def get_node_name(node: Node, source: bytes) -> str | None:
        """Extract the name from an OCaml node."""
        # Map node types to their name extraction logic
        node_name_extractors = {
            "value_definition": OCamlPlugin._extract_value_name,
            "let_binding": OCamlPlugin._extract_value_name,
            "let_rec_binding": OCamlPlugin._extract_value_name,
            "type_definition": OCamlPlugin._extract_type_name,
            "type_binding": OCamlPlugin._extract_type_name,
            "module_definition": OCamlPlugin._extract_module_name,
            "module_binding": OCamlPlugin._extract_module_name,
            "exception_definition": OCamlPlugin._extract_exception_name,
            "class_definition": OCamlPlugin._extract_class_name,
            "class_binding": OCamlPlugin._extract_class_name,
        }

        extractor = node_name_extractors.get(node.type)
        return extractor(node, source) if extractor else None

    @staticmethod
    def _extract_value_name(node: Node, source: bytes) -> str | None:
        """Extract name from value/let definitions."""
        for child in node.children:
            if child.type == "value_name":
                return source[child.start_byte : child.end_byte].decode("utf-8")
            if child.type == "let_binding":
                for subchild in child.children:
                    if subchild.type == "value_name":
                        return source[subchild.start_byte : subchild.end_byte].decode(
                            "utf-8",
                        )
        return None

    @staticmethod
    def _extract_type_name(node: Node, source: bytes) -> str | None:
        """Extract name from type definitions."""
        for child in node.children:
            if child.type in {"type_constructor", "lowercase_identifier"}:
                return source[child.start_byte : child.end_byte].decode("utf-8")
            if child.type == "type_binding":
                for subchild in child.children:
                    if subchild.type == "type_constructor":
                        return source[subchild.start_byte : subchild.end_byte].decode(
                            "utf-8",
                        )
        return None

    @staticmethod
    def _extract_module_name(node: Node, source: bytes) -> str | None:
        """Extract name from module definitions."""
        for child in node.children:
            if child.type in {"module_name", "uppercase_identifier"}:
                return source[child.start_byte : child.end_byte].decode("utf-8")
            if child.type == "module_binding":
                for subchild in child.children:
                    if subchild.type == "module_name":
                        return source[subchild.start_byte : subchild.end_byte].decode(
                            "utf-8",
                        )
        return None

    @staticmethod
    def _extract_exception_name(node: Node, source: bytes) -> str | None:
        """Extract name from exception definitions."""
        for child in node.children:
            if child.type in {"constructor_name", "uppercase_identifier"}:
                return source[child.start_byte : child.end_byte].decode("utf-8")
            if child.type == "constructor_declaration":
                for subchild in child.children:
                    if subchild.type == "constructor_name":
                        return source[subchild.start_byte : subchild.end_byte].decode(
                            "utf-8",
                        )
        return None

    @staticmethod
    def _extract_class_name(node: Node, source: bytes) -> str | None:
        """Extract name from class definitions."""
        for child in node.children:
            if child.type in {"class_name", "lowercase_identifier"}:
                return source[child.start_byte : child.end_byte].decode("utf-8")
        return None

    def get_semantic_chunks(self, node: Node, source: bytes) -> list[dict[str, any]]:
        """Extract semantic chunks specific to OCaml."""
        chunks = []

        def extract_chunks(n: Node, module_context: str | None = None):
            if n.type in self.default_chunk_types:
                content = source[n.start_byte : n.end_byte].decode(
                    "utf-8",
                    errors="replace",
                )
                chunk = {
                    "type": n.type,
                    "start_line": n.start_point[0] + 1,
                    "end_line": n.end_point[0] + 1,
                    "content": content,
                    "name": self.get_node_name(n, source),
                }
                if module_context:
                    chunk["module"] = module_context
                if n.type in {"let_binding", "let_rec_binding"}:
                    chunk["is_recursive"] = n.type == "let_rec_binding"
                elif n.type == "type_definition":
                    if "=" in content and "|" in content:
                        chunk["type_kind"] = "variant"
                    elif "=" in content and "{" in content:
                        chunk["type_kind"] = "record"
                    else:
                        chunk["type_kind"] = "alias"
                chunks.append(chunk)
                if n.type in {"module_definition", "module_binding"}:
                    module_context = self.get_node_name(n, source)
            for child in n.children:
                extract_chunks(child, module_context)

        extract_chunks(node)
        return chunks

    def get_chunk_node_types(self) -> set[str]:
        """Get OCaml-specific node types that form chunks."""
        return self.default_chunk_types

    @staticmethod
    def should_chunk_node(node: Node) -> bool:
        """Determine if a specific node should be chunked."""
        if node.type.endswith("_definition") or node.type.endswith("_binding"):
            return True
        if node.type in {"fun_expression", "function_expression"}:
            return True
        if node.type in {"signature", "structure"}:
            return True
        return node.type == "comment"

    def get_node_context(self, node: Node, source: bytes) -> str | None:
        """Extract meaningful context for a node."""
        # Map node types to their context format (prefix, default)
        node_context_map = {
            "value_definition": ("let", "let binding"),
            "let_binding": ("let", "let binding"),
            "let_rec_binding": ("let rec", "let rec binding"),
            "type_definition": ("type", "type definition"),
            "type_binding": ("type", "type definition"),
            "module_definition": ("module", "module"),
            "module_binding": ("module", "module"),
            "exception_definition": ("exception", "exception"),
            "class_definition": ("class", "class"),
            "class_binding": ("class", "class"),
            "signature": (None, "module signature"),
            "structure": (None, "module structure"),
        }

        if node.type not in node_context_map:
            return None

        prefix, default = node_context_map[node.type]
        if prefix is None:
            return default

        name = self.get_node_name(node, source)
        return f"{prefix} {name}" if name else default

    def process_node(
        self,
        node: Node,
        source: bytes,
        file_path: str,
        parent_context: str | None = None,
    ):
        """Process OCaml nodes with special handling for nested structures."""
        if node.type in {"module_definition", "module_binding"}:
            chunk = self.create_chunk(node, source, file_path, parent_context)
            if chunk and self.should_include_chunk(chunk):
                module_name = self.get_node_name(node, source)
                if module_name:
                    parent_context = f"module:{module_name}"
                return chunk
        if node.type == "let_rec_binding":
            chunks = []
            main_chunk = self.create_chunk(node, source, file_path, parent_context)
            if main_chunk and self.should_include_chunk(main_chunk):
                chunks.append(main_chunk)
            for child in node.children:
                if child.type == "let_binding":
                    sub_chunk = self.create_chunk(
                        child,
                        source,
                        file_path,
                        parent_context,
                    )
                    if sub_chunk and self.should_include_chunk(sub_chunk):
                        sub_chunk.node_type = "recursive_function"
                        chunks.append(sub_chunk)
            return chunks if chunks else None
        if node.type == "type_definition":
            chunk = self.create_chunk(node, source, file_path, parent_context)
            if chunk and self.should_include_chunk(chunk):
                content = source[node.start_byte : node.end_byte].decode("utf-8")
                if "|" in content:
                    chunk.metadata = {"type_kind": "variant"}
                elif "{" in content and "}" in content:
                    chunk.metadata = {"type_kind": "record"}
                return chunk
        return super().process_node(node, source, file_path, parent_context)

    def get_context_for_children(self, node: Node, chunk) -> str:
        """Build context string for nested definitions."""
        if node.type in {"module_definition", "module_binding"}:
            name = self.get_node_name(node, chunk.content.encode("utf-8"))
            if name:
                return f"module:{name}"
        if node.type in {"class_definition", "class_binding"}:
            name = self.get_node_name(node, chunk.content.encode("utf-8"))
            if name:
                return f"class:{name}"
        return chunk.node_type
