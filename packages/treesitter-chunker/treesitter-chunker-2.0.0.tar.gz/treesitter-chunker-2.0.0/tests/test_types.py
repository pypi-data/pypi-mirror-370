"""Comprehensive tests for the type system."""

import json
from dataclasses import asdict, fields, replace
from pathlib import Path
from typing import get_type_hints

import pytest

from chunker.types import CodeChunk


class TestCodeChunkBasics:
    """Test basic CodeChunk functionality."""

    @staticmethod
    def test_dataclass_fields():
        """Test that CodeChunk has all expected fields."""
        field_names = {f.name for f in fields(CodeChunk)}
        expected_fields = {
            "language",
            "file_path",
            "node_type",
            "start_line",
            "end_line",
            "byte_start",
            "byte_end",
            "parent_context",
            "content",
            "chunk_id",
            "parent_chunk_id",
            "references",
            "dependencies",
            "metadata",
            # new identity & hierarchy
            "node_id",
            "file_id",
            "symbol_id",
            "parent_route",
        }
        assert field_names == expected_fields

    @staticmethod
    def test_field_types():
        """Test that fields have correct type annotations."""
        type_hints = get_type_hints(CodeChunk)
        for field in [
            "language",
            "file_path",
            "node_type",
            "parent_context",
            "content",
        ]:
            assert type_hints[field] is str
        for field in ["start_line", "end_line", "byte_start", "byte_end"]:
            assert type_hints[field] is int
        assert type_hints["chunk_id"] is str
        assert type_hints["parent_chunk_id"] == str | None
        assert type_hints["references"] == list[str]
        assert type_hints["dependencies"] == list[str]

    @classmethod
    def test_create_minimal_chunk(cls):
        """Test creating a chunk with minimal required fields."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test():
    pass""",
        )
        assert chunk.language == "python"
        assert chunk.file_path == "/test/file.py"
        assert chunk.node_type == "function"
        assert chunk.start_line == 1
        assert chunk.end_line == 5
        assert chunk.byte_start == 0
        assert chunk.byte_end == 100
        assert chunk.parent_context == "module"
        assert chunk.content == "def test():\n    pass"
        assert chunk.chunk_id
        assert chunk.parent_chunk_id is None
        assert chunk.references == []
        assert chunk.dependencies == []

    @classmethod
    def test_create_full_chunk(cls):
        """Test creating a chunk with all fields specified."""
        chunk = CodeChunk(
            language="javascript",
            file_path="/app/main.js",
            node_type="class",
            start_line=10,
            end_line=20,
            byte_start=150,
            byte_end=400,
            parent_context="module",
            content="class MyClass { }",
            chunk_id="custom_id_123",
            parent_chunk_id="parent_456",
            references=["ref1", "ref2"],
            dependencies=["dep1", "dep2", "dep3"],
        )
        assert chunk.chunk_id == "custom_id_123"
        assert chunk.parent_chunk_id == "parent_456"
        assert chunk.references == ["ref1", "ref2"]
        assert chunk.dependencies == ["dep1", "dep2", "dep3"]


