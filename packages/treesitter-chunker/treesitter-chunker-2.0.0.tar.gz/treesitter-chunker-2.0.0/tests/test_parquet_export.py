"""Tests for Parquet export functionality."""

import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from chunker.exporters import ParquetExporter
from chunker.types import CodeChunk


def read_parquet_table(path):
    """Read parquet table with compatibility for older pyarrow versions."""
    # For pyarrow < 16, use OSFile to avoid path conversion issues
    if int(pa.__version__.split(".")[0]) < 16:
        with pa.OSFile(str(path), "rb") as source:
            return pq.read_table(source)
    else:
        return pq.read_table(str(path))


@pytest.fixture
def sample_chunks():
    """Create sample code chunks for testing."""
    return [
        CodeChunk(
            language="python",
            file_path="test1.py",
            node_type="function_definition",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="",
            content="def test_func():\n    pass",
        ),
        CodeChunk(
            language="python",
            file_path="test1.py",
            node_type="class_definition",
            start_line=7,
            end_line=15,
            byte_start=102,
            byte_end=250,
            parent_context="",
            content="class TestClass:\n    def method(self):\n        pass",
        ),
        CodeChunk(
            language="rust",
            file_path="test2.rs",
            node_type="function_definition",
            start_line=1,
            end_line=3,
            byte_start=0,
            byte_end=50,
            parent_context="",
            content='fn main() {\n    println!("Hello");\n}',
        ),
    ]


def test_basic_export(sample_chunks):
    """Test basic Parquet export functionality."""
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        output_path = Path(tmp.name)

        exporter = ParquetExporter()
        exporter.export(sample_chunks, output_path)

        # Read back and verify
        table = read_parquet_table(output_path)
        assert len(table) == 3

        # Check schema
        assert "language" in table.schema.names
        assert "file_path" in table.schema.names
        assert "node_type" in table.schema.names
        assert "content" in table.schema.names
        assert "metadata" in table.schema.names
        assert "lines_of_code" in table.schema.names
        assert "byte_size" in table.schema.names

        # Check nested metadata
        metadata_col = table.column("metadata")
        assert metadata_col.type.num_fields == 4

        # Cleanup
        output_path.unlink()


def test_column_selection(sample_chunks):
    """Test exporting with selected columns only."""
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        output_path = Path(tmp.name)

        exporter = ParquetExporter(columns=["language", "node_type", "lines_of_code"])
        exporter.export(sample_chunks, output_path)

        # Read back and verify
        table = read_parquet_table(output_path)
        assert len(table) == 3

        # Check only selected columns are present
        assert set(table.schema.names) == {"language", "node_type", "lines_of_code"}

        # Cleanup
        output_path.unlink()


def test_partitioned_export(sample_chunks):
    """Test partitioned Parquet export."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "partitioned_chunks"

        exporter = ParquetExporter(partition_by=["language"])
        exporter.export(sample_chunks, output_path)

        # Check partitions were created
        assert (output_path / "language=python").exists()
        assert (output_path / "language=rust").exists()

        # Read back partitioned dataset - use compatibility approach
        if int(pa.__version__.split(".")[0]) < 16:
            # For older pyarrow, read partitions directly
            tables = []
            for lang_dir in output_path.glob("language=*"):
                for parquet_file in lang_dir.glob("*.parquet"):
                    with pa.OSFile(str(parquet_file), "rb") as source:
                        tables.append(pq.read_table(source))
            table = pa.concat_tables(tables) if tables else pa.table({})
        else:
            dataset = pq.ParquetDataset(str(output_path))
            table = dataset.read()
        assert len(table) == 3


def test_compression_options(sample_chunks):
    """Test different compression codecs."""
    compressions = ["snappy", "gzip", "zstd", None]

    for compression in compressions:
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
            output_path = Path(tmp.name)

            exporter = ParquetExporter(compression=compression)
            exporter.export(sample_chunks, output_path)

            # Verify file was created and can be read
            assert output_path.exists()
            table = read_parquet_table(output_path)
            assert len(table) == 3

            # Cleanup
            output_path.unlink()


def test_streaming_export(sample_chunks):
    """Test streaming export for large datasets."""
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        output_path = Path(tmp.name)

        exporter = ParquetExporter()

        # Use iterator to simulate streaming
        def chunks_iterator():
            yield from sample_chunks

        exporter.export_streaming(chunks_iterator(), output_path, batch_size=2)

        # Read back and verify
        table = read_parquet_table(output_path)
        assert len(table) == 3

        # Cleanup
        output_path.unlink()


def test_empty_chunks():
    """Test exporting empty chunks list."""
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        output_path = Path(tmp.name)

        exporter = ParquetExporter()
        exporter.export([], output_path)

        # Read back and verify
        table = read_parquet_table(output_path)
        assert len(table) == 0

        # Cleanup
        output_path.unlink()


def test_metadata_structure(sample_chunks):
    """Test nested metadata structure is correctly preserved."""
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        output_path = Path(tmp.name)

        exporter = ParquetExporter()
        exporter.export(sample_chunks, output_path)

        # Read back
        table = read_parquet_table(output_path)

        # Check metadata is a struct type
        metadata_col = table.column("metadata")
        assert metadata_col.type.num_fields == 4

        # Check first row's metadata values directly from PyArrow
        first_row_metadata = metadata_col[0].as_py()
        assert first_row_metadata["start_line"] == 1
        assert first_row_metadata["end_line"] == 5
        assert first_row_metadata["byte_start"] == 0
        assert first_row_metadata["byte_end"] == 100

        # Cleanup
        output_path.unlink()
