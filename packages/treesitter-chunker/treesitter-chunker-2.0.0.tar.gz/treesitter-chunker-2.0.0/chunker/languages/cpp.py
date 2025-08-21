from __future__ import annotations

from typing import TYPE_CHECKING

from .c import CPlugin

if TYPE_CHECKING:
    from tree_sitter import Node


class CppPlugin(CPlugin):
    """Plugin for C++ language chunking, inheriting from C plugin."""

    @property
    def language_name(self) -> str:
        return "cpp"

    @property
    def supported_extensions(self) -> set[str]:
        return {".cpp", ".cxx", ".cc", ".hpp", ".hxx", ".h", ".hh"}

    @property
    def default_chunk_types(self) -> set[str]:
        c_types = super().default_chunk_types
        cpp_types = {
            "class_specifier",
            "namespace_definition",
            "template_declaration",
            "constructor_definition",
            "destructor_definition",
            "operator_cast_definition",
            "function_definition",
            "field_declaration",
        }
        return c_types | cpp_types

    def get_node_name(self, node: Node, source: bytes) -> str | None:
        """Extract the name from a C++ node."""
        if node.type == "class_specifier":
            for child in node.children:
                if child.type == "type_identifier":
                    return source[child.start_byte : child.end_byte].decode("utf-8")
        elif node.type == "namespace_definition":
            for child in node.children:
                if child.type == "identifier":
                    return source[child.start_byte : child.end_byte].decode("utf-8")
        elif node.type == "template_declaration":
            for child in node.children:
                if child.type in {
                    "class_specifier",
                    "function_definition",
                    "struct_specifier",
                }:
                    return self.get_node_name(child, source)
        elif node.type in {"constructor_definition", "destructor_definition"}:
            for child in node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "qualified_identifier":
                            parts = (
                                source[subchild.start_byte : subchild.end_byte]
                                .decode("utf-8")
                                .split("::")
                            )
                            return parts[-1]
                        if subchild.type == "destructor_name":
                            return source[
                                subchild.start_byte : subchild.end_byte
                            ].decode("utf-8")
        return super().get_node_name(node, source)

    def process_node(
        self,
        node: Node,
        source: bytes,
        file_path: str,
        parent_context: str | None = None,
    ):
        """Process C++ nodes with special handling."""
        if node.type == "field_declaration":
            has_function_declarator = False
            for child in node.children:
                if child.type == "function_declarator":
                    has_function_declarator = True
                    break
            if not has_function_declarator:
                return None
            chunk = self.create_chunk(node, source, file_path, parent_context)
            if chunk and self.should_include_chunk(chunk):
                chunk.node_type = "method_declaration"
                return chunk
        elif node.type == "template_declaration":
            for child in node.children:
                if child.type in self.chunk_node_types:
                    chunk = self.process_node(child, source, file_path, parent_context)
                    if chunk:
                        chunk.node_type = f"template_{chunk.node_type}"
                        chunk.content = source[node.start_byte : node.end_byte].decode(
                            "utf-8",
                            errors="replace",
                        )
                        chunk.byte_start = node.start_byte
                        chunk.byte_end = node.end_byte
                        chunk.start_line = node.start_point[0] + 1
                        chunk.end_line = node.end_point[0] + 1
                        return chunk
            return None
        return super().process_node(node, source, file_path, parent_context)

    def get_context_for_children(self, node: Node, chunk) -> str:
        """Build context string for nested definitions."""
        name = self.get_node_name(node, chunk.content.encode("utf-8"))
        if not name:
            return chunk.parent_context
        if node.type in {"class_specifier", "namespace_definition"}:
            if chunk.parent_context:
                return f"{chunk.parent_context}::{name}"
            return name
        return name