class TestChunkIdGeneration:
    """Test chunk ID generation functionality."""

    @classmethod
    def test_generate_id_method(cls):
        """Test the generate_id method."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test():
    pass""",
        )
        generated_id = chunk.generate_id()
        assert len(generated_id) == 40
        assert all(c in "0123456789abcdef" for c in generated_id)
        assert chunk.generate_id() == generated_id

    @classmethod
    def test_auto_id_generation_on_init(cls):
        """Test that chunk_id is auto-generated when not provided."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test():
    pass""",
        )
        assert chunk.chunk_id
        assert len(chunk.chunk_id) == 40
        assert chunk.chunk_id == chunk.generate_id()

    @classmethod
    def test_custom_id_not_overwritten(cls):
        """Test that custom chunk_id is not overwritten."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test():
    pass""",
            chunk_id="my_custom_id",
        )
        assert chunk.chunk_id == "my_custom_id"
        assert chunk.chunk_id != chunk.generate_id()

    @classmethod
    def test_id_generation_uniqueness(cls):
        """Test that different chunks generate different IDs."""
        chunk1 = CodeChunk(
            language="python",
            file_path="/test/file1.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test1():
    pass""",
        )
        chunk2 = CodeChunk(
            language="python",
            file_path="/test/file2.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test1():
    pass""",
        )
        chunk3 = CodeChunk(
            language="python",
            file_path="/test/file1.py",
            node_type="function",
            start_line=10,
            end_line=15,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test1():
    pass""",
        )
        chunk4 = CodeChunk(
            language="python",
            file_path="/test/file1.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test2():
    pass""",
        )
        ids = {
            chunk1.chunk_id,
            chunk2.chunk_id,
            chunk3.chunk_id,
            chunk4.chunk_id,
        }
        # With stable IDs based on path/language/route/content,
        # identical content under same route can collide intentionally
        assert len(ids) >= 3
        assert chunk1.chunk_id == chunk3.chunk_id

    @classmethod
    def test_id_generation_consistency(cls):
        """Test that ID generation is consistent for same data."""
        chunk1 = CodeChunk(
            language="rust",
            file_path="/src/main.rs",
            node_type="function",
            start_line=42,
            end_line=50,
            byte_start=1000,
            byte_end=1500,
            parent_context="impl",
            content="fn process() -> Result<()> { Ok(()) }",
        )
        chunk2 = CodeChunk(
            language="rust",
            file_path="/src/main.rs",
            node_type="function",
            start_line=42,
            end_line=50,
            byte_start=1000,
            byte_end=1500,
            parent_context="impl",
            content="fn process() -> Result<()> { Ok(()) }",
        )
        assert chunk1.chunk_id == chunk2.chunk_id


