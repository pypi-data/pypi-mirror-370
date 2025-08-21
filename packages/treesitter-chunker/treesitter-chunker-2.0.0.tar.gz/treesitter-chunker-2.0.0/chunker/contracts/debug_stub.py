from typing import Any

from .debug_contract import ChunkComparisonContract, DebugVisualizationContract


class DebugVisualizationStub(DebugVisualizationContract):
    """Stub implementation that can be instantiated and tested"""

    @staticmethod
    def visualize_ast(
        file_path: str,
        language: str,
        output_format: str = "svg",
    ) -> str | bytes:
        """Stub that returns valid default values"""
        if output_format in {"svg", "dot", "json"}:
            return "Not implemented - Debug Tools team will implement"
        return b"Not implemented - Debug Tools team will implement"

    @staticmethod
    def inspect_chunk(
        file_path: str,
        chunk_id: str,
        include_context: bool = True,
    ) -> dict[str, Any]:
        """Stub that returns valid default values"""
        return {
            "status": "not_implemented",
            "team": "Debug Tools",
            "content": "",
            "metadata": {},
            "boundaries": {"start": 0, "end": 0},
            "relationships": [],
            "tokens": 0,
            "complexity": 0,
            "ast_nodes": [],
        }

    @staticmethod
    def profile_chunking(file_path: str, language: str) -> dict[str, Any]:
        """Stub that returns valid default values"""
        return {
            "status": "not_implemented",
            "team": "Debug Tools",
            "total_time": 0.0,
            "phases": {"parse": 0.0, "chunk": 0.0, "metadata": 0.0},
            "memory_usage": 0.0,
            "chunk_count": 0,
            "bottlenecks": [],
        }

    @staticmethod
    def debug_mode_chunking(
        file_path: str,
        language: str,
        breakpoints: list[str] | None = None,
    ) -> dict[str, Any]:
        """Stub that returns valid default values"""
        return {
            "status": "not_implemented",
            "team": "Debug Tools",
            "trace": [],
            "decisions": [],
            "rules_applied": [],
        }


class ChunkComparisonStub(ChunkComparisonContract):
    """Stub implementation for chunk comparison"""

    @staticmethod
    def compare_strategies(
        file_path: str,
        language: str,
        strategies: list[str],
    ) -> dict[str, Any]:
        """Stub that returns valid default values"""
        return {
            "status": "not_implemented",
            "team": "Debug Tools",
            "comparisons": {},
            "metrics": {"chunk_counts": {}, "sizes": {}, "overlaps": {}},
            "visual_diff": None,
        }
