"""Semantic analysis interfaces for intelligent chunk merging and relationship analysis."""

from abc import ABC, abstractmethod

from chunker.types import CodeChunk


class SemanticMerger(ABC):
    """Merge related chunks based on semantic analysis."""

    @staticmethod
    @abstractmethod
    def should_merge(chunk1: CodeChunk, chunk2: CodeChunk) -> bool:
        """
        Determine if two chunks should be merged based on semantic relationship.

        Examples of chunks that should merge:
        - Getter and setter methods
        - Overloaded functions
        - Small related methods in the same class
        - Interface and its implementation

        Args:
            chunk1: First chunk
            chunk2: Second chunk

        Returns:
            True if chunks should be merged
        """

    @staticmethod
    @abstractmethod
    def merge_chunks(chunks: list[CodeChunk]) -> list[CodeChunk]:
        """
        Merge related chunks to reduce fragmentation while preserving semantics.

        Args:
            chunks: List of chunks to potentially merge

        Returns:
            List of chunks after merging related ones
        """

    @staticmethod
    @abstractmethod
    def get_merge_reason(chunk1: CodeChunk, chunk2: CodeChunk) -> str | None:
        """
        Get the reason why two chunks would be merged.

        Args:
            chunk1: First chunk
            chunk2: Second chunk

        Returns:
            Reason for merging or None if they shouldn't merge
        """


class RelationshipAnalyzer(ABC):
    """Analyze relationships between code elements."""

    @staticmethod
    @abstractmethod
    def find_related_chunks(chunks: list[CodeChunk]) -> dict[str, list[str]]:
        """
        Find relationships between chunks.

        Args:
            chunks: List of chunks to analyze

        Returns:
            Dict mapping chunk IDs to lists of related chunk IDs
        """

    @staticmethod
    @abstractmethod
    def find_overloaded_functions(chunks: list[CodeChunk]) -> list[list[CodeChunk]]:
        """
        Find groups of overloaded functions.

        Args:
            chunks: List of chunks to analyze

        Returns:
            List of groups, where each group contains overloaded functions
        """

    @staticmethod
    @abstractmethod
    def find_getter_setter_pairs(
        chunks: list[CodeChunk],
    ) -> list[tuple[CodeChunk, CodeChunk]]:
        """
        Find getter/setter method pairs.

        Args:
            chunks: List of chunks to analyze

        Returns:
            List of (getter, setter) tuples
        """

    @staticmethod
    @abstractmethod
    def find_interface_implementations(chunks: list[CodeChunk]) -> dict[str, list[str]]:
        """
        Find interface/implementation relationships.

        Args:
            chunks: List of chunks to analyze

        Returns:
            Dict mapping interface chunk IDs to implementation chunk IDs
        """

    @staticmethod
    @abstractmethod
    def calculate_cohesion_score(chunk1: CodeChunk, chunk2: CodeChunk) -> float:
        """
        Calculate cohesion score between two chunks (0.0 to 1.0).

        Higher scores indicate stronger relationships.

        Args:
            chunk1: First chunk
            chunk2: Second chunk

        Returns:
            Cohesion score between 0.0 and 1.0
        """