class TestDataclassSerialization:
    """Test dataclass serialization and deserialization."""

    @classmethod
    def test_asdict_conversion(cls):
        """Test converting CodeChunk to dictionary using asdict."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="""def test():
    pass""",
            chunk_id="test_id",
            parent_chunk_id="parent_id",
            references=["ref1"],
            dependencies=["dep1", "dep2"],
        )
        chunk_dict = asdict(chunk)
        assert isinstance(chunk_dict, dict)
        assert chunk_dict["language"] == "python"
        assert chunk_dict["file_path"] == "/test/file.py"
        assert chunk_dict["node_type"] == "function"
        assert chunk_dict["start_line"] == 1
        assert chunk_dict["end_line"] == 5
        assert chunk_dict["byte_start"] == 0
        assert chunk_dict["byte_end"] == 100
        assert chunk_dict["parent_context"] == "module"
        assert chunk_dict["content"] == "def test():\n    pass"
        assert chunk_dict["chunk_id"] == "test_id"
        assert chunk_dict["parent_chunk_id"] == "parent_id"
        assert chunk_dict["references"] == ["ref1"]
        assert chunk_dict["dependencies"] == ["dep1", "dep2"]

    @classmethod
    def test_create_from_dict(cls):
        """Test creating CodeChunk from dictionary."""
        chunk_dict = {
            "language": "javascript",
            "file_path": "/app/index.js",
            "node_type": "function",
            "start_line": 10,
            "end_line": 20,
            "byte_start": 200,
            "byte_end": 400,
            "parent_context": "module",
            "content": "function main() { }",
            "chunk_id": "js_chunk_1",
            "parent_chunk_id": None,
            "references": ["React", "useState"],
            "dependencies": ["react", "lodash"],
        }
        chunk = CodeChunk(**chunk_dict)
        assert chunk.language == "javascript"
        assert chunk.file_path == "/app/index.js"
        assert chunk.node_type == "function"
        assert chunk.start_line == 10
        assert chunk.end_line == 20
        assert chunk.byte_start == 200
        assert chunk.byte_end == 400
        assert chunk.parent_context == "module"
        assert chunk.content == "function main() { }"
        assert chunk.chunk_id == "js_chunk_1"
        assert chunk.parent_chunk_id is None
        assert chunk.references == ["React", "useState"]
        assert chunk.dependencies == ["react", "lodash"]

    @classmethod
    def test_roundtrip_serialization(cls):
        """Test that chunk survives dict roundtrip."""
        original = CodeChunk(
            language="c++",
            file_path="/src/main.cpp",
            node_type="class",
            start_line=100,
            end_line=200,
            byte_start=2000,
            byte_end=5000,
            parent_context="namespace",
            content="class Engine { };",
            chunk_id="cpp_class_1",
            parent_chunk_id="namespace_1",
            references=["std::vector", "std::string"],
            dependencies=["iostream", "vector", "string"],
        )
        chunk_dict = asdict(original)
        reconstructed = CodeChunk(**chunk_dict)
        assert reconstructed.language == original.language
        assert reconstructed.file_path == original.file_path
        assert reconstructed.node_type == original.node_type
        assert reconstructed.start_line == original.start_line
        assert reconstructed.end_line == original.end_line
        assert reconstructed.byte_start == original.byte_start
        assert reconstructed.byte_end == original.byte_end
        assert reconstructed.parent_context == original.parent_context
        assert reconstructed.content == original.content
        assert reconstructed.chunk_id == original.chunk_id
        assert reconstructed.parent_chunk_id == original.parent_chunk_id
        assert reconstructed.references == original.references
        assert reconstructed.dependencies == original.dependencies

    @classmethod
    def test_json_serialization(cls):
        """Test JSON serialization and deserialization."""
        chunk = CodeChunk(
            language="rust",
            file_path="/src/lib.rs",
            node_type="function",
            start_line=50,
            end_line=60,
            byte_start=1000,
            byte_end=1200,
            parent_context="impl",
            content="pub fn new() -> Self { }",
            chunk_id="rust_fn_1",
            parent_chunk_id=None,
            references=["Self"],
            dependencies=[],
        )
        json_str = json.dumps(asdict(chunk), indent=2)
        assert isinstance(json_str, str)
        chunk_dict = json.loads(json_str)
        reconstructed = CodeChunk(**chunk_dict)
        assert reconstructed.language == chunk.language
        assert reconstructed.content == chunk.content
        assert reconstructed.chunk_id == chunk.chunk_id
        assert reconstructed.parent_chunk_id == chunk.parent_chunk_id
        assert reconstructed.references == chunk.references
        assert reconstructed.dependencies == chunk.dependencies


class TestFieldValidation:
    """Test field validation and edge cases."""

    @classmethod
    def test_empty_strings(cls):
        """Test behavior with empty strings."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/empty.py",
            node_type="module",
            start_line=1,
            end_line=1,
            byte_start=0,
            byte_end=0,
            parent_context="",
            content="",
        )
        assert not chunk.parent_context
        assert not chunk.content
        assert chunk.chunk_id

    @classmethod
    def test_line_number_edge_cases(cls):
        """Test edge cases for line numbers."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="statement",
            start_line=42,
            end_line=42,
            byte_start=100,
            byte_end=120,
            parent_context="function",
            content="return True",
        )
        assert chunk.start_line == chunk.end_line == 42

    @classmethod
    def test_byte_position_edge_cases(cls):
        """Test edge cases for byte positions."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="comment",
            start_line=1,
            end_line=1,
            byte_start=50,
            byte_end=50,
            parent_context="module",
            content="",
        )
        assert chunk.byte_start == chunk.byte_end == 50

    @classmethod
    def test_special_characters_in_content(cls):
        """Test handling of special characters in content."""
        special_content = """def test():
    print("Hello\\nWorld")  # Newline
    path = "C:\\\\Users\\\\test"  # Backslashes
    unicode = "Hello 世界 🌍"  # Unicode
    """
        chunk = CodeChunk(
            language="python",
            file_path="/test/special.py",
            node_type="function",
            start_line=1,
            end_line=4,
            byte_start=0,
            byte_end=len(special_content.encode()),
            parent_context="module",
            content=special_content,
        )
        assert chunk.content == special_content
        chunk_dict = asdict(chunk)
        reconstructed = CodeChunk(**chunk_dict)
        assert reconstructed.content == special_content

    @classmethod
    def test_none_parent_chunk_id(cls):
        """Test None value for parent_chunk_id."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="module",
            start_line=1,
            end_line=100,
            byte_start=0,
            byte_end=2000,
            parent_context="",
            content="# module content",
            parent_chunk_id=None,
        )
        assert chunk.parent_chunk_id is None
        chunk_dict = asdict(chunk)
        assert chunk_dict["parent_chunk_id"] is None

    @classmethod
    def test_empty_lists(cls):
        """Test empty lists for references and dependencies."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="def test(): pass",
            references=[],
            dependencies=[],
        )
        assert chunk.references == []
        assert chunk.dependencies == []
        chunk_dict = asdict(chunk)
        assert chunk_dict["references"] == []
        assert chunk_dict["dependencies"] == []


