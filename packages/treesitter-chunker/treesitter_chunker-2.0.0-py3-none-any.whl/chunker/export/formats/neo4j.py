"""Export chunks to Neo4j graph database fmt."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from chunker.interfaces.export import (
    ChunkRelationship,
    ExportFormat,
    ExportMetadata,
    StructuredExporter,
)

if TYPE_CHECKING:
    import io
    from collections.abc import Iterator

    from chunker.types import CodeChunk


class Neo4jExporter(StructuredExporter):
    """Export chunks and relationships to Neo4j Cypher fmt.

    Generates Cypher queries that can be executed against a Neo4j database.
    """

    def __init__(self):
        self._batch_size = 1000
        self._node_label = "CodeChunk"
        self._use_merge = True
        self._include_content = True

    def export(
        self,
        chunks: list[CodeChunk],
        relationships: list[ChunkRelationship],
        output: Path | io.IOBase,
        metadata: ExportMetadata | None = None,
    ) -> None:
        """Export chunks with relationships as Neo4j Cypher queries.

        Args:
            chunks: List of code chunks
            relationships: List of chunk relationships
            output: Output path or stream
            metadata: Export metadata
        """
        cypher_lines = []
        cypher_lines.extend(
            [
                "// TreeSitter Chunker Neo4j Export",
                f"// Generated: {datetime.now(UTC).isoformat()}",
                f"// Chunks: {len(chunks)}, Relationships: {len(relationships)}",
                "",
                "// Create constraints for better performance",
                f"CREATE CONSTRAINT IF NOT EXISTS FOR (c:{self._node_label}) REQUIRE c.chunk_id IS UNIQUE;",
                f"CREATE INDEX IF NOT EXISTS FOR (c:{self._node_label}) ON (c.file_path);",
                f"CREATE INDEX IF NOT EXISTS FOR (c:{self._node_label}) ON (c.node_type);",
                f"CREATE INDEX IF NOT EXISTS FOR (c:{self._node_label}) ON (c.language);",
                "",
            ],
        )
        if metadata:
            cypher_lines.extend(self._generate_metadata_node(metadata))
            cypher_lines.append("")
        cypher_lines.append("// Create code chunk nodes")
        cypher_lines.extend(self._generate_node_queries(chunks))
        cypher_lines.append("")
        cypher_lines.append("// Create relationships")
        cypher_lines.extend(self._generate_relationship_queries(relationships))
        cypher_content = "\n".join(cypher_lines)
        if isinstance(output, str | Path):
            Path(output).write_text(cypher_content, encoding="utf-8")
        else:
            output.write(cypher_content)

    def export_streaming(
        self,
        chunk_iterator: Iterator[CodeChunk],
        relationship_iterator: Iterator[ChunkRelationship],
        output: Path | io.IOBase,
    ) -> None:
        """Export using iterators for large datasets."""
        if isinstance(output, str | Path):
            with Path(output).open("w", encoding="utf-8") as f:
                self._stream_cypher(chunk_iterator, relationship_iterator, f)
        else:
            self._stream_cypher(chunk_iterator, relationship_iterator, output)

    @staticmethod
    def supports_format(fmt: ExportFormat) -> bool:
        """Check if this exporter supports a fmt."""
        return fmt == ExportFormat.NEO4J

    def get_schema(self) -> dict[str, Any]:
        """Get the export schema."""
        return {
            "fmt": "neo4j",
            "version": "4.4+",
            "node_label": self._node_label,
            "batch_size": self._batch_size,
            "use_merge": self._use_merge,
            "include_content": self._include_content,
        }

    def set_node_label(self, label: str) -> None:
        """Set the label for chunk nodes."""
        self._node_label = label

    def set_use_merge(self, use_merge: bool) -> None:
        """Set whether to use MERGE instead of CREATE."""
        self._use_merge = use_merge

    def set_include_content(self, include: bool) -> None:
        """Set whether to include full content in nodes."""
        self._include_content = include

    def set_batch_size(self, size: int) -> None:
        """Set batch size for queries."""
        self._batch_size = size

    @staticmethod
    def _generate_metadata_node(metadata: ExportMetadata) -> list[str]:
        """Generate Cypher for metadata node."""
        return [
            "// Create metadata node",
            "CREATE (m:ExportMetadata {",
            f"  fmt: '{metadata.fmt.value}',",
            f"  version: '{metadata.version}',",
            f"  created_at: datetime('{metadata.created_at}'),",
            f"  source_files: {json.dumps(metadata.source_files)},",
            f"  chunk_count: {metadata.chunk_count},",
            f"  relationship_count: {metadata.relationship_count},",
            f"  options: {json.dumps(metadata.options)}",
            "});",
        ]

    def _generate_node_queries(self, chunks: list[CodeChunk]) -> list[str]:
        """Generate Cypher queries for creating nodes."""
        queries = []
        for i in range(0, len(chunks), self._batch_size):
            batch = chunks[i : i + self._batch_size]
            batch_data = []
            for chunk in batch:
                node_data = {
                    "chunk_id": chunk.chunk_id,
                    "language": chunk.language,
                    "file_path": chunk.file_path,
                    "node_type": chunk.node_type,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "byte_start": chunk.byte_start,
                    "byte_end": chunk.byte_end,
                    "parent_context": chunk.parent_context or "",
                    "parent_chunk_id": chunk.parent_chunk_id or "",
                    "references": chunk.references,
                    "dependencies": chunk.dependencies,
                }
                if self._include_content:
                    node_data["content"] = chunk.content.replace(
                        "\\",
                        "\\\\",
                    ).replace('"', '\\"')
                batch_data.append(node_data)
            operation = "MERGE" if self._use_merge else "CREATE"
            query_lines = [
                f"UNWIND {json.dumps(batch_data)} AS chunk",
                f"{operation} (c:{self._node_label} {{chunk_id: chunk.chunk_id}})",
                "SET c.language = chunk.language,",
                "    c.file_path = chunk.file_path,",
                "    c.node_type = chunk.node_type,",
                "    c.start_line = chunk.start_line,",
                "    c.end_line = chunk.end_line,",
                "    c.byte_start = chunk.byte_start,",
                "    c.byte_end = chunk.byte_end,",
                "    c.parent_context = chunk.parent_context,",
                "    c.parent_chunk_id = chunk.parent_chunk_id,",
                "    c.references = chunk.references,",
                "    c.dependencies = chunk.dependencies",
            ]
            if self._include_content:
                query_lines.append("    c.content = chunk.content")
            else:
                query_lines[-1] += ","
                query_lines.append("    c.has_content = true")
            query_lines.append(";")
            queries.extend(query_lines)
            queries.append("")
        return queries

    def _generate_relationship_queries(
        self,
        relationships: list[ChunkRelationship],
    ) -> list[str]:
        """Generate Cypher queries for creating relationships."""
        queries = []
        relationships_by_type = {}
        for rel in relationships:
            rel_type = rel.relationship_type.value
            if rel_type not in relationships_by_type:
                relationships_by_type[rel_type] = []
            relationships_by_type[rel_type].append(rel)
        for rel_type, typed_relationships in relationships_by_type.items():
            queries.append(f"// {rel_type} relationships")
            neo4j_rel_type = self._to_neo4j_relationship_type(rel_type)
            for i in range(0, len(typed_relationships), self._batch_size):
                batch = typed_relationships[i : i + self._batch_size]
                batch_data = []
                for rel in batch:
                    rel_data = {
                        "source_id": rel.source_chunk_id,
                        "target_id": rel.target_chunk_id,
                    }
                    if rel.metadata:
                        rel_data["metadata"] = rel.metadata
                    batch_data.append(rel_data)
                query_lines = [
                    f"UNWIND {json.dumps(batch_data)} AS rel",
                    f"MATCH (source:{self._node_label} {{chunk_id: rel.source_id}})",
                    f"MATCH (target:{self._node_label} {{chunk_id: rel.target_id}})",
                    f"MERGE (source)-[r:{neo4j_rel_type}]->(target)",
                ]
                if any(r.get("metadata") for r in batch_data):
                    query_lines.append(
                        "SET r.metadata = CASE WHEN rel.metadata IS NOT NULL THEN rel.metadata ELSE null END",
                    )
                query_lines.append(";")
                queries.extend(query_lines)
                queries.append("")
        return queries

    @staticmethod
    def _to_neo4j_relationship_type(rel_type: str) -> str:
        """Convert relationship type to Neo4j-friendly fmt."""
        return rel_type.upper()

    def _stream_cypher(
        self,
        chunk_iterator: Iterator[CodeChunk],
        relationship_iterator: Iterator[ChunkRelationship],
        output: io.IOBase,
    ) -> None:
        """Stream Cypher queries to output."""
        output.write("// TreeSitter Chunker Neo4j Export\n")
        output.write(f"// Generated: {datetime.now(UTC).isoformat()}\n")
        output.write("\n")
        output.write("// Create constraints for better performance\n")
        output.write(
            f"""CREATE CONSTRAINT IF NOT EXISTS FOR (c:{self._node_label}) REQUIRE c.chunk_id IS UNIQUE;
