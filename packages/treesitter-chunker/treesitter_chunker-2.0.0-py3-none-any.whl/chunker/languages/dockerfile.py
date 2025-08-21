"""
Support for Dockerfile language.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from chunker.contracts.language_plugin_contract import ExtendedLanguagePluginContract

from .base import ChunkRule, LanguageConfig
from .plugin_base import LanguagePlugin

if TYPE_CHECKING:
    from tree_sitter import Node


class DockerfileConfig(LanguageConfig):
    """Language configuration for Dockerfile."""

    @property
    def language_id(self) -> str:
        return "dockerfile"

    @property
    def chunk_types(self) -> set[str]:
        """Dockerfile-specific chunk types."""
        return {
            "from_instruction",
            "run_instruction",
            "cmd_instruction",
            "entrypoint_instruction",
            "copy_instruction",
            "add_instruction",
            "workdir_instruction",
            "expose_instruction",
            "env_instruction",
            "arg_instruction",
            "label_instruction",
            "user_instruction",
            "volume_instruction",
            "shell_instruction",
            "healthcheck_instruction",
            "stopsignal_instruction",
            "onbuild_instruction",
            "comment",
        }

    @property
    def file_extensions(self) -> set[str]:
        return {".dockerfile", "Dockerfile", ".Dockerfile"}

    def __init__(self):
        super().__init__()
        self.add_chunk_rule(
            ChunkRule(
                node_types={"instruction"},
                include_children=True,
                priority=5,
                metadata={"type": "multi_line_instruction"},
            ),
        )

        # Add rules for multi-line instructions
        self.add_chunk_rule(
            ChunkRule(
                node_types={"instruction"},
                include_children=True,
                priority=5,
                metadata={"type": "multi_line_instruction"},
            ),
        )


# Register the Dockerfile configuration
from .base import language_config_registry

dockerfile_config = DockerfileConfig()
language_config_registry.register(dockerfile_config)


class DockerfilePlugin(LanguagePlugin, ExtendedLanguagePluginContract):
    """Plugin for Dockerfile language chunking."""

    @property
    def language_name(self) -> str:
        return "dockerfile"

    @property
    def supported_extensions(self) -> set[str]:
        return {"Dockerfile", ".dockerfile", ".Dockerfile"}

    @property
    def default_chunk_types(self) -> set[str]:
        return {
            "from_instruction",
            "run_instruction",
            "cmd_instruction",
            "entrypoint_instruction",
            "copy_instruction",
            "add_instruction",
            "workdir_instruction",
            "expose_instruction",
            "env_instruction",
            "arg_instruction",
            "label_instruction",
            "user_instruction",
            "volume_instruction",
            "shell_instruction",
            "healthcheck_instruction",
            "stopsignal_instruction",
            "onbuild_instruction",
            "comment",
        }

    @staticmethod
    def get_node_name(node: Node, source: bytes) -> str | None:
        """Extract the instruction name from a Dockerfile node."""
        if node.type.endswith("_instruction"):
            for child in node.children:
                if child.type in {"from", "run", "cmd", "copy", "add", "env", "arg"}:
                    return (
                        source[child.start_byte : child.end_byte]
                        .decode("utf-8")
                        .upper()
                    )
        elif node.type == "comment":
            return "COMMENT"
        return None

    def get_semantic_chunks(self, node: Node, source: bytes) -> list[dict[str, any]]:
        """Extract semantic chunks specific to Dockerfile."""
        chunks = []

        def extract_chunks(n: Node, _parent_type: str | None = None):
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
                    "instruction": self.get_node_name(n, source),
                }
                chunks.append(chunk)
            for child in n.children:
                extract_chunks(child, n.type)

        extract_chunks(node)
        return chunks

    def get_chunk_node_types(self) -> set[str]:
        """Get Dockerfile-specific node types that form chunks."""
        return self.default_chunk_types

    @staticmethod
    def should_chunk_node(node: Node) -> bool:
        """Determine if a specific node should be chunked."""
        if node.type.endswith("_instruction"):
            return True
        return node.type == "comment"

    def get_node_context(self, node: Node, source: bytes) -> str | None:
        """Extract meaningful context for a node."""
        if node.type == "from_instruction":
            for child in node.children:
                if child.type == "image_spec":
                    return f"FROM {source[child.start_byte:child.end_byte].decode('utf-8')}"
        elif node.type.endswith("_instruction"):
            instruction = self.get_node_name(node, source)
            return f"{instruction} instruction"
        return None
