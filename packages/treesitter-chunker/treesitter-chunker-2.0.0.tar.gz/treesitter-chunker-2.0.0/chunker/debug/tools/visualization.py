"""
Debug visualization implementation
"""

import json
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Any

import graphviz

from chunker.contracts.debug_contract import DebugVisualizationContract
from chunker.core import chunk_file
from chunker.debug.visualization.ast_visualizer import ASTVisualizer
from chunker.languages import language_config_registry
from chunker.parser import get_parser


class DebugVisualization(DebugVisualizationContract):
    """Implementation of debug visualization contract"""

    @classmethod
    def visualize_ast(
        cls,
        file_path: str,
        language: str,
        output_format: str = "svg",
    ) -> str | bytes:
        """
        Generate visual representation of the AST for a file

        Args:
            file_path: Path to source file
            language: Programming language
            output_format: Output format (svg, png, dot, json, text)

        Returns:
            Visualization data in requested format
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if output_format not in {"svg", "png", "dot", "json", "text"}:
            raise ValueError(f"Unsupported format: {output_format}")
        try:
            chunks = chunk_file(file_path, language)
        except (FileNotFoundError, IndexError, KeyError):
            chunks = None
        visualizer = ASTVisualizer(language)
        if output_format == "text":
            result = visualizer.visualize_file(
                file_path,
                output_format="json",
                chunks=chunks,
            )
            return result if isinstance(result, str) else json.dumps(result)
        if output_format == "json":
            result = visualizer.visualize_file(
                file_path,
                output_format="json",
                chunks=chunks,
            )
            return result if isinstance(result, str) else json.dumps(result)
        if output_format in {"svg", "png", "dot"}:
            graph_source = visualizer.visualize_file(
                file_path,
                output_format="graph",
                chunks=chunks,
            )
            if output_format == "dot":
                return graph_source
            try:
                dot = graphviz.Source(graph_source)
                dot.format = output_format
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=f".{output_format}",
                ) as tmp:
                    dot.render(tmp.name.replace(f".{output_format}", ""), cleanup=True)
                    result_path = tmp.name
                with Path(result_path).open(
                    "rb" if output_format == "png" else "r",
                ) as f:
                    result = f.read()
                Path(result_path).unlink()
                return result
            except ImportError:
                return graph_source
        raise ValueError(f"Unsupported format: {output_format}")

    @classmethod
    def inspect_chunk(
        cls,
        file_path: str,
        chunk_id: str,
        include_context: bool = True,
    ) -> dict[str, Any]:
        """
        Inspect details of a specific chunk

        Args:
            file_path: Path to source file
            chunk_id: ID of chunk to inspect
            include_context: Include surrounding context

        Returns:
            Detailed chunk information
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".rs": "rust",
            ".go": "go",
            ".rb": "ruby",
            ".java": "java",
        }
        language = language_map.get(ext, "python")
        chunks = chunk_file(file_path, language)
        target_chunk = None
        for chunk in chunks:
            if chunk.chunk_id == chunk_id:
                target_chunk = chunk
                break
        if not target_chunk:
            raise ValueError(f"Chunk not found: {chunk_id}")
        result = {
            "id": target_chunk.chunk_id,
            "type": target_chunk.node_type,
            "start_line": target_chunk.start_line,
            "end_line": target_chunk.end_line,
            "content": target_chunk.content,
            "metadata": target_chunk.metadata or {},
            "relationships": {
                "parent": target_chunk.parent_chunk_id,
                "children": [],
                "siblings": [],
            },
            "context": {},
        }
        for chunk in chunks:
            if chunk.parent_chunk_id == target_chunk.chunk_id:
                result["relationships"]["children"].append(chunk.chunk_id)
            elif (
                chunk.parent_chunk_id == target_chunk.parent_chunk_id
                and chunk.chunk_id != target_chunk.chunk_id
            ):
                result["relationships"]["siblings"].append(chunk.chunk_id)
        if include_context:
            with Path(file_path).open("r", encoding="utf-8") as f:
                lines = f.readlines()
            start_context = max(0, target_chunk.start_line - 6)
            before_lines = lines[start_context : target_chunk.start_line - 1]
            end_context = min(len(lines), target_chunk.end_line + 5)
            after_lines = lines[target_chunk.end_line : end_context]
            result["context"] = {
                "before": "".join(before_lines),
                "after": "".join(after_lines),
                "parent_context": target_chunk.parent_context or "",
                "file_path": file_path,
                "language": target_chunk.language,
            }
        return result

    @classmethod
    def profile_chunking(cls, file_path: str, language: str) -> dict[str, Any]:
        """
        Profile the chunking process for performance analysis

        Args:
            file_path: Path to source file
            language: Programming language

        Returns:
            Performance metrics
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        tracemalloc.start()
        start_time = time.perf_counter()
        phase_times = {}
        phase_start = time.perf_counter()
        parser = get_parser(language)
        with Path(file_path).open("rb") as f:
            content = f.read()
        parser.parse(content)  # Parse to validate syntax
        phase_times["parsing"] = time.perf_counter() - phase_start
        phase_start = time.perf_counter()
        chunks = chunk_file(file_path, language)
        phase_times["chunking"] = time.perf_counter() - phase_start
        phase_start = time.perf_counter()
        metadata_count = sum(1 for c in chunks if c.metadata)
        phase_times["metadata"] = time.perf_counter() - phase_start
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        total_time = time.perf_counter() - start_time
        chunk_sizes = [(c.end_line - c.start_line + 1) for c in chunks]
        avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
        return {
            "total_time": total_time,
            "memory_peak": peak,
            "memory_current": current,
            "chunk_count": len(chunks),
            "phases": phase_times,
            "statistics": {
                "file_size": len(content),
                "total_lines": content.count(b"\n") + 1,
                "chunks_with_metadata": metadata_count,
                "average_chunk_size": avg_size,
                "max_chunk_size": max(chunk_sizes) if chunk_sizes else 0,
                "min_chunk_size": min(chunk_sizes) if chunk_sizes else 0,
            },
        }

    @classmethod
    def debug_mode_chunking(
        cls,
        file_path: str,
        language: str,
        breakpoints: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Run chunking in debug mode with detailed trace information

        Args:
            file_path: Path to source file
            language: Programming language
            breakpoints: List of node types to break on

        Returns:
            Step-by-step trace of chunking process
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        breakpoints = breakpoints or []
        trace = {
            "steps": [],
            "decision_points": [],
            "rule_applications": [],
            "node_visits": 0,
            "chunks_created": 0,
        }
        parser = get_parser(language)
        with Path(file_path).open("rb") as f:
            content = f.read()
        tree = parser.parse(content)  # Parse to validate syntax
        config = language_config_registry.get(language)

        def debug_walk(node, depth=0, parent_ctx=None):
            trace["node_visits"] += 1
            step = {
                "node_type": node.type,
                "depth": depth,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "actions": [],
            }
            if node.type in breakpoints:
                step["breakpoint"] = True
            should_chunk = False
            should_ignore = False
            if config:
                should_chunk = config.should_chunk_node(node.type)
                should_ignore = config.should_ignore_node(node.type)
                if should_ignore:
                    step["actions"].append("ignored")
                    trace["rule_applications"].append(
                        {
                            "rule": "ignore",
                            "node_type": node.type,
                            "line": node.start_point[0] + 1,
                        },
                    )
                elif should_chunk:
                    step["actions"].append("chunk_created")
                    trace["chunks_created"] += 1
                    trace["decision_points"].append(
                        {
                            "node_type": node.type,
                            "decision": "create_chunk",
                            "line": node.start_point[0] + 1,
                            "reason": f"Matches chunk rule for {language}",
                        },
                    )
            elif node.type in {
                "function_definition",
                "class_definition",
                "method_definition",
            }:
                step["actions"].append("chunk_created")
                trace["chunks_created"] += 1
            trace["steps"].append(step)
            if node.child_count > 0:
                for i in range(node.child_count):
                    child = node.children[i]
                    new_parent_ctx = node.type if should_chunk else parent_ctx
                    debug_walk(child, depth + 1, new_parent_ctx)

        debug_walk(tree.root_node)
        return trace