""",
        )
        output.write(
            f"CREATE INDEX IF NOT EXISTS FOR (c:{self._node_label}) ON (c.file_path);\n",
        )
        output.write(
            f"CREATE INDEX IF NOT EXISTS FOR (c:{self._node_label}) ON (c.node_type);\n",
        )
        output.write(
            f"CREATE INDEX IF NOT EXISTS FOR (c:{self._node_label}) ON (c.language);\n",
        )
        output.write("\n")
        output.write("// Create code chunk nodes\n")
        chunk_batch = []
        for chunk in chunk_iterator:
            chunk_batch.append(chunk)
            if len(chunk_batch) >= self._batch_size:
                for line in self._generate_node_queries(chunk_batch):
                    output.write(line + "\n")
                chunk_batch = []
                output.flush()
        if chunk_batch:
            for line in self._generate_node_queries(chunk_batch):
                output.write(line + "\n")
        output.write("\n")
        output.write("// Create relationships\n")
        relationships_by_type = {}
        for rel in relationship_iterator:
            rel_type = rel.relationship_type.value
            if rel_type not in relationships_by_type:
                relationships_by_type[rel_type] = []
            relationships_by_type[rel_type].append(rel)
            if len(relationships_by_type[rel_type]) >= self._batch_size:
                self._write_relationship_batch(
                    output,
                    rel_type,
                    relationships_by_type[rel_type],
                )
                relationships_by_type[rel_type] = []
        for rel_type, rels in relationships_by_type.items():
            if rels:
                self._write_relationship_batch(output, rel_type, rels)

    def _write_relationship_batch(
        self,
        output: io.IOBase,
        rel_type: str,
        relationships: list[ChunkRelationship],
    ) -> None:
        """Write a batch of relationships to output."""
        output.write(f"// {rel_type} relationships\n")
        neo4j_rel_type = self._to_neo4j_relationship_type(rel_type)
        batch_data = []
        for rel in relationships:
            rel_data = {
                "source_id": rel.source_chunk_id,
                "target_id": rel.target_chunk_id,
            }
            if rel.metadata:
                rel_data["metadata"] = rel.metadata
            batch_data.append(rel_data)
        output.write(f"UNWIND {json.dumps(batch_data)} AS rel\n")
        output.write(f"MATCH (source:{self._node_label} {{chunk_id: rel.source_id}})\n")
        output.write(f"MATCH (target:{self._node_label} {{chunk_id: rel.target_id}})\n")
        output.write(f"MERGE (source)-[r:{neo4j_rel_type}]->(target)\n")
        if any(r.get("metadata") for r in batch_data):
            output.write(
                """SET r.metadata = CASE WHEN rel.metadata IS NOT NULL THEN rel.metadata ELSE null END
""",
            )
        output.write(";\n\n")
        output.flush()