class TestDataclassFeatures:
    """Test dataclass-specific features."""

    @classmethod
    def test_equality(cls):
        """Test CodeChunk equality comparison."""
        chunk1 = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="def test(): pass",
        )
        chunk2 = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="def test(): pass",
        )
        assert chunk1 == chunk2
        assert chunk1.chunk_id == chunk2.chunk_id
        chunk3 = replace(chunk1, content="def test2(): pass")
        assert chunk1 != chunk3

    @classmethod
    def test_replace(cls):
        """Test using dataclasses.replace."""
        original = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="def test(): pass",
            chunk_id="original_id",
        )
        modified = replace(
            original,
            start_line=10,
            end_line=15,
            content="def modified(): pass",
        )
        assert modified.start_line == 10
        assert modified.end_line == 15
        assert modified.content == "def modified(): pass"
        assert modified.language == original.language
        assert modified.file_path == original.file_path
        assert modified.node_type == original.node_type
        assert modified.chunk_id == original.chunk_id

    @classmethod
    def test_field_defaults(cls):
        """Test field default values."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="def test(): pass",
        )
        assert chunk.chunk_id
        assert chunk.parent_chunk_id is None
        assert chunk.references == []
        assert chunk.dependencies == []
        chunk.references.append("ref1")
        chunk.dependencies.extend(["dep1", "dep2"])
        chunk2 = CodeChunk(
            language="python",
            file_path="/test/file2.py",
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="def test2(): pass",
        )
        assert chunk2.references == []
        assert chunk2.dependencies == []


class TestTypeCompatibility:
    """Test type compatibility and coercion."""

    @classmethod
    def test_accept_path_like_objects(cls):
        """Test that file_path can accept path-like strings."""
        path = Path("/test/file.py")
        chunk = CodeChunk(
            language="python",
            file_path=str(path),
            node_type="function",
            start_line=1,
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="def test(): pass",
        )
        assert chunk.file_path == "/test/file.py"

    @classmethod
    def test_type_flexibility(cls):
        """Test that dataclasses don't enforce runtime type checking."""
        chunk = CodeChunk(
            language="python",
            file_path="/test/file.py",
            node_type="function",
            start_line="1",
            end_line=5,
            byte_start=0,
            byte_end=100,
            parent_context="module",
            content="def test(): pass",
        )
        assert chunk.start_line == "1"
        assert chunk.end_line == 5
        with pytest.raises(TypeError):
            _ = chunk.start_line + 1


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    @classmethod
    def test_nested_function_chunks(cls):
        """Test representing nested functions."""
        outer = CodeChunk(
            language="python",
            file_path="/app/utils.py",
            node_type="function",
            start_line=10,
            end_line=20,
            byte_start=150,
            byte_end=400,
            parent_context="module",
            content="""def outer():
    def inner():
        pass""",
            chunk_id="outer_func",
        )
        inner = CodeChunk(
            language="python",
            file_path="/app/utils.py",
            node_type="function",
            start_line=11,
            end_line=12,
            byte_start=180,
            byte_end=220,
            parent_context="function:outer",
            content="""def inner():
        pass""",
            parent_chunk_id="outer_func",
        )
        assert inner.parent_chunk_id == outer.chunk_id
        assert "outer" in inner.parent_context

    @classmethod
    def test_class_with_methods(cls):
        """Test representing a class with multiple methods."""
        class_chunk = CodeChunk(
            language="python",
            file_path="/app/models.py",
            node_type="class",
            start_line=50,
            end_line=100,
            byte_start=1000,
            byte_end=3000,
            parent_context="module",
            content="""class User:
    ...""",
            chunk_id="user_class",
        )
        init_method = CodeChunk(
            language="python",
            file_path="/app/models.py",
            node_type="function",
            start_line=52,
            end_line=55,
            byte_start=1050,
            byte_end=1200,
            parent_context="class:User",
            content="""def __init__(self, name):
    self.name = name""",
            parent_chunk_id="user_class",
            references=["self"],
        )
        str_method = CodeChunk(
            language="python",
            file_path="/app/models.py",
            node_type="function",
            start_line=57,
            end_line=59,
            byte_start=1250,
            byte_end=1350,
            parent_context="class:User",
            content="""def __str__(self):
    return self.name""",
            parent_chunk_id="user_class",
            references=["self"],
            dependencies=["__init__"],
        )
        assert init_method.parent_chunk_id == class_chunk.chunk_id
        assert str_method.parent_chunk_id == class_chunk.chunk_id
        assert "__init__" in str_method.dependencies

    @classmethod
    def test_module_with_imports(cls):
        """Test representing a module with imports and dependencies."""
        chunk = CodeChunk(
            language="python",
            file_path="/app/main.py",
            node_type="module",
            start_line=1,
            end_line=200,
            byte_start=0,
            byte_end=5000,
            parent_context="",
            content="""import os
import sys
from typing import List
...""",
            dependencies=["os", "sys", "typing"],
            references=["List"],
        )
        assert "os" in chunk.dependencies
        assert "sys" in chunk.dependencies
        assert "typing" in chunk.dependencies
        assert "List" in chunk.references

    @classmethod
    def test_javascript_arrow_function(cls):
        """Test representing JavaScript arrow functions."""
        chunk = CodeChunk(
            language="javascript",
            file_path="/app/handlers.js",
            node_type="arrow_function",
            start_line=25,
            end_line=30,
            byte_start=500,
            byte_end=650,
            parent_context="module",
            content="""const handleClick = (event) => {
  console.log(event);
}""",
            chunk_id="handle_click",
            references=["console", "event"],
        )
        assert chunk.node_type == "arrow_function"
        assert "console" in chunk.references
        assert "event" in chunk.references


