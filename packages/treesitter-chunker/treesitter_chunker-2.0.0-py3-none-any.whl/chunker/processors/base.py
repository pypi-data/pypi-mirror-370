"""Base interface for specialized processors.

This module defines the SpecializedProcessor interface that all
file-type-specific processors must implement.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from chunker.types import CodeChunk


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata.

    Used by processors that handle non-code text formats.
    """

    content: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    metadata: dict[str, Any]
    chunk_type: str = "text"

    @property
    def line_count(self) -> int:
        """Number of lines in this chunk."""
        return self.end_line - self.start_line + 1

    @property
    def byte_size(self) -> int:
        """Size of chunk in bytes."""
        return self.end_byte - self.start_byte


@dataclass
class ProcessorConfig:
    """Configuration for specialized processors.

    Attributes:
        chunk_size: Target chunk size in lines
        preserve_structure: Whether to preserve file structure
        include_comments: Whether to include comments in chunks
        group_related: Whether to group related items
        format_specific: Format-specific configuration
    """

    chunk_size: int = 50
    # Optional constraints used by some processors/tests
    min_chunk_size: int | None = None
    max_chunk_size: int | None = None
    overlap_size: int | None = None
    preserve_structure: bool = True
    include_comments: bool = True
    group_related: bool = True
    format_specific: dict[str, Any] = None

    def __post_init__(self):
        if self.format_specific is None:
            self.format_specific = {}


class SpecializedProcessor(ABC):
    """Base interface for specialized file processors.

    Each processor handles a specific file type or fmt,
    providing intelligent chunking that preserves the
    semantic structure of the content.

    Note: This base class supports two different interfaces:
    1. The structured approach (detect_format, parse_structure, chunk_content)
       used by ConfigProcessor
    2. The simple approach (process) used by LogProcessor and others

    Processors should implement one of these approaches.
    """

    def __init__(self, config: ProcessorConfig | dict[str, Any] | None = None):
        """Initialize processor with configuration.

        Args:
            config: Processor configuration (ProcessorConfig or dict)
        """
        if isinstance(config, dict):
            # Allow dict to map directly onto ProcessorConfig fields when present
            cfg = ProcessorConfig()
            for key, value in config.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, value)
                else:
                    # Unknown keys go into format_specific
                    if cfg.format_specific is None:
                        cfg.format_specific = {}
                    cfg.format_specific[key] = value
            self.config = cfg
        else:
            self.config = config or ProcessorConfig()

    @staticmethod
    @abstractmethod
    def can_handle(file_path: str, content: str | None = None) -> bool:
        """Check if this processor can handle the given file.

        Args:
            file_path: Path to the file
            content: Optional file content for detection

        Returns:
            True if this processor can handle the file
        """

    def can_process(
        self,
        file_path: str | Path,
        content: str | None = None,
    ) -> bool:
        """Alias for can_handle to support different interfaces."""
        return self.can_handle(str(file_path), content)

    @staticmethod
    def detect_format(_file_path: str, _content: str) -> str | None:
        """Detect the specific fmt of the file.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            Format identifier (e.g., 'ini', 'toml', 'yaml') or None
        """
        return None

    @staticmethod
    def parse_structure(_content: str, _format: str) -> dict[str, Any]:
        """Parse the file structure.

        Args:
            content: File content
            fmt: Detected fmt

        Returns:
            Parsed structure representation
        """
        return {}

    @staticmethod
    def chunk_content(
        _content: str,
        _structure: dict[str, Any],
        _file_path: str,
    ) -> list[CodeChunk]:
        """Chunk the content based on its structure.

        Args:
            content: File content
            structure: Parsed structure
            file_path: Path to the file

        Returns:
            List of code chunks
        """
        return []

    def process(self, file_path: str, content: str) -> list[CodeChunk | TextChunk]:
        """Process a file and return chunks.

        This is the main entry point that orchestrates the processing.
        Can be overridden by processors that use a different approach.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of chunks (CodeChunk or TextChunk)
        """
        fmt = self.detect_format(file_path, content)
        if fmt is not None:
            structure = self.parse_structure(content, fmt)
            chunks = self.chunk_content(content, structure, file_path)
            return chunks
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement either the structured approach (detect_format, parse_structure, chunk_content) or override the process method",
        )

    def process_file(
        self,
        file_path: str | Path,
        config: dict[str, Any] | None = None,
    ) -> list[TextChunk]:
        """Process a file and return text chunks.

        This method supports the LogProcessor interface.

        Args:
            file_path: Path to the file
            config: Optional configuration overrides

        Returns:
            List of text chunks
        """
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()
        if config:
            old_config = self.config.format_specific
            self.config.format_specific.update(config)
        try:
            chunks = self.process(str(file_path), content)
            text_chunks = []
            for chunk in chunks:
                if isinstance(chunk, CodeChunk):
                    text_chunk = TextChunk(
                        content=chunk.content,
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                        start_byte=chunk.byte_start,
                        end_byte=chunk.byte_end,
                        metadata=chunk.metadata,
                        chunk_type=chunk.node_type,
                    )
                    text_chunks.append(text_chunk)
                else:
                    text_chunks.append(chunk)
            return text_chunks
        finally:
            if config:
                self.config.format_specific = old_config

    def process_stream(
        self,
        stream: Iterator[str],
        file_path: Path | None = None,
    ) -> Iterator[TextChunk]:
        """Process content from a stream.

        Args:
            stream: Iterator yielding lines or chunks of text
            file_path: Optional file path for context

        Yields:
            Text chunks as they are processed
        """
        content = "".join(stream)
        chunks = self.process(str(file_path) if file_path else "", content)
        for chunk in chunks:
            if isinstance(chunk, TextChunk):
                yield chunk

    @staticmethod
    def get_supported_formats() -> list[str]:
        """Get list of supported file formats.

        Returns:
            List of fmt identifiers
        """
        return []

    @staticmethod
    def get_format_extensions() -> dict[str, list[str]]:
        """Get file extensions for each fmt.

        Returns:
            Mapping of fmt to list of extensions
        """
        return {}

    def get_metadata(self) -> dict[str, Any]:
        """Get processor metadata.

        Returns:
            Dictionary with processor information
        """
        return {
            "name": self.__class__.__name__,
            "supported_formats": self.get_supported_formats(),
            "config": self.config,
        }
