"""Tree-sitter grammar validator implementation."""

import ctypes
import logging
import platform
from pathlib import Path

from chunker._internal.registry import LanguageRegistry
from chunker.exceptions import ChunkerError
from chunker.interfaces.grammar import GrammarValidator

logger = logging.getLogger(__name__)


class ValidationError(ChunkerError):
    """Error during grammar validation."""


class TreeSitterGrammarValidator(GrammarValidator):
    """Validates grammar compatibility and correctness."""

    def __init__(self):
        """Initialize grammar validator."""
        self._registry = LanguageRegistry()

    @staticmethod
    def check_abi_compatibility(grammar_path: Path) -> tuple[bool, str | None]:
        """Check if grammar ABI is compatible.

        Args:
            grammar_path: Path to compiled grammar

        Returns:
            Tuple of (is_compatible, error_message)
        """
        if not grammar_path.exists():
            return False, f"Grammar file not found: {grammar_path}"
        try:
            system = platform.system()
            if system == "Windows":
                lib = ctypes.CDLL(str(grammar_path))
            else:
                lib = ctypes.cdll.LoadLibrary(str(grammar_path))
            language_name = grammar_path.stem
            if language_name.startswith("lib"):
                language_name = language_name[3:]
            func_name = f"tree_sitter_{language_name}"
            if not hasattr(lib, func_name):
                for variant in [
                    language_name.replace("-", "_"),
                    language_name.replace("_", ""),
                ]:
                    func_name = f"tree_sitter_{variant}"
                    if hasattr(lib, func_name):
                        break
                else:
                    return (False, f"No tree_sitter function found in {grammar_path}")
            lang_func = getattr(lib, func_name)
            lang_func.restype = ctypes.c_void_p
            lang_ptr = lang_func()
            if not lang_ptr:
                return False, "Language function returned null pointer"
            return True, None
        except (IndexError, KeyError) as e:
            return False, f"Failed to load grammar: {e!s}"

    def validate_node_types(
        self,
        language: str,
        expected_types: set[str],
    ) -> list[str]:
        """Validate expected node types exist.

        Args:
            language: Language name
            expected_types: Set of expected node type names

        Returns:
            List of missing node types
        """
        try:
            from chunker.parser import get_parser  # local import to avoid cycle

            parser = get_parser(language)
            test_code = self._get_minimal_test_code(language)
            tree = parser.parse(test_code.encode())
            found_types = set()
            self._collect_node_types(tree.root_node, found_types)
            missing = []
            critical_types = self._get_critical_node_types(language)
            for node_type in critical_types:
                if node_type in expected_types and node_type not in found_types:
                    logger.warning(
                        "Expected node type '%s' not found in test parse",
                        node_type,
                    )

                    missing.append(node_type)
            return missing
        except (IndexError, KeyError, SyntaxError) as e:
            logger.error("Failed to validate node types for %s: %s", language, e)
            return list(expected_types)

    def test_parse(self, language: str, sample_code: str) -> tuple[bool, str | None]:
        """Test parsing with sample code.

        Args:
            language: Language name
            sample_code: Sample code to parse

        Returns:
            Tuple of (success, error_message)
        """
        try:
            from chunker.parser import get_parser  # local import to avoid cycle

            parser = get_parser(language)
            tree = parser.parse(sample_code.encode())
            if tree.root_node is None:
                return False, "Parse resulted in null root node"
            if self._has_errors(tree.root_node):
                error_nodes = self._find_error_nodes(tree.root_node)
                error_info = ", ".join(
                    f"Error at {n.start_point}" for n in error_nodes[:3]
                )
                return False, f"Parse errors found: {error_info}"
            if tree.root_node.child_count == 0:
                return False, "Parse resulted in empty tree"
            return True, None
        except (IndexError, KeyError, SyntaxError) as e:
            return False, f"Parse failed: {e!s}"

    def validate_grammar_features(self, language: str) -> dict[str, bool]:
        """Validate specific grammar features.

        Args:
            language: Language name

        Returns:
            Dictionary of feature -> supported
        """
        features = {}
        try:
            from chunker.parser import get_parser  # local import to avoid cycle

            parser = get_parser(language)
            test_code = self._get_minimal_test_code(language)
            tree = parser.parse(test_code.encode())
            features["basic_parse"] = tree.root_node is not None
            unicode_code = self._get_unicode_test_code(language)
            if unicode_code:
                try:
                    tree = parser.parse(unicode_code.encode("utf-8"))
                    features["unicode"] = not self._has_errors(tree.root_node)
                except (IndexError, KeyError, SyntaxError):
                    features["unicode"] = False
            try:
                parser.parse(test_code.encode(), tree)
                features["incremental"] = True
            except (IndexError, KeyError, SyntaxError):
                features["incremental"] = False
            try:
                parser.set_timeout_micros(1000)
                features["timeout"] = True
            except (IndexError, KeyError, SyntaxError):
                features["timeout"] = False
            return features
        except (IndexError, KeyError, SyntaxError) as e:
            logger.error("Failed to validate features for %s: %s", language, e)
            return {"error": str(e)}

    def _collect_node_types(self, node, types: set[str]) -> None:
        """Recursively collect all node types in a tree."""
        if node.is_named:
            types.add(node.type)
        for child in node.children:
            self._collect_node_types(child, types)

    def _has_errors(self, node) -> bool:
        """Check if tree has any error nodes."""
        if node.type == "ERROR" or node.is_error:
            return True
        return any(self._has_errors(child) for child in node.children)

    def _find_error_nodes(self, node, errors=None):
        """Find all error nodes in tree."""
        if errors is None:
            errors = []
        if node.type == "ERROR" or node.is_error:
            errors.append(node)
        for child in node.children:
            self._find_error_nodes(child, errors)
        return errors

    @staticmethod
    def _get_minimal_test_code(language: str) -> str:
        """Get minimal valid code for a language."""
        minimal_code = {
            "python": "pass",
            "javascript": ";",
            "typescript": ";",
            "rust": "",
            "go": "package main",
            "ruby": "",
            "java": "class T{}",
            "c": "",
            "cpp": "",
            "csharp": "class T{}",
            "php": "<?php",
            "swift": "",
            "kotlin": "",
            "scala": "",
            "haskell": "",
            "lua": "",
            "bash": "",
            "json": "{}",
            "yaml": "---",
            "toml": "",
            "html": "<html></html>",
            "css": "",
            "sql": "SELECT 1",
            "markdown": "# Test",
        }
        return minimal_code.get(language, "")

    @staticmethod
    def _get_unicode_test_code(language: str) -> str | None:
        """Get unicode test code for a language."""
        unicode_tests = {
            "python": '# 你好\nx = "世界"',
            "javascript": '// 你好\nlet x = "世界";',
            "rust": """// 你好
let x = "世界";""",
            "go": """// 你好
var x = "世界\"""",
            "ruby": '# 你好\nx = "世界"',
            "java": """// 你好
String x = "世界";""",
        }
        return unicode_tests.get(language)

    @staticmethod
    def _get_critical_node_types(language: str) -> set[str]:
        """Get critical node types for a language."""
        critical_types = {
            "python": {"module", "function_definition", "class_definition"},
            "javascript": {"program", "function_declaration", "class_declaration"},
            "rust": {"source_file", "function_item", "struct_item"},
            "go": {"source_file", "function_declaration", "type_declaration"},
            "ruby": {"program", "method", "class"},
            "java": {"program", "method_declaration", "class_declaration"},
            "c": {"translation_unit", "function_definition", "struct_specifier"},
            "cpp": {"translation_unit", "function_definition", "class_specifier"},
        }
        return critical_types.get(language, set())
