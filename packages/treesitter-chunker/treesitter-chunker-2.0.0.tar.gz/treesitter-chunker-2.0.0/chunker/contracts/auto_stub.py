"""Concrete stub implementation for testing - Zero-Config API"""

from pathlib import Path
from typing import Any

from .auto_contract import AutoChunkResult, ZeroConfigContract


class ZeroConfigStub(ZeroConfigContract):
    """Stub implementation that can be instantiated and tested"""

    # Class-level state to support static methods
    _installed_languages = {"python", "rust", "javascript"}
    _extension_map = {
        ".py": "python",
        ".pyw": "python",
        ".rs": "rust",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".go": "go",
        ".java": "java",
        ".rb": "ruby",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
    }

    @staticmethod
    def ensure_language(
        language: str,
        version: str | None = None,
    ) -> bool:
        """Stub that simulates language setup"""
        if language in {
            "python",
            "rust",
            "javascript",
            "go",
            "java",
            "ruby",
            "c",
            "cpp",
        }:
            ZeroConfigStub._installed_languages.add(language)
            return True
        return False

    @staticmethod
    def auto_chunk_file(
        file_path: str | Path,
        language: str | None = None,
        token_limit: int | None = None,
    ) -> AutoChunkResult:
        """Stub that simulates auto chunking"""
        path = Path(file_path)
        if not language:
            language = ZeroConfigStub.detect_language(path)
        grammar_downloaded = False
        if language and language not in ZeroConfigStub._installed_languages:
            grammar_downloaded = ZeroConfigStub.ensure_language(language)
        return AutoChunkResult(
            chunks=[
                {
                    "id": "chunk_1",
                    "content": f"# Stub chunk for {path.name}",
                    "start_line": 1,
                    "end_line": 10,
                    "type": "function" if language else "text",
                },
            ],
            language=language or "unknown",
            grammar_downloaded=grammar_downloaded,
            fallback_used=not bool(language),
            metadata={"file_path": str(path), "file_size": 1000, "total_chunks": 1},
        )

    @staticmethod
    def detect_language(file_path: str | Path) -> str | None:
        """Stub that detects language from extension"""
        path = Path(file_path)
        extension = path.suffix.lower()
        return ZeroConfigStub._extension_map.get(extension)

    @staticmethod
    def chunk_text(
        text: str,
        language: str,
        token_limit: int | None = None,
    ) -> AutoChunkResult:
        """Stub that chunks text"""
        grammar_downloaded = False
        if language not in ZeroConfigStub._installed_languages:
            grammar_downloaded = ZeroConfigStub.ensure_language(language)
        return AutoChunkResult(
            chunks=[
                {
                    "id": "chunk_1",
                    "content": text[:100] if len(text) > 100 else text,
                    "start_line": 1,
                    "end_line": text.count("\n") + 1,
                    "type": "code",
                },
            ],
            language=language,
            grammar_downloaded=grammar_downloaded,
            fallback_used=False,
            metadata={"text_length": len(text), "total_chunks": 1},
        )

    @staticmethod
    def list_supported_extensions() -> dict[str, list[str]]:
        """Stub that returns extension mappings"""
        language_extensions: dict[str, list[str]] = {}
        for ext, lang in ZeroConfigStub._extension_map.items():
            if lang not in language_extensions:
                language_extensions[lang] = []
            language_extensions[lang].append(ext)
        return language_extensions

    @staticmethod
    def get_chunker_for_language(
        language: str,
        auto_download: bool = True,
    ) -> Any:
        """Stub that returns a mock chunker"""
        if auto_download:
            ZeroConfigStub.ensure_language(language)
        if language not in ZeroConfigStub._installed_languages:
            raise ValueError(f"Language {language} not available")

        class MockChunker:

            def __init__(self, lang):
                self.language = lang

            @staticmethod
            def chunk(text):
                return [{"content": text, "type": "mock"}]

        return MockChunker(language)

    @staticmethod
    def preload_languages(languages: list[str]) -> dict[str, bool]:
        """Stub that simulates preloading"""
        results = {}
        for lang in languages:
            success = ZeroConfigStub.ensure_language(lang)
            results[lang] = success
            if success:
                ZeroConfigStub._installed_languages.add(lang)
        return results
