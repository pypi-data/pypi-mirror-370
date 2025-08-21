"""Tests for fallback chunking functionality."""

import tempfile
import warnings
from pathlib import Path

from chunker.fallback import (
    FallbackWarning,
    FileTypeDetector,
    LineBasedChunker,
    LogChunker,
    MarkdownChunker,
)
from chunker.fallback.detection.file_type import EncodingDetector, FileType
from chunker.fallback.fallback_manager import FallbackManager
from chunker.interfaces.fallback import FallbackReason


class TestFallbackBase:
    """Test base fallback functionality."""

    @classmethod
    def test_fallback_warning_emitted(cls):
        """Test that fallback usage emits warnings."""
        chunker = LineBasedChunker()
        chunker.set_fallback_reason(FallbackReason.NO_GRAMMAR)
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            chunker.chunk_text(content, "test.txt")
            assert len(w) == 1
            assert issubclass(w[0].category, FallbackWarning)
            assert "WARNING: Using fallback chunking" in str(w[0].message)

    @classmethod
    def test_line_based_chunking(cls):
        """Test basic line-based chunking."""
        chunker = LineBasedChunker(lines_per_chunk=2, overlap=0)
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        chunks = chunker.chunk_by_lines(content, 2, 0)
        assert len(chunks) == 3
        assert chunks[0].content == "Line 1\nLine 2\n"
        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 2
        assert chunks[1].content == "Line 3\nLine 4\n"
        assert chunks[1].start_line == 3
        assert chunks[1].end_line == 4
        assert chunks[2].content == "Line 5"
        assert chunks[2].start_line == 5
        assert chunks[2].end_line == 5

    @classmethod
    def test_line_based_with_overlap(cls):
        """Test line-based chunking with overlap."""
        chunker = LineBasedChunker(lines_per_chunk=3, overlap=1)
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        chunks = chunker.chunk_by_lines(content, 3, 1)
        assert len(chunks) == 2
        assert "Line 1" in chunks[0].content
        assert "Line 3" in chunks[0].content
        assert "Line 3" in chunks[1].content
        assert "Line 5" in chunks[1].content

    @classmethod
    def test_delimiter_based_chunking(cls):
        """Test delimiter-based chunking."""
        chunker = LineBasedChunker()
        content = "Section 1\n---\nSection 2\n---\nSection 3"
        chunks = chunker.chunk_by_delimiter(content, "---", include_delimiter=False)
        assert len(chunks) == 3
        assert chunks[0].content.strip() == "Section 1"
        assert chunks[1].content.strip() == "Section 2"
        assert chunks[2].content.strip() == "Section 3"


class TestFileTypeDetection:
    """Test file type detection."""

    @classmethod
    def test_extension_detection(cls):
        """Test detection by file extension."""
        detector = FileTypeDetector()
        assert detector.detect_file_type("test.log") == FileType.LOG
        assert detector.detect_file_type("README.md") == FileType.MARKDOWN
        assert detector.detect_file_type("data.csv") == FileType.CSV
        assert detector.detect_file_type("config.yaml") == FileType.YAML
        assert detector.detect_file_type("notes.txt") == FileType.TEXT

    @classmethod
    def test_content_detection(cls):
        """Test detection by content patterns."""
        detector = FileTypeDetector()
        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".unknown",
            delete=False,
        ) as f:
            f.write("2024-01-15 10:30:45 ERROR Something went wrong\n")
            f.write("2024-01-15 10:30:46 INFO Process started\n")
            f.flush()
            file_type = detector.detect_file_type(f.name)
            assert file_type == FileType.LOG
            Path(f.name).unlink()

    @classmethod
    def test_encoding_detection(cls):
        """Test encoding detection."""
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
            f.write("Hello, world! 你好世界")
            f.flush()
            encoding, _confidence = EncodingDetector.detect_encoding(f.name)
            assert encoding.lower() in {"utf-8", "utf8"}
            content, _used_encoding = EncodingDetector.read_with_encoding(f.name)
            assert "Hello, world!" in content
            assert "你好世界" in content
            Path(f.name).unlink()


class TestLogChunker:
    """Test log file chunking."""

    @classmethod
    def test_timestamp_detection(cls):
        """Test timestamp pattern detection."""
        chunker = LogChunker()
        log_content = """2024-01-15T10:30:45.123Z INFO Starting application
2024-01-15T10:30:46.456Z DEBUG Configuration loaded
2024-01-15T10:31:00.789Z ERROR Connection failed"""
        format_info = chunker.detect_log_format(log_content)
        assert format_info["has_timestamps"] is True
        assert format_info["has_levels"] is True

    @classmethod
    def test_chunk_by_timestamp(cls):
        """Test chunking logs by time window."""
        chunker = LogChunker()
        chunker.file_path = "test.log"
        log_content = """2024-01-15 10:30:00 INFO Start
2024-01-15 10:30:30 DEBUG Processing
2024-01-15 10:31:00 INFO Checkpoint
2024-01-15 10:31:30 DEBUG More processing
2024-01-15 10:32:00 INFO Complete"""
        chunks = chunker.chunk_by_timestamp(log_content, 60)
        assert len(chunks) >= 2
        assert "10:30:00" in chunks[0].content
        assert "10:30:30" in chunks[0].content

    @classmethod
    def test_chunk_by_severity(cls):
        """Test chunking logs by severity level."""
        chunker = LogChunker()
        chunker.file_path = "test.log"
        log_content = """INFO Starting process
INFO Configuration loaded
ERROR Failed to connect
ERROR Retry failed
WARN Using fallback
INFO Process complete"""
        chunks = chunker.chunk_by_severity(log_content, group_consecutive=True)
        assert len(chunks) == 4
        assert "Starting process" in chunks[0].content
        assert "Configuration loaded" in chunks[0].content
        assert "Failed to connect" in chunks[1].content
        assert "Retry failed" in chunks[1].content