class TestLargeScaleData:
    """Test handling of large-scale data."""

    @classmethod
    def test_large_content(cls):
        """Test chunk with large content."""
        large_content = "x" * 10000
        chunk = CodeChunk(
            language="text",
            file_path="/test/large.txt",
            node_type="file",
            start_line=1,
            end_line=1000,
            byte_start=0,
            byte_end=10000,
            parent_context="",
            content=large_content,
        )
        assert len(chunk.content) == 10000
        chunk_dict = asdict(chunk)
        assert len(chunk_dict["content"]) == 10000
        json_str = json.dumps(chunk_dict)
        assert large_content in json_str

    @classmethod
    def test_many_dependencies(cls):
        """Test chunk with many dependencies and references."""
        deps = [f"dependency_{i}" for i in range(100)]
        refs = [f"reference_{i}" for i in range(100)]
        chunk = CodeChunk(
            language="python",
            file_path="/test/complex.py",
            node_type="module",
            start_line=1,
            end_line=5000,
            byte_start=0,
            byte_end=100000,
            parent_context="",
            content="# Complex module",
            dependencies=deps,
            references=refs,
        )
        assert len(chunk.dependencies) == 100
        assert len(chunk.references) == 100
        assert chunk.dependencies[50] == "dependency_50"
        assert chunk.references[75] == "reference_75"

    @classmethod
    def test_batch_creation_performance(cls):
        """Test creating many chunks efficiently."""
        chunks = []
        for i in range(1000):
            chunk = CodeChunk(
                language="python",
                file_path=f"/test/file_{i}.py",
                node_type="function",
                start_line=i * 10,
                end_line=i * 10 + 5,
                byte_start=i * 100,
                byte_end=i * 100 + 50,
                parent_context="module",
                content=f"def function_{i}(): pass",
            )
            chunks.append(chunk)
        assert len(chunks) == 1000
        ids = {c.chunk_id for c in chunks}
        assert len(ids) == 1000
        all_dicts = [asdict(c) for c in chunks]
        assert len(all_dicts) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
