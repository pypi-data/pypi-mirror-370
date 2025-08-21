"""
Rust extractor module for Phase 2 call site extraction.

This module provides specialized extraction capabilities for Rust source code,
including support for function calls, method calls, macro invocations, and
other Rust-specific language constructs.
"""

from .rust_extractor import RustExtractor, RustPatterns

__all__ = ['RustExtractor', 'RustPatterns']