"""Export chunks and relationships to Apache Parquet fmt."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pyarrow as pa
import pyarrow.parquet as pq

from chunker.exceptions import ChunkerError
from chunker.interfaces.export import (
    ChunkRelationship,
    ExportFormat,
    ExportMetadata,
    StructuredExporter,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from chunker.types import CodeChunk


class StructuredParquetExporter(StructuredExporter):
    """Export chunks and relationships to Parquet fmt with full structure."""

    def __init__(
        self,
        compression: str = "snappy",
        partition_by: list[str] | None = None,
    ):
        """Initialize the Parquet exporter.

        Args:
            compression: Compression codec ('snappy', 'gzip', 'brotli', 'lz4', 'zstd', None)
            partition_by: List of columns to partition by (e.g., ['language', 'file_path'])
        """
        self.compression = compression
        self.partition_by = partition_by
        self._batch_size = 10000
        self._chunks_schema = self._create_chunks_schema()
        self._relationships_schema = self._create_relationships_schema()

    def export(
        self,
        chunks: list[CodeChunk],
        relationships: list[ChunkRelationship],
        output: Path | io.IOBase,
        metadata: ExportMetadata | None = None,
    ) -> None:
        """Export chunks with relationships to Parquet.

        Creates two Parquet files:
        - <output>_chunks.parquet: Contains chunk data
        - <output>_relationships.parquet: Contains relationship data

        Args:
            chunks: List of code chunks
            relationships: List of chunk relationships
            output: Output path (base name for files)
            metadata: Export metadata
        """
        if isinstance(output, io.IOBase):
            raise ChunkerError("Parquet export requires a file path, not a stream")
        base_path = Path(output).with_suffix("")
        chunks_path = f"{base_path}_chunks.parquet"
        self._export_chunks(chunks, chunks_path)
        relationships_path = f"{base_path}_relationships.parquet"
        self._export_relationships(relationships, relationships_path)
        if metadata:
            metadata_path = f"{base_path}_metadata.parquet"
            self._export_metadata(metadata, metadata_path)

    def export_streaming(
        self,
        chunk_iterator: Iterator[CodeChunk],
        relationship_iterator: Iterator[ChunkRelationship],
        output: Path | io.IOBase,
    ) -> None:
        """Export using iterators for large datasets."""
        if isinstance(output, io.IOBase):
            raise ChunkerError("Parquet export requires a file path, not a stream")
        base_path = Path(output).with_suffix("")
        chunks_path = f"{base_path}_chunks.parquet"
        self._stream_chunks(chunk_iterator, chunks_path)
        relationships_path = f"{base_path}_relationships.parquet"
        self._stream_relationships(relationship_iterator, relationships_path)

    @staticmethod
    def supports_format(fmt: ExportFormat) -> bool:
        """Check if this exporter supports a fmt."""
        return fmt == ExportFormat.PARQUET

    def get_schema(self) -> dict[str, Any]:
        """Get the export schema."""
        return {
            "fmt": "parquet",
            "version": "2.6",
            "compression": self.compression,
            "partition_by": self.partition_by,
            "batch_size": self._batch_size,
            "schemas": {
                "chunks": self._chunks_schema.to_string(),
                "relationships": self._relationships_schema.to_string(),
            },
        }

    def set_batch_size(self, size: int) -> None:
        """Set batch size for streaming operations."""
        self._batch_size = size

    @staticmethod
    def _create_chunks_schema() -> pa.Schema:
        """Create PyArrow schema for chunks."""
        return pa.schema(
            [
                pa.field("chunk_id", pa.string(), nullable=False),
                pa.field("language", pa.string(), nullable=False),
                pa.field("file_path", pa.string(), nullable=False),
                pa.field("node_type", pa.string(), nullable=False),
                pa.field("start_line", pa.int64(), nullable=False),
                pa.field("end_line", pa.int64(), nullable=False),
                pa.field("byte_start", pa.int64(), nullable=False),
                pa.field("byte_end", pa.int64(), nullable=False),
                pa.field("parent_context", pa.string()),
                pa.field("content", pa.string(), nullable=False),
                pa.field("parent_chunk_id", pa.string()),
                pa.field("references", pa.list_(pa.string())),
                pa.field("dependencies", pa.list_(pa.string())),
                pa.field("lines_of_code", pa.int64()),
                pa.field("byte_size", pa.int64()),
            ],
        )

    @staticmethod
    def _create_relationships_schema() -> pa.Schema:
        """Create PyArrow schema for relationships."""
        return pa.schema(
            [
                pa.field("source_chunk_id", pa.string(), nullable=False),
                pa.field("target_chunk_id", pa.string(), nullable=False),
                pa.field("relationship_type", pa.string(), nullable=False),
                pa.field("metadata", pa.string()),
            ],
        )

    @staticmethod
    def _create_metadata_schema() -> pa.Schema:
        """Create PyArrow schema for metadata."""
        return pa.schema(
            [
                pa.field("fmt", pa.string()),
                pa.field("version", pa.string()),
                pa.field("created_at", pa.string()),
                pa.field("source_files", pa.list_(pa.string())),
                pa.field("chunk_count", pa.int64()),
                pa.field("relationship_count", pa.int64()),
                pa.field("options", pa.string()),
            ],
        )

    @staticmethod
    def _chunk_to_dict(chunk: CodeChunk) -> dict[str, Any]:
        """Convert a CodeChunk to a dictionary."""
        return {
            "chunk_id": chunk.chunk_id,
            "language": chunk.language,
            "file_path": chunk.file_path,
            "node_type": chunk.node_type,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "byte_start": chunk.byte_start,
            "byte_end": chunk.byte_end,
            "parent_context": chunk.parent_context or "",
            "content": chunk.content,
            "parent_chunk_id": chunk.parent_chunk_id or "",
            "references": chunk.references,
            "dependencies": chunk.dependencies,
            "lines_of_code": chunk.end_line - chunk.start_line + 1,
            "byte_size": chunk.byte_end - chunk.byte_start,
        }

    @staticmethod
    def _relationship_to_dict(rel: ChunkRelationship) -> dict[str, Any]:
        """Convert a ChunkRelationship to a dictionary."""
        return {
            "source_chunk_id": rel.source_chunk_id,
            "target_chunk_id": rel.target_chunk_id,
            "relationship_type": rel.relationship_type.value,
            "metadata": json.dumps(rel.metadata) if rel.metadata else "",
        }

    def _export_chunks(self, chunks: list[CodeChunk], output_path: str | Path) -> None:
        """Export chunks to Parquet file."""
        records = [self._chunk_to_dict(chunk) for chunk in chunks]
        table = pa.Table.from_pylist(records, schema=self._chunks_schema)
        path_str = str(output_path)
        if self.partition_by:
            valid_partitions = [
                col for col in self.partition_by if col in self._chunks_schema.names
            ]
            if valid_partitions:
                # When writing a partitioned dataset, manually create partitions
                root_path = Path(path_str)
                if root_path.suffix:
                    root_path = root_path.parent
                root_path.mkdir(parents=True, exist_ok=True)

                # Group records by partition columns
                partitions = {}
                for i in range(len(table)):
                    partition_key = tuple(
                        table.column(col)[i].as_py() for col in valid_partitions
                    )
                    if partition_key not in partitions:
                        partitions[partition_key] = []
                    partitions[partition_key].append(i)

                # Write each partition to its own file
                for partition_values, row_indices in partitions.items():
                    partition_dir = root_path
                    for i, col in enumerate(valid_partitions):
                        partition_dir = partition_dir / f"{col}={partition_values[i]}"

                    partition_dir.mkdir(parents=True, exist_ok=True)
                    subset_table = table.take(row_indices)
                    partition_file = partition_dir / "data.parquet"
                    with pa.OSFile(str(partition_file), "wb") as sink:
                        pq.write_table(subset_table, sink, compression=self.compression)
            else:
                with pa.OSFile(path_str, "wb") as sink:
                    pq.write_table(table, sink, compression=self.compression)
        else:
            with pa.OSFile(path_str, "wb") as sink:
                pq.write_table(table, sink, compression=self.compression)

    def _export_relationships(
        self,
        relationships: list[ChunkRelationship],
        output_path: str | Path,
    ) -> None:
        """Export relationships to Parquet file."""
        records = [self._relationship_to_dict(rel) for rel in relationships]
        table = pa.Table.from_pylist(records, schema=self._relationships_schema)
        with pa.OSFile(str(output_path), "wb") as sink:
            pq.write_table(table, sink, compression=self.compression)

    def _export_metadata(
        self,
        metadata: ExportMetadata,
        output_path: str | Path,
    ) -> None:
        """Export metadata to Parquet file."""
        record = {
            "fmt": metadata.fmt.value,
            "version": metadata.version,
            "created_at": metadata.created_at,
            "source_files": metadata.source_files,
            "chunk_count": metadata.chunk_count,
            "relationship_count": metadata.relationship_count,
            "options": json.dumps(metadata.options),
        }
        table = pa.Table.from_pylist([record], schema=self._create_metadata_schema())
        with pa.OSFile(str(output_path), "wb") as sink:
            pq.write_table(table, sink, compression=self.compression)

    def _stream_chunks(
        self,
        chunk_iterator: Iterator[CodeChunk],
        output_path: str | Path,
    ) -> None:
        """Stream chunks to Parquet file."""
        writer = None
        batch = []
        try:
            for chunk in chunk_iterator:
                batch.append(self._chunk_to_dict(chunk))
                if len(batch) >= self._batch_size:
                    table = pa.Table.from_pylist(batch, schema=self._chunks_schema)
                    if writer is None:
                        sink = pa.OSFile(str(output_path), "wb")
                        writer = pq.ParquetWriter(
                            sink,
                            schema=self._chunks_schema,
                            compression=self.compression,
                        )
                    writer.write_table(table)
                    batch = []
            if batch:
                table = pa.Table.from_pylist(batch, schema=self._chunks_schema)
                if writer is None:
                    sink = pa.OSFile(str(output_path), "wb")
                    writer = pq.ParquetWriter(
                        sink,
                        schema=self._chunks_schema,
                        compression=self.compression,
                    )
                writer.write_table(table)
        finally:
            if writer:
                writer.close()

    def _stream_relationships(
        self,
        relationship_iterator: Iterator[ChunkRelationship],
        output_path: str | Path,
    ) -> None:
        """Stream relationships to Parquet file."""
        writer = None
        batch = []
        try:
            for rel in relationship_iterator:
                batch.append(self._relationship_to_dict(rel))
                if len(batch) >= self._batch_size:
                    table = pa.Table.from_pylist(
                        batch,
                        schema=self._relationships_schema,
                    )
                    if writer is None:
                        sink = pa.OSFile(str(output_path), "wb")
                        writer = pq.ParquetWriter(
                            sink,
                            schema=self._relationships_schema,
                            compression=self.compression,
                        )
                    writer.write_table(table)
                    batch = []
            if batch:
                table = pa.Table.from_pylist(batch, schema=self._relationships_schema)
                if writer is None:
                    sink = pa.OSFile(str(output_path), "wb")
                    writer = pq.ParquetWriter(
                        sink,
                        schema=self._relationships_schema,
                        compression=self.compression,
                    )
                writer.write_table(table)
        finally:
            if writer:
                writer.close()
