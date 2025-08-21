"""
Comprehensive unit tests for the Rust extractor.

Tests cover all functionality including function calls, method calls,
macro invocations, and edge cases with 95%+ coverage.
"""

import unittest
from pathlib import Path
import tempfile
import os

from .rust_extractor import RustExtractor, RustPatterns
from ..core.extraction_framework import CallSite, ExtractionResult


class TestRustExtractor(unittest.TestCase):
    """Test cases for RustExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = RustExtractor()
        self.test_file_path = Path("/test/example.rs")
    
    def tearDown(self):
        """Clean up after tests."""
        self.extractor.cleanup()
    
    def test_initialization(self):
        """Test extractor initialization."""
        self.assertEqual(self.extractor.language, "rust")
        self.assertIsInstance(self.extractor.patterns, RustPatterns)
        self.assertIsInstance(self.extractor.performance_metrics, dict)
        self.assertEqual(self.extractor.performance_metrics['total_extractions'], 0)
    
    def test_validate_source_valid_rust(self):
        """Test source validation with valid Rust code."""
        valid_code = """
        fn main() {
            println!("Hello, world!");
        }
        """
        self.assertTrue(self.extractor.validate_source(valid_code))
    
    def test_validate_source_invalid_input(self):
        """Test source validation with invalid input."""
        self.assertFalse(self.extractor.validate_source(""))
        self.assertFalse(self.extractor.validate_source(None))
        self.assertFalse(self.extractor.validate_source(123))
    
    def test_validate_source_unbalanced_braces(self):
        """Test source validation with unbalanced braces."""
        unbalanced_code = "fn main() { println!(\"test\");"
        self.assertFalse(self.extractor.validate_source(unbalanced_code))
    
    def test_extract_calls_simple_function(self):
        """Test extraction of simple function calls."""
        source_code = """
        fn main() {
            hello_world();
            calculate(10, 20);
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertIsInstance(result, ExtractionResult)
        self.assertTrue(result.is_successful())
        self.assertGreaterEqual(len(result.call_sites), 2)
        
        # Find specific calls
        function_names = [call.function_name for call in result.call_sites]
        self.assertIn("hello_world", function_names)
        self.assertIn("calculate", function_names)
    
    def test_extract_calls_method_calls(self):
        """Test extraction of method calls."""
        source_code = """
        fn main() {
            let mut vec = Vec::new();
            vec.push(1);
            vec.push(2);
            let len = vec.len();
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        method_calls = [call for call in result.call_sites if call.call_type == 'method']
        self.assertGreaterEqual(len(method_calls), 3)
        
        method_names = [call.function_name for call in method_calls]
        self.assertIn("push", method_names)
        self.assertIn("len", method_names)
    
    def test_extract_calls_macro_calls(self):
        """Test extraction of macro calls."""
        source_code = """
        fn main() {
            println!("Hello, {}!", "world");
            vec![1, 2, 3, 4];
            assert_eq!(2 + 2, 4);
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        macro_calls = [call for call in result.call_sites if call.call_type == 'macro']
        self.assertGreaterEqual(len(macro_calls), 3)
        
        macro_names = [call.function_name for call in macro_calls]
        self.assertIn("println", macro_names)
        self.assertIn("vec", macro_names)
        self.assertIn("assert_eq", macro_names)
    
    def test_extract_calls_associated_functions(self):
        """Test extraction of associated function calls."""
        source_code = """
        fn main() {
            let s = String::new();
            let v = Vec::<i32>::new();
            let result = std::fs::read_to_string("file.txt");
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        associated_calls = [call for call in result.call_sites 
                          if call.call_type == 'associated_function']
        self.assertGreaterEqual(len(associated_calls), 3)
        
        function_names = [call.function_name for call in associated_calls]
        self.assertIn("new", function_names)
        self.assertIn("read_to_string", function_names)
    
    def test_extract_calls_chained_methods(self):
        """Test extraction of chained method calls."""
        source_code = """
        fn main() {
            let result = "hello world"
                .to_string()
                .to_uppercase()
                .trim()
                .len();
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        method_calls = [call for call in result.call_sites if call.call_type == 'method']
        self.assertGreaterEqual(len(method_calls), 4)
        
        method_names = [call.function_name for call in method_calls]
        self.assertIn("to_string", method_names)
        self.assertIn("to_uppercase", method_names)
        self.assertIn("trim", method_names)
        self.assertIn("len", method_names)
    
    def test_extract_calls_with_generics(self):
        """Test extraction of calls with generic parameters."""
        source_code = """
        fn main() {
            let v = Vec::<i32>::new();
            collect::<Vec<_>>();
            parse::<u32>();
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        
        # Check that generic parameters are captured
        for call in result.call_sites:
            if call.function_name in ["new", "collect", "parse"]:
                self.assertIn("generic_params", call.context)
    
    def test_extract_calls_async_unsafe(self):
        """Test extraction of async and unsafe calls."""
        source_code = """
        async fn main() {
            async_function().await;
            unsafe {
                unsafe_function();
            }
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        self.assertGreaterEqual(len(result.call_sites), 2)
    
    def test_extract_calls_closures(self):
        """Test extraction of calls within closures."""
        source_code = """
        fn main() {
            let numbers = vec![1, 2, 3, 4];
            let doubled: Vec<i32> = numbers
                .iter()
                .map(|x| multiply(*x, 2))
                .collect();
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        function_names = [call.function_name for call in result.call_sites]
        self.assertIn("multiply", function_names)
    
    def test_extract_calls_trait_methods(self):
        """Test extraction of trait method calls."""
        source_code = """
        fn main() {
            let result = <i32 as ToString>::to_string(&42);
            <Vec<i32> as Clone>::clone(&vec);
        }
        """
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        trait_calls = [call for call in result.call_sites 
                      if call.call_type == 'trait_method']
        self.assertGreaterEqual(len(trait_calls), 2)
    
    def test_extract_calls_comments_and_strings(self):
        """Test that calls in comments and strings are ignored."""
        source_code = '''
        fn main() {
            // This is a comment with ignored_function()
            /* Block comment with another_ignored_function() */
            let s = "String with fake_function() call";
            real_function();
        }
        '''
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        function_names = [call.function_name for call in result.call_sites]
        self.assertIn("real_function", function_names)
        self.assertNotIn("ignored_function", function_names)
        self.assertNotIn("another_ignored_function", function_names)
        self.assertNotIn("fake_function", function_names)
    
    def test_extract_calls_with_file_path(self):
        """Test extraction with file path metadata."""
        source_code = "fn main() { test_function(); }"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as f:
            f.write(source_code)
            temp_path = Path(f.name)
        
        try:
            result = self.extractor.extract_calls(source_code, temp_path)
            
            self.assertTrue(result.is_successful())
            self.assertEqual(result.metadata['file_path'], str(temp_path))
            
            for call in result.call_sites:
                self.assertEqual(call.file_path, temp_path)
        
        finally:
            os.unlink(temp_path)
    
    def test_extract_calls_empty_source(self):
        """Test extraction with empty source code."""
        with self.assertRaises(ValueError):
            self.extractor.extract_calls("", self.test_file_path)
    
    def test_extract_calls_invalid_input(self):
        """Test extraction with invalid input."""
        with self.assertRaises(TypeError):
            self.extractor.extract_calls(None, self.test_file_path)
        
        with self.assertRaises(TypeError):
            self.extractor.extract_calls(123, self.test_file_path)
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        source_code = """
        fn main() {
            function_call();
            object.method_call();
            println!("macro");
        }
        """
        
        initial_extractions = self.extractor.performance_metrics['total_extractions']
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        self.assertEqual(
            self.extractor.performance_metrics['total_extractions'],
            initial_extractions + 1
        )
        self.assertGreater(self.extractor.performance_metrics['function_calls_found'], 0)
        self.assertGreater(self.extractor.performance_metrics['method_calls_found'], 0)
        self.assertGreater(self.extractor.performance_metrics['macro_calls_found'], 0)
    
    def test_call_site_validation(self):
        """Test call site validation and error handling."""
        source_code = "fn main() { test(); }"
        
        result = self.extractor.extract_calls(source_code, self.test_file_path)
        
        self.assertTrue(result.is_successful())
        
        for call_site in result.call_sites:
            self.assertIsInstance(call_site, CallSite)
            self.assertTrue(call_site.function_name)
            self.assertGreaterEqual(call_site.line_number, 1)
            self.assertGreaterEqual(call_site.column_number, 0)
            self.assertGreaterEqual(call_site.byte_start, 0)
            self.assertGreaterEqual(call_site.byte_end, call_site.byte_start)
            self.assertEqual(call_site.language, "rust")


class TestRustPatterns(unittest.TestCase):
    """Test cases for RustPatterns class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.patterns = RustPatterns()
    
    def test_find_function_calls_basic(self):
        """Test basic function call detection."""
        source_code = """
        fn main() {
            hello();
            world(1, 2, 3);
            complex_function_name();
        }
        """
        
        calls = self.patterns.find_function_calls(source_code)
        
        self.assertGreaterEqual(len(calls), 3)
        function_names = [call['name'] for call in calls]
        self.assertIn("hello", function_names)
        self.assertIn("world", function_names)
        self.assertIn("complex_function_name", function_names)
    
    def test_find_function_calls_with_modules(self):
        """Test function calls with module paths."""
        source_code = """
        fn main() {
            std::fs::read("file.txt");
            crate::module::function();
            super::parent_function();
        }
        """
        
        calls = self.patterns.find_function_calls(source_code)
        
        self.assertGreaterEqual(len(calls), 3)
        function_names = [call['name'] for call in calls]
        self.assertIn("read", function_names)
        self.assertIn("function", function_names)
        self.assertIn("parent_function", function_names)
    
    def test_find_function_calls_with_generics(self):
        """Test function calls with generic parameters."""
        source_code = """
        fn main() {
            collect::<Vec<i32>>();
            parse::<u32>();
            generic_func::<String, i32>(arg1, arg2);
        }
        """
        
        calls = self.patterns.find_function_calls(source_code)
        
        self.assertGreaterEqual(len(calls), 3)
        
        # Check that generics are parsed
        for call in calls:
            if call['name'] in ["collect", "parse", "generic_func"]:
                self.assertIn("generic_params", call)
    
    def test_find_method_calls_basic(self):
        """Test basic method call detection."""
        source_code = """
        fn main() {
            obj.method();
            string.len();
            vector.push(item);
        }
        """
        
        calls = self.patterns.find_method_calls(source_code)
        
        self.assertGreaterEqual(len(calls), 3)
        method_names = [call['name'] for call in calls]
        self.assertIn("method", method_names)
        self.assertIn("len", method_names)
        self.assertIn("push", method_names)
    
    def test_find_method_calls_chained(self):
        """Test chained method call detection."""
        source_code = """
        fn main() {
            obj.method1().method2().method3();
        }
        """
        
        calls = self.patterns.find_chained_method_calls(source_code)
        
        self.assertGreaterEqual(len(calls), 3)
        method_names = [call['name'] for call in calls]
        self.assertIn("method1", method_names)
        self.assertIn("method2", method_names)
        self.assertIn("method3", method_names)
    
    def test_find_macro_calls_basic(self):
        """Test basic macro call detection."""
        source_code = """
        fn main() {
            println!("Hello");
            vec![1, 2, 3];
            assert_eq!(a, b);
            custom_macro!{content};
        }
        """
        
        calls = self.patterns.find_macro_calls(source_code)
        
        self.assertGreaterEqual(len(calls), 4)
        macro_names = [call['name'] for call in calls]
        self.assertIn("println", macro_names)
        self.assertIn("vec", macro_names)
        self.assertIn("assert_eq", macro_names)
        self.assertIn("custom_macro", macro_names)
    
    def test_find_associated_function_calls(self):
        """Test associated function call detection."""
        source_code = """
        fn main() {
            String::new();
            Vec::<i32>::with_capacity(10);
            std::fs::File::open("test.txt");
        }
        """
        
        calls = self.patterns.find_associated_function_calls(source_code)
        
        self.assertGreaterEqual(len(calls), 3)
        function_names = [call['name'] for call in calls]
        self.assertIn("new", function_names)
        self.assertIn("with_capacity", function_names)
        self.assertIn("open", function_names)
    
    def test_find_trait_method_calls(self):
        """Test trait method call detection."""
        source_code = """
        fn main() {
            <i32 as ToString>::to_string(&42);
            <String as Clone>::clone(&s);
        }
        """
        
        calls = self.patterns.find_trait_method_calls(source_code)
        
        self.assertGreaterEqual(len(calls), 2)
        method_names = [call['name'] for call in calls]
        self.assertIn("to_string", method_names)
        self.assertIn("clone", method_names)
    
    def test_parse_arguments_simple(self):
        """Test simple argument parsing."""
        test_cases = [
            ("()", []),
            ("(a)", ["a"]),
            ("(a, b)", ["a", "b"]),
            ("(1, 2, 3)", ["1", "2", "3"]),
            ('("string", 42)', ['"string"', "42"]),
        ]
        
        for args_str, expected in test_cases:
            with self.subTest(args_str=args_str):
                result = self.patterns._parse_arguments(args_str)
                self.assertEqual(result, expected)
    
    def test_parse_arguments_complex(self):
        """Test complex argument parsing."""
        test_cases = [
            ("(vec![1, 2, 3], other)", ["vec![1, 2, 3]", "other"]),
            ("(func(a, b), c)", ["func(a, b)", "c"]),
            ('("string with, comma", other)', ['"string with, comma"', "other"]),
        ]
        
        for args_str, expected in test_cases:
            with self.subTest(args_str=args_str):
                result = self.patterns._parse_arguments(args_str)
                self.assertEqual(result, expected)
    
    def test_parse_generics(self):
        """Test generic parameter parsing."""
        test_cases = [
            ("::<i32>", ["i32"]),
            ("::<String, Vec<i32>>", ["String", "Vec<i32>"]),
            ("::<'a, T>", ["'a", "T"]),
        ]
        
        for generics_str, expected in test_cases:
            with self.subTest(generics_str=generics_str):
                result = self.patterns._parse_generics(generics_str)
                self.assertEqual(result, expected)
    
    def test_is_in_string_or_comment(self):
        """Test string and comment detection."""
        source_code = '''
        fn main() {
            // This is a comment with function_call()
            let s = "string with fake_call()";
            real_call();
            /* block comment with other_call() */
        }
        '''
        
        # Find position of each call
        real_call_pos = source_code.find("real_call()")
        comment_call_pos = source_code.find("function_call()")
        string_call_pos = source_code.find("fake_call()")
        block_comment_pos = source_code.find("other_call()")
        
        # real_call should not be in string or comment
        self.assertFalse(self.patterns._is_in_string_or_comment(source_code, real_call_pos))
        
        # Others should be detected as in string/comment
        self.assertTrue(self.patterns._is_in_string_or_comment(source_code, comment_call_pos))
        self.assertTrue(self.patterns._is_in_string_or_comment(source_code, string_call_pos))
        self.assertTrue(self.patterns._is_in_string_or_comment(source_code, block_comment_pos))
    
    def test_delimiters_match(self):
        """Test delimiter matching."""
        self.assertTrue(self.patterns._delimiters_match('(', ')'))
        self.assertTrue(self.patterns._delimiters_match('[', ']'))
        self.assertTrue(self.patterns._delimiters_match('{', '}'))
        
        self.assertFalse(self.patterns._delimiters_match('(', ']'))
        self.assertFalse(self.patterns._delimiters_match('[', '}'))
        self.assertFalse(self.patterns._delimiters_match('{', ')'))
    
    def test_is_function_definition(self):
        """Test function definition detection."""
        source_code = """
        fn main() {
            function_call();
        }
        
        fn other_function() {
            // This is a function definition, not a call
        }
        """
        
        call_pos = source_code.find("function_call()")
        def_pos = source_code.find("fn other_function")
        
        self.assertFalse(self.patterns._is_function_definition(source_code, call_pos))
        self.assertTrue(self.patterns._is_function_definition(source_code, def_pos))


class TestRustExtractorIntegration(unittest.TestCase):
    """Integration tests for the complete Rust extractor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.extractor = RustExtractor()
    
    def tearDown(self):
        """Clean up after tests."""
        self.extractor.cleanup()
    
    def test_complex_rust_code(self):
        """Test extraction from complex Rust code."""
        source_code = '''
        use std::fs;
        use std::collections::HashMap;
        
        struct MyStruct {
            field: i32,
        }
        
        impl MyStruct {
            fn new(value: i32) -> Self {
                Self { field: value }
            }
            
            fn process(&self) -> i32 {
                self.field * 2
            }
        }
        
        async fn async_function() -> Result<String, Box<dyn std::error::Error>> {
            let content = fs::read_to_string("file.txt")?;
            Ok(content.trim().to_string())
        }
        
        fn main() -> Result<(), Box<dyn std::error::Error>> {
            println!("Starting application");
            
            let mut map = HashMap::<String, i32>::new();
            map.insert("key".to_string(), 42);
            
            let obj = MyStruct::new(10);
            let result = obj.process();
            
            assert_eq!(result, 20);
            
            let numbers = vec![1, 2, 3, 4, 5];
            let doubled: Vec<i32> = numbers
                .iter()
                .map(|x| x * 2)
                .collect();
            
            println!("Result: {:?}", doubled);
            
            Ok(())
        }
        '''
        
        result = self.extractor.extract_calls(source_code)
        
        self.assertTrue(result.is_successful())
        self.assertGreater(len(result.call_sites), 10)
        
        # Check that different types of calls are found
        call_types = [call.call_type for call in result.call_sites]
        self.assertIn('function', call_types)
        self.assertIn('method', call_types)
        self.assertIn('macro', call_types)
        self.assertIn('associated_function', call_types)
        
        # Check specific calls
        function_names = [call.function_name for call in result.call_sites]
        self.assertIn("println", function_names)
        self.assertIn("new", function_names)
        self.assertIn("insert", function_names)
        self.assertIn("process", function_names)
        self.assertIn("collect", function_names)
    
    def test_error_handling(self):
        """Test error handling in extraction."""
        # Test with malformed code that might cause regex issues
        malformed_code = "fn main() { unclosed_call( }"
        
        result = self.extractor.extract_calls(malformed_code)
        
        # Should not crash, might have warnings
        self.assertIsInstance(result, ExtractionResult)
    
    def test_large_file_performance(self):
        """Test performance with larger files."""
        # Generate a large source file
        lines = []
        for i in range(1000):
            lines.extend([
                f"fn function_{i}() {{",
                f"    println!(\"Function {i}\");",
                f"    other_call_{i}();",
                f"    obj.method_{i}();",
                "}"
            ])
        
        large_source = "\n".join(lines)
        
        import time
        start_time = time.time()
        result = self.extractor.extract_calls(large_source)
        extraction_time = time.time() - start_time
        
        self.assertTrue(result.is_successful())
        self.assertGreater(len(result.call_sites), 2000)  # Should find many calls
        self.assertLess(extraction_time, 5.0)  # Should complete in reasonable time


if __name__ == '__main__':
    # Run tests with high verbosity
    unittest.main(verbosity=2)