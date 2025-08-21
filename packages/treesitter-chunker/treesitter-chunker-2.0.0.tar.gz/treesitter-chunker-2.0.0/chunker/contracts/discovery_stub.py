"""Concrete stub implementation for testing - Grammar Discovery"""

from datetime import datetime

from .discovery_contract import (
    GrammarCompatibility,
    GrammarDiscoveryContract,
    GrammarInfo,
)


class GrammarDiscoveryStub(GrammarDiscoveryContract):
    """Stub implementation that can be instantiated and tested"""

    @staticmethod
    def list_available_grammars(
        include_community: bool = False,
    ) -> list[GrammarInfo]:
        """Stub that returns valid default values"""
        return [
            GrammarInfo(
                name="python",
                url="https://github.com/tree-sitter/tree-sitter-python",
                version="0.20.0",
                last_updated=datetime(2023, 1, 1),
                stars=500,
                description="Python grammar for tree-sitter",
                supported_extensions=[".py", ".pyw"],
                official=True,
            ),
            GrammarInfo(
                name="rust",
                url="https://github.com/tree-sitter/tree-sitter-rust",
                version="0.20.0",
                last_updated=datetime(2023, 1, 1),
                stars=400,
                description="Rust grammar for tree-sitter",
                supported_extensions=[".rs"],
                official=True,
            ),
        ]

    @staticmethod
    def get_grammar_info(language: str) -> GrammarInfo | None:
        """Stub that returns info for known languages"""
        if language == "python":
            return GrammarInfo(
                name="python",
                url="https://github.com/tree-sitter/tree-sitter-python",
                version="0.20.0",
                last_updated=datetime(2023, 1, 1),
                stars=500,
                description="Python grammar for tree-sitter",
                supported_extensions=[".py", ".pyw"],
                official=True,
            )
        if language == "rust":
            return GrammarInfo(
                name="rust",
                url="https://github.com/tree-sitter/tree-sitter-rust",
                version="0.20.0",
                last_updated=datetime(2023, 1, 1),
                stars=400,
                description="Rust grammar for tree-sitter",
                supported_extensions=[".rs"],
                official=True,
            )
        return None

    @staticmethod
    def check_grammar_updates(
        installed_grammars: dict[str, str],
    ) -> dict[str, tuple[str, str]]:
        """Stub that simulates updates available"""
        updates = {}
        for lang, version in installed_grammars.items():
            if (lang == "python" and version < "0.20.0") or (
                lang == "rust" and version < "0.20.0"
            ):
                updates[lang] = version, "0.20.0"
        return updates

    @staticmethod
    def get_grammar_compatibility(
        language: str,
        version: str,
    ) -> GrammarCompatibility:
        """Stub that returns valid compatibility info"""
        return GrammarCompatibility(
            min_tree_sitter_version="0.20.0",
            max_tree_sitter_version="0.22.0",
            abi_version=14,
            tested_python_versions=["3.8", "3.9", "3.10", "3.11"],
        )

    @staticmethod
    def search_grammars(query: str) -> list[GrammarInfo]:
        """Stub that searches through minimal grammar list"""
        query_lower = query.lower()
        all_grammars = GrammarDiscoveryStub.list_available_grammars(
            include_community=True,
        )
        return [
            g
            for g in all_grammars
            if query_lower in g.name.lower() or query_lower in g.description.lower()
        ]

    @staticmethod
    def refresh_cache() -> bool:
        """Stub that always succeeds"""
        return True
