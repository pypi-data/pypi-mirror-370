"""Plugin system base classes for tree-sitter-chunker.

This module provides the plugin interface that wraps around the language
configuration system from Phase 2.1.
"""

from __future__ import annotations

import logging
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from chunker.types import CodeChunk

if TYPE_CHECKING:
    from pathlib import Path

    from tree_sitter import Node, Parser

    from .base import LanguageConfig
logger = logging.getLogger(__name__)


@dataclass
class PluginConfig:
    """Configuration for a language plugin."""

    enabled: bool = True
    chunk_types: set[str] | None = None
    min_chunk_size: int = 1
    max_chunk_size: int | None = None
    custom_options: dict[str, Any] = None

    def __post_init__(self):
        if self.custom_options is None:
            self.custom_options = {}


class LanguagePlugin(ABC):
    """Abstract base class for language-specific chunking plugins.

    This wraps around the LanguageConfig system to provide backward
    compatibility with the plugin architecture.
    """

    PLUGIN_API_VERSION = "1.0"

    def __init__(self, config: PluginConfig | None = None):
        self.config = config or PluginConfig()
        self._parser: Parser | None = None
        self._language_config: LanguageConfig | None = None
        self._validate_plugin()

    @staticmethod
    @property
    @abstractmethod
    def language_name() -> str:
        """Return the language identifier (e.g., 'python', 'rust')."""

    @staticmethod
    @property
    @abstractmethod
    def supported_extensions() -> set[str]:
        """Return set of file extensions this plugin handles (e.g., {'.py', '.pyi'})."""

    @property
    def chunk_node_types(self) -> set[str]:
        """Return set of tree-sitter node types to chunk."""
        if self.config.chunk_types:
            return self.config.chunk_types
        return self.default_chunk_types

    @staticmethod
    @property
    @abstractmethod
    def default_chunk_types() -> set[str]:
        """Return default set of node types to chunk for this language."""

    @property
    def plugin_version(self) -> str:
        """Return the plugin version. Override in subclasses."""
        return "1.0.0"

    @property
    def minimum_api_version(self) -> str:
        """Return minimum required API version. Override if needed."""
        return "1.0"

    @property
    def plugin_metadata(self) -> dict[str, Any]:
        """Return plugin metadata. Override to add custom metadata."""

        def _resolve(value: Any) -> Any:
            # Handle @staticmethod @property patterns gracefully
            try:
                if isinstance(value, (set, list, tuple)):
                    return value
                if isinstance(value, str):
                    return value
                if callable(value):
                    return value()
            except Exception:
                return value
            return value

        extensions = _resolve(self.supported_extensions)
        if isinstance(extensions, property):
            try:
                extensions = extensions.fget(self) if extensions.fget else []
            except Exception:
                extensions = []
        chunk_types = _resolve(self.default_chunk_types)
        if isinstance(chunk_types, property):
            try:
                chunk_types = chunk_types.fget(self) if chunk_types.fget else []
            except Exception:
                chunk_types = []
        return {
            "name": self.__class__.__name__,
            "language": _resolve(self.language_name),
            "version": self.plugin_version,
            "api_version": self.minimum_api_version,
            "extensions": list(extensions) if extensions is not None else [],
            "chunk_types": list(chunk_types) if chunk_types is not None else [],
        }

    def set_parser(self, parser: Parser) -> None:
        """Set the tree-sitter parser for this plugin."""
        self._parser = parser

    def process_node(
        self,
        node: Node,
        source: bytes,
        file_path: str,
        parent_context: str | None = None,
    ) -> CodeChunk | None:
        """
        Process a single node into a chunk.

        Args:
            node: Tree-sitter node to process
            source: Source code bytes
            file_path: Path to the source file
            parent_context: Context from parent node (e.g., class name for methods)

        Returns:
            CodeChunk if node should be chunked, None otherwise
        """
        if node.type not in self.chunk_node_types:
            return None
        chunk = self.create_chunk(node, source, file_path, parent_context)
        if chunk and self.should_include_chunk(chunk):
            return chunk
        return None

    def create_chunk(
        self,
        node: Node,
        source: bytes,
        file_path: str,
        parent_context: str | None = None,
    ) -> CodeChunk:
        """Create a CodeChunk from a node. Can be overridden for custom behavior."""
        content = source[node.start_byte : node.end_byte].decode(
            "utf-8",
            errors="replace",
        )
        return CodeChunk(
            language=self.language_name,
            file_path=file_path,
            node_type=node.type,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            byte_start=node.start_byte,
            byte_end=node.end_byte,
            parent_context=parent_context or "",
            content=content,
        )

    def should_include_chunk(self, chunk: CodeChunk) -> bool:
        """Apply filters to determine if chunk should be included."""
        lines = chunk.end_line - chunk.start_line + 1
        if lines < self.config.min_chunk_size:
            return False
        return not (self.config.max_chunk_size and lines > self.config.max_chunk_size)

    def walk_tree(
        self,
        node: Node,
        source: bytes,
        file_path: str,
        parent_context: str | None = None,
    ) -> list[CodeChunk]:
        """
        Recursively walk the tree and extract chunks.

        Args:
            node: Current tree-sitter node
            source: Source code bytes
            file_path: Path to the source file
            parent_context: Context from parent node

        Returns:
            List of CodeChunk objects
        """
        chunks: list[CodeChunk] = []
        chunk = self.process_node(node, source, file_path, parent_context)
        if chunk:
            chunks.append(chunk)
            parent_context = self.get_context_for_children(node, chunk)
        for child in node.children:
            chunks.extend(self.walk_tree(child, source, file_path, parent_context))
        return chunks

    @staticmethod
    def get_context_for_children(_node: Node, chunk: CodeChunk) -> str:
        """
        Get context string to pass to children nodes.
        Can be overridden for language-specific context building.
        """
        return chunk.node_type

    def chunk_file(self, file_path: Path) -> list[CodeChunk]:
        """Parse a file and return chunks."""
        if not self._parser:
            raise RuntimeError(f"Parser not set for {self.language_name} plugin")
        source = file_path.read_bytes()
        tree = self._parser.parse(source)
        return self.walk_tree(tree.root_node, source, str(file_path))

    @staticmethod
    @abstractmethod
    def get_node_name(node: Node, source: bytes) -> str | None:
        """
        Extract a human-readable name from a node (e.g., function name).
        Used for better context building.
        """

    def _validate_plugin(self) -> None:
        """Validate plugin compatibility and requirements."""
        if not self._is_api_compatible():
            raise RuntimeError(
                f"Plugin {self.__class__.__name__} requires API version {self.minimum_api_version} but system provides {self.PLUGIN_API_VERSION}",
            )
        try:
            _ = self.language_name
            _ = self.supported_extensions
            _ = self.default_chunk_types
        except (OSError, subprocess.SubprocessError) as e:
            raise RuntimeError(
                f"Plugin {self.__class__.__name__} failed validation: {e}",
            ) from e
        logger.debug(
            "Plugin %s v%s validated successfully for language '%s'",
            self.__class__.__name__,
            self.plugin_version,
            self.language_name,
        )

    def _is_api_compatible(self) -> bool:
        """Check if plugin is compatible with current API version."""

        def parse_version(version: str) -> tuple[int, int]:
            """Parse version string to tuple of (major, minor)."""
            parts = version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            return major, minor

        current_version = parse_version(self.PLUGIN_API_VERSION)
        required_version = parse_version(self.minimum_api_version)
        return (
            current_version[0] == required_version[0]
            and current_version[1] >= required_version[1]
        )
