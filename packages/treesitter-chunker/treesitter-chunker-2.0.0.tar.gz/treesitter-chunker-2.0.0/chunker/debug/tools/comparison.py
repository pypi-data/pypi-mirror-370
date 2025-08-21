"""
Chunk comparison implementation
"""

from pathlib import Path
from typing import Any

from chunker.contracts.debug_contract import ChunkComparisonContract
from chunker.core import chunk_file
from chunker.fallback.fallback_manager import FallbackManager
from chunker.parser import get_parser
from chunker.strategies import (
    AdaptiveChunker,
    CompositeChunker,
    HierarchicalChunker,
    SemanticChunker,
)
from chunker.token.chunker import TreeSitterTokenAwareChunker
from chunker.token.counter import TiktokenCounter


class ChunkComparison(ChunkComparisonContract):
    """Implementation of chunk comparison contract"""

    def compare_strategies(
        self,
        file_path: str,
        language: str,
        strategies: list[str],
    ) -> dict[str, Any]:
        """
        Compare different chunking strategies on the same file

        Args:
            file_path: Path to source file
            language: Programming language
            strategies: List of strategy names to compare

        Returns:
            Comparison data including chunk counts, sizes, overlaps
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        strategy_map = {
            "default": self._chunk_default,
            "adaptive": self._chunk_adaptive,
            "composite": self._chunk_composite,
            "hierarchical": self._chunk_hierarchical,
            "semantic": self._chunk_semantic,
            "token_aware": self._chunk_token_aware,
            "fallback": self._chunk_fallback,
        }
        for strategy in strategies:
            if strategy not in strategy_map:
                raise ValueError(
                    f"Unknown strategy: {strategy}. Available: {list(strategy_map.keys())}",
                )
        results = {}
        all_chunks = {}
        errors = []

        # Process all strategies, collecting errors
        for strategy in strategies:
            try:
                chunks = strategy_map[strategy](file_path, language)
                all_chunks[strategy] = chunks
                chunk_sizes = [(c.end_line - c.start_line + 1) for c in chunks]
                byte_sizes = [(c.byte_end - c.byte_start) for c in chunks]
                results[strategy] = {
                    "chunk_count": len(chunks),
                    "total_lines": sum(chunk_sizes),
                    "average_lines": (
                        sum(chunk_sizes) / len(chunk_sizes) if chunks else 0
                    ),
                    "min_lines": min(chunk_sizes) if chunks else 0,
                    "max_lines": max(chunk_sizes) if chunks else 0,
                    "average_bytes": sum(byte_sizes) / len(byte_sizes) if chunks else 0,
                    "chunks": [
                        {
                            "id": c.chunk_id,
                            "type": c.node_type,
                            "lines": f"{c.start_line}-{c.end_line}",
                            "size": c.end_line - c.start_line + 1,
                        }
                        for c in chunks
                    ],
                }
            except (IndexError, KeyError, TypeError) as e:
                errors.append((strategy, e))

        # Process errors after loop
        for strategy, error in errors:
            results[strategy] = {"error": str(error), "chunk_count": 0}
            all_chunks[strategy] = []
        overlaps = {}
        for i, strat1 in enumerate(strategies):
            if strat1 not in all_chunks:
                continue
            for strat2 in strategies[i + 1 :]:
                if strat2 not in all_chunks:
                    continue
                overlap_count = self._calculate_overlap(
                    all_chunks[strat1],
                    all_chunks[strat2],
                )
                overlaps[f"{strat1}_vs_{strat2}"] = {
                    "overlapping_chunks": overlap_count,
                    "similarity": (
                        overlap_count
                        / max(len(all_chunks[strat1]), len(all_chunks[strat2]))
                        if all_chunks[strat1] or all_chunks[strat2]
                        else 0
                    ),
                }
        differences = []
        if len(strategies) == 2 and all(s in all_chunks for s in strategies):
            chunks1 = all_chunks[strategies[0]]
            chunks2 = all_chunks[strategies[1]]
            differences.extend(
                {
                    "strategy": strategies[0],
                    "unique_chunk": {
                        "type": c1.node_type,
                        "lines": f"{c1.start_line}-{c1.end_line}",
                    },
                }
                for c1 in chunks1
                if not any(self._chunks_overlap(c1, c2) for c2 in chunks2)
            )
            differences.extend(
                {
                    "strategy": strategies[1],
                    "unique_chunk": {
                        "type": c2.node_type,
                        "lines": f"{c2.start_line}-{c2.end_line}",
                    },
                }
                for c2 in chunks2
                if not any(self._chunks_overlap(c1, c2) for c1 in chunks1)
            )
        return {
            "file_path": file_path,
            "language": language,
            "strategies": results,
            "overlaps": overlaps,
            "differences": differences[:10],
            "summary": {
                "total_strategies": len(strategies),
                "successful": sum(1 for r in results.values() if "error" not in r),
                "failed": sum(1 for r in results.values() if "error" in r),
            },
        }

    @staticmethod
    def _chunk_default(file_path: str, language: str):
        """Use default chunking strategy"""
        return chunk_file(file_path, language)

    @classmethod
    def _chunk_adaptive(cls, file_path: str, language: str):
        """Use adaptive chunking strategy"""
        chunker = AdaptiveChunker()
        with open(file_path, "rb") as f:
            src = f.read()
        ast = get_parser(language).parse(src).root_node
        return chunker.chunk(ast, src, file_path, language)

    @classmethod
    def _chunk_composite(cls, file_path: str, language: str):
        """Use composite chunking strategy"""
        chunker = CompositeChunker()
        with open(file_path, "rb") as f:
            src = f.read()
        ast = get_parser(language).parse(src).root_node
        return chunker.chunk(ast, src, file_path, language)

    @classmethod
    def _chunk_hierarchical(cls, file_path: str, language: str):
        """Use hierarchical chunking strategy"""
        chunker = HierarchicalChunker()
        with open(file_path, "rb") as f:
            src = f.read()
        ast = get_parser(language).parse(src).root_node
        return chunker.chunk(ast, src, file_path, language)

    @classmethod
    def _chunk_semantic(cls, file_path: str, language: str):
        """Use semantic chunking strategy"""
        chunker = SemanticChunker()
        with open(file_path, "rb") as f:
            src = f.read()
        ast = get_parser(language).parse(src).root_node
        return chunker.chunk(ast, src, file_path, language)

    @classmethod
    def _chunk_token_aware(cls, file_path: str, language: str):
        """Use token-aware chunking strategy"""
        counter = TiktokenCounter()
        chunker = TreeSitterTokenAwareChunker(token_counter=counter, max_tokens=1000)
        return chunker.chunk_file(file_path, language)

    @classmethod
    def _chunk_fallback(cls, file_path: str, _language: str):
        """Use fallback chunking for unsupported files"""
        manager = FallbackManager()
        return manager.chunk_file(file_path)

    def _calculate_overlap(self, chunks1, chunks2):
        """Calculate number of overlapping chunks between two sets"""
        overlap_count = 0
        for c1 in chunks1:
            for c2 in chunks2:
                if self._chunks_overlap(c1, c2):
                    overlap_count += 1
                    break
        return overlap_count

    @staticmethod
    def _chunks_overlap(chunk1, chunk2):
        """Check if two chunks overlap"""
        return not (
            chunk1.end_line < chunk2.start_line or chunk2.end_line < chunk1.start_line
        )