class TestMarkdownChunker:
    """Test markdown file chunking."""

    @classmethod
    def test_chunk_by_headers(cls):
        """Test chunking markdown by headers."""
        chunker = MarkdownChunker()
        chunker.file_path = "test.md"
        md_content = """# Title

Introduction paragraph.

## Section 1

Content for section 1.

### Subsection 1.1

Detailed content.

## Section 2

Content for section 2."""
        chunks = chunker.chunk_by_headers(md_content, max_level=2)
        assert len(chunks) >= 3
        section1_chunk = next(c for c in chunks if "Section 1" in c.content)
        assert "Subsection 1.1" in section1_chunk.content

    @classmethod
    def test_chunk_by_sections(cls):
        """Test chunking markdown by logical sections."""
        chunker = MarkdownChunker()
        chunker.file_path = "test.md"
        md_content = """# Title

Introduction paragraph.

```python
def hello():
    print("Hello")
```

Some more text.

- Item 1
- Item 2
- Item 3

Final paragraph."""
        chunks = chunker.chunk_by_sections(
            md_content,
            include_code_blocks=True,
        )
        assert len(chunks) >= 4
        code_chunk = next((c for c in chunks if "code_block" in c.node_type), None)
        assert code_chunk is not None
        assert "def hello():" in code_chunk.content

    @classmethod
    def test_extract_code_blocks(cls):
        """Test extracting code blocks from markdown."""
        chunker = MarkdownChunker()
        chunker.file_path = "test.md"
        md_content = """# Example

Here's some Python code:

```python
def greet(name):
    return f"Hello, {name}!"
```

And some JavaScript:

```javascript
function greet(name) {
    return `Hello, ${name}!`;
}
```
"""
        chunks = chunker.extract_code_blocks(md_content)
        assert len(chunks) == 2
        python_chunk = next(c for c in chunks if c.language == "python")
        assert "def greet" in python_chunk.content
        js_chunk = next(c for c in chunks if c.language == "javascript")
        assert "function greet" in js_chunk.content


class TestFallbackManager:
    """Test fallback manager coordination."""

    @classmethod
    def test_manager_file_detection(cls):
        """Test manager's file type detection and chunking."""
        manager = FallbackManager()
        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".log",
            delete=False,
        ) as f:
            f.write("2024-01-15 10:30:00 INFO Test log entry\n")
            f.write("2024-01-15 10:30:01 ERROR Something failed\n")
            f.flush()
            assert manager.can_chunk(f.name) is True
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                chunks = manager.chunk_file(f.name)
                assert len(chunks) > 0
                assert any("Test log entry" in chunk.content for chunk in chunks)
                assert any(
                    issubclass(warning.category, FallbackWarning) for warning in w
                )
            Path(f.name).unlink()

    @classmethod
    def test_manager_fallback_info(cls):
        """Test getting fallback information."""
        manager = FallbackManager()
        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".csv",
            delete=False,
        ) as f:
            f.write("name,age,city\n")
            f.write("Alice,30,NYC\n")
            f.flush()
            info = manager.get_fallback_info(f.name)
            assert info["file_type"] == "csv"
            assert info["can_chunk"] is True
            assert info["should_use_fallback"] is True
            assert info["fallback_reason"] == FallbackReason.NO_GRAMMAR.value
            Path(f.name).unlink()

    @classmethod
    def test_csv_chunking(cls):
        """Test CSV-specific chunking."""
        manager = FallbackManager()
        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".csv",
            delete=False,
        ) as f:
            f.write("id,name,score\n")
            for i in range(60):
                f.write(f"{i},User{i},{i * 10}\n")
            f.flush()
            chunks = manager.chunk_file(f.name)
            assert len(chunks) > 0
            assert (
                len(
                    chunks,
                )
                > 1
            ), "Need multiple chunks to test header inclusion"
            assert chunks[0].start_line == 2
            assert "id,name,score" not in chunks[0].content
            for i, chunk in enumerate(chunks[1:], 1):
                assert "id,name,score" in chunk.content, f"Chunk {i} missing header"
            Path(f.name).unlink()
