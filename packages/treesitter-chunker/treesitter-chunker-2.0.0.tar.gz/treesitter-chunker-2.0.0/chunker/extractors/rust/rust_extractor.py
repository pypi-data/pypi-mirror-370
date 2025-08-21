"""
Rust-specific extractor for Phase 2 call site extraction.

This module provides specialized extraction for Rust source code,
supporting function calls, method calls, macro invocations, and
other Rust-specific language constructs.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import logging
import re
import time

from ..core.extraction_framework import BaseExtractor, ExtractionResult, CallSite, ExtractionUtils

logger = logging.getLogger(__name__)


class RustExtractor(BaseExtractor):
    """Specialized extractor for Rust source code."""
    
    def __init__(self):
        """Initialize Rust extractor."""
        super().__init__("rust")
        self.patterns = RustPatterns()
        self._regex_cache = {}
        
        # Initialize performance tracking
        self.performance_metrics = {
            'total_extractions': 0,
            'function_calls_found': 0,
            'method_calls_found': 0,
            'macro_calls_found': 0,
            'validation_failures': 0,
        }
        
        self.logger.debug("Initialized Rust extractor with pattern cache")
        
    def extract_calls(self, source_code: str, file_path: Optional[Path] = None) -> ExtractionResult:
        """
        Extract call sites from Rust source code.
        
        Args:
            source_code: The Rust source code to analyze
            file_path: Optional path to the source file
            
        Returns:
            ExtractionResult containing found call sites and metadata
        """
        start_time = time.perf_counter()
        result = ExtractionResult()
        
        # Validate input first - let exceptions propagate for invalid input
        self._validate_input(source_code, file_path)
        
        try:
            
            # Validate source code syntax
            if not self.validate_source(source_code):
                result.add_warning("Source code validation failed - may contain syntax errors")
            
            # Set up file path
            if file_path is None:
                file_path = Path("<unknown>")
            elif isinstance(file_path, str):
                file_path = Path(file_path)
            
            # Extract different types of calls
            with self._measure_performance('function_calls'):
                function_calls = self.extract_function_calls(source_code)
                
            with self._measure_performance('method_calls'):
                method_calls = self.extract_method_calls(source_code)
                
            with self._measure_performance('macro_calls'):
                macro_calls = self.extract_macro_calls(source_code)
            
            # Combine all call sites
            all_calls = function_calls + method_calls + macro_calls
            
            # Process and validate call sites
            processed_calls = []
            for call in all_calls:
                if isinstance(call, CallSite):
                    # Validate call site
                    validation_errors = ExtractionUtils.validate_call_site(call, source_code)
                    if validation_errors:
                        result.add_warning(f"Call site validation failed: {'; '.join(validation_errors)}")
                        self.performance_metrics['validation_failures'] += 1
                    else:
                        processed_calls.append(call)
                else:
                    # Convert raw call data to CallSite
                    try:
                        call_site = self._create_call_site(call, source_code, file_path)
                        if call_site:
                            processed_calls.append(call_site)
                    except Exception as e:
                        result.add_error(f"Failed to create call site: {e}")
            
            result.call_sites = processed_calls
            
            # Update performance metrics
            self.performance_metrics['total_extractions'] += 1
            self.performance_metrics['function_calls_found'] += len(function_calls)
            self.performance_metrics['method_calls_found'] += len(method_calls)
            self.performance_metrics['macro_calls_found'] += len(macro_calls)
            
            # Add metadata
            result.metadata.update({
                'language': 'rust',
                'file_path': str(file_path),
                'source_lines': len(source_code.splitlines()),
                'source_bytes': len(source_code.encode('utf-8')),
                'extractor_version': '1.0.0',
                'rust_specific_features': {
                    'function_calls': len(function_calls),
                    'method_calls': len(method_calls),
                    'macro_calls': len(macro_calls),
                    'total_calls': len(processed_calls)
                }
            })
            
            # Copy performance metrics
            result.performance_metrics.update(self.get_performance_metrics())
            
        except Exception as e:
            result.add_error("Failed to extract calls from Rust source", e)
        
        finally:
            result.extraction_time = time.perf_counter() - start_time
        
        self.logger.debug(f"Extracted {len(result.call_sites)} call sites in {result.extraction_time:.3f}s")
        return result
        
    def validate_source(self, source_code: str) -> bool:
        """
        Validate Rust source code.
        
        Args:
            source_code: The source code to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not source_code or not isinstance(source_code, str):
                return False
            
            # Basic syntax checks
            source_code = source_code.strip()
            if not source_code:
                return False
            
            # Check for balanced braces, brackets, and parentheses
            if not self._check_balanced_delimiters(source_code):
                return False
            
            # Check for basic Rust syntax patterns
            if not self._has_rust_syntax_patterns(source_code):
                # Allow files that might be partial or simple
                self.logger.debug("No clear Rust syntax patterns found, but allowing")
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error validating Rust source: {e}")
            return False
    
    def extract_function_calls(self, source_code: str) -> List[CallSite]:
        """
        Extract function calls from Rust code.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of CallSite objects for function calls
        """
        calls = []
        
        try:
            # Find regular function calls
            function_calls = self.patterns.find_function_calls(source_code)
            calls.extend(function_calls)
            
            # Find associated function calls (Type::function)
            associated_calls = self.patterns.find_associated_function_calls(source_code)
            calls.extend(associated_calls)
            
            # Find closure calls
            closure_calls = self.patterns.find_closure_calls(source_code)
            calls.extend(closure_calls)
            
        except Exception as e:
            self.logger.error(f"Error extracting function calls: {e}")
        
        return calls
        
    def extract_method_calls(self, source_code: str) -> List[CallSite]:
        """
        Extract method calls from Rust code.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of CallSite objects for method calls
        """
        calls = []
        
        try:
            # Find regular method calls
            method_calls = self.patterns.find_method_calls(source_code)
            calls.extend(method_calls)
            
            # Find chained method calls
            chained_calls = self.patterns.find_chained_method_calls(source_code)
            calls.extend(chained_calls)
            
            # Find trait method calls
            trait_calls = self.patterns.find_trait_method_calls(source_code)
            calls.extend(trait_calls)
            
        except Exception as e:
            self.logger.error(f"Error extracting method calls: {e}")
        
        return calls
    
    def extract_macro_calls(self, source_code: str) -> List[CallSite]:
        """
        Extract macro invocations from Rust code.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of CallSite objects for macro calls
        """
        calls = []
        
        try:
            # Find macro calls
            macro_calls = self.patterns.find_macro_calls(source_code)
            calls.extend(macro_calls)
            
        except Exception as e:
            self.logger.error(f"Error extracting macro calls: {e}")
        
        return calls
    
    def _create_call_site(self, call_data: Dict[str, Any], source_code: str, file_path: Path) -> Optional[CallSite]:
        """
        Create a CallSite object from extracted call data.
        
        Args:
            call_data: Dictionary containing call information
            source_code: Original source code
            file_path: Path to the source file
            
        Returns:
            CallSite object or None if creation failed
        """
        try:
            # Extract required fields
            function_name = call_data.get('name', '')
            if not function_name:
                return None
            
            # Calculate position information
            byte_start = call_data.get('start', 0)
            byte_end = call_data.get('end', byte_start + len(function_name))
            
            # Calculate line and column
            line_number, column_number = ExtractionUtils.calculate_line_column(source_code, byte_start)
            
            # Create context
            context = {
                'raw_match': call_data.get('match', ''),
                'call_pattern': call_data.get('pattern', ''),
                'arguments': call_data.get('arguments', []),
                'receiver': call_data.get('receiver', ''),
                'module_path': call_data.get('module_path', ''),
                'generic_params': call_data.get('generic_params', []),
                'is_async': call_data.get('is_async', False),
                'is_unsafe': call_data.get('is_unsafe', False),
                'in_macro': call_data.get('in_macro', False),
            }
            
            # Add additional context from call_data
            for key, value in call_data.items():
                if key not in context and key not in ['name', 'start', 'end', 'type']:
                    context[key] = value
            
            return CallSite(
                function_name=function_name,
                line_number=line_number,
                column_number=column_number,
                byte_start=byte_start,
                byte_end=byte_end,
                call_type=call_data.get('type', 'function'),
                context=context,
                language='rust',
                file_path=file_path
            )
            
        except Exception as e:
            self.logger.error(f"Error creating call site: {e}")
            return None
    
    def _check_balanced_delimiters(self, source_code: str) -> bool:
        """Check if delimiters are balanced in the source code."""
        try:
            # Track delimiter balance
            stack = []
            pairs = {'(': ')', '[': ']', '{': '}', '<': '>'}
            in_string = False
            in_char = False
            in_comment = False
            escape_next = False
            i = 0
            
            while i < len(source_code):
                char = source_code[i]
                
                # Handle escape sequences
                if escape_next:
                    escape_next = False
                    i += 1
                    continue
                
                if char == '\\':
                    escape_next = True
                    i += 1
                    continue
                
                # Handle comments
                if not in_string and not in_char:
                    if i < len(source_code) - 1:
                        two_char = source_code[i:i+2]
                        if two_char == '//':
                            # Line comment - skip to end of line
                            while i < len(source_code) and source_code[i] != '\n':
                                i += 1
                            continue
                        elif two_char == '/*':
                            # Block comment
                            in_comment = True
                            i += 2
                            continue
                
                if in_comment:
                    if i < len(source_code) - 1 and source_code[i:i+2] == '*/':
                        in_comment = False
                        i += 2
                        continue
                    i += 1
                    continue
                
                # Handle strings and characters
                if char == '"' and not in_char:
                    in_string = not in_string
                elif char == "'" and not in_string:
                    in_char = not in_char
                elif not in_string and not in_char:
                    # Handle delimiters
                    if char in pairs:
                        stack.append(char)
                    elif char in pairs.values():
                        if not stack:
                            return False
                        last = stack.pop()
                        if pairs.get(last) != char:
                            return False
                
                i += 1
            
            return len(stack) == 0 and not in_string and not in_char and not in_comment
            
        except Exception:
            return True  # If we can't check, assume it's okay
    
    def _has_rust_syntax_patterns(self, source_code: str) -> bool:
        """Check for Rust-specific syntax patterns."""
        rust_patterns = [
            r'\bfn\s+\w+',          # Function definitions
            r'\bstruct\s+\w+',      # Struct definitions
            r'\benum\s+\w+',        # Enum definitions
            r'\bimpl\s+',           # Implementation blocks
            r'\btrait\s+\w+',       # Trait definitions
            r'\buse\s+',            # Use statements
            r'\bmut\s+',            # Mutable variables
            r'\blet\s+',            # Variable declarations
            r'\bmatch\s+',          # Match expressions
            r'\bif\s+let\s+',       # If let expressions
            r'\bwhile\s+let\s+',    # While let expressions
            r'::',                   # Path separator
            r'\w+!',                # Macro calls
            r'&\w+',                # References
            r'->\s*\w+',            # Return types
        ]
        
        for pattern in rust_patterns:
            if re.search(pattern, source_code):
                return True
        
        return False


class RustPatterns:
    """Rust-specific pattern recognition using regex."""
    
    def __init__(self):
        """Initialize pattern cache."""
        self._compiled_patterns = {}
    
    def _get_pattern(self, name: str, pattern: str) -> re.Pattern:
        """Get compiled regex pattern with caching."""
        if name not in self._compiled_patterns:
            self._compiled_patterns[name] = re.compile(pattern, re.MULTILINE | re.DOTALL)
        return self._compiled_patterns[name]
    
    def find_function_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Find function calls using regex patterns.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of dictionaries containing call information
        """
        calls = []
        
        try:
            # Pattern for function calls including module paths: module::function(args) or function(args)
            # This pattern includes generics - using a simpler approach for nested generics
            function_pattern = self._get_pattern(
                'function_calls',
                r'(?:(\w+(?:::\w+)*?)::)?(\w+)(?:::<[^>]*(?:<[^>]*>[^>]*)?>)?\s*(\([^)]*\))'
            )
            
            for match in function_pattern.finditer(source_code):
                # Skip if this looks like a function definition
                if self._is_function_definition(source_code, match.start()):
                    continue
                
                # Skip if inside a string or comment
                if self._is_in_string_or_comment(source_code, match.start()):
                    continue
                
                # Skip if this is a method call (preceded by a dot)
                if match.start() > 0 and source_code[match.start() - 1] == '.':
                    continue
                
                module_path = match.group(1) or ''
                function_name = match.group(2)
                args = match.group(3)
                
                call_data = {
                    'name': function_name,
                    'type': 'function',
                    'start': match.start(),
                    'end': match.end(),
                    'match': match.group(0).strip(),
                    'pattern': 'function_call',
                    'module_path': module_path,
                    'arguments': self._parse_arguments(args),
                    'generic_params': [],
                }
                
                calls.append(call_data)
                
        except Exception as e:
            logger.error(f"Error finding function calls: {e}")
        
        return calls
    
    def find_method_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Find method calls using regex patterns.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of dictionaries containing call information
        """
        calls = []
        
        try:
            # Pattern for method calls: receiver.method(args)
            method_pattern = self._get_pattern(
                'method_calls',
                r'(\w+)\.(\w+)(?:::<[^>]*>)?\s*(\([^)]*\))'
            )
            
            for match in method_pattern.finditer(source_code):
                # Skip if inside a string or comment
                if self._is_in_string_or_comment(source_code, match.start()):
                    continue
                
                receiver = match.group(1)
                method_name = match.group(2)
                args = match.group(3)
                
                call_data = {
                    'name': method_name,
                    'type': 'method',
                    'start': match.start(),
                    'end': match.end(),
                    'match': match.group(0).strip(),
                    'pattern': 'method_call',
                    'receiver': receiver,
                    'arguments': self._parse_arguments(args),
                    'generic_params': [],
                }
                
                calls.append(call_data)
                
        except Exception as e:
            logger.error(f"Error finding method calls: {e}")
        
        return calls
    
    def find_macro_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Find macro invocations using regex patterns.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of dictionaries containing call information
        """
        calls = []
        
        try:
            # Pattern for macro calls: macro_name!(args) or macro_name![args] or macro_name!{args}
            macro_pattern = self._get_pattern(
                'macro_calls',
                r'(\w+)!([\(\[\{])([^}\]\)]*)[\)\]\}]'
            )
            
            for match in macro_pattern.finditer(source_code):
                # Skip if inside a string or comment
                if self._is_in_string_or_comment(source_code, match.start()):
                    continue
                
                macro_name = match.group(1)
                delim = match.group(2)
                content = match.group(3)
                
                call_data = {
                    'name': macro_name,
                    'type': 'macro',
                    'start': match.start(),
                    'end': match.end(),
                    'match': match.group(0).strip(),
                    'pattern': 'macro_call',
                    'content': content.strip(),
                    'delimiter': delim,
                    'in_macro': True,
                }
                
                calls.append(call_data)
                
        except Exception as e:
            logger.error(f"Error finding macro calls: {e}")
        
        return calls
    
    def find_associated_function_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Find associated function calls (Type::function).
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of dictionaries containing call information
        """
        calls = []
        
        try:
            # Pattern for associated function calls: Type::function(args) or Type::<T>::function(args)
            # More specific pattern that handles turbofish syntax in type specification
            associated_pattern = self._get_pattern(
                'associated_calls',
                r'(\w+(?:::\w+)*?)(?:::<[^>]*>)?::(\w+)(?:::<[^>]*>)?\s*(\([^)]*\))'
            )
            
            for match in associated_pattern.finditer(source_code):
                # Skip if inside a string or comment
                if self._is_in_string_or_comment(source_code, match.start()):
                    continue
                
                type_path = match.group(1)
                function_name = match.group(2)
                args = match.group(3)
                
                call_data = {
                    'name': function_name,
                    'type': 'associated_function',
                    'start': match.start(),
                    'end': match.end(),
                    'match': match.group(0).strip(),
                    'pattern': 'associated_function_call',
                    'type_path': type_path,
                    'arguments': self._parse_arguments(args),
                    'generic_params': [],
                }
                
                calls.append(call_data)
                
        except Exception as e:
            logger.error(f"Error finding associated function calls: {e}")
        
        return calls
    
    def find_closure_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Find closure calls and invocations.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of dictionaries containing call information
        """
        calls = []
        
        try:
            # Pattern for closures: |params| body
            closure_pattern = self._get_pattern(
                'closure_calls',
                r'\|[^|]*\|\s*([^,\)\]\};]+)'
            )
            
            for match in closure_pattern.finditer(source_code):
                # Skip if inside a string or comment
                if self._is_in_string_or_comment(source_code, match.start()):
                    continue
                
                # Extract function calls within closure body
                body = match.group(1)
                if body and body.strip():
                    # Look for function calls within the closure body
                    # Use a simple function call pattern to avoid recursion
                    body_calls_pattern = re.compile(r'(\w+)\s*(\([^)]*\))')
                    for body_match in body_calls_pattern.finditer(body):
                        # Calculate absolute position in source
                        body_start = match.start(1)
                        call_start = body_start + body_match.start()
                        call_end = body_start + body_match.end()
                        
                        call_data = {
                            'name': body_match.group(1),
                            'type': 'function',
                            'start': call_start,
                            'end': call_end,
                            'match': body_match.group(0),
                            'pattern': 'closure_function_call',
                            'arguments': self._parse_arguments(body_match.group(2)),
                            'in_closure': True,
                        }
                        
                        calls.append(call_data)
                
        except Exception as e:
            logger.error(f"Error finding closure calls: {e}")
        
        return calls
    
    def find_chained_method_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Find chained method calls.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of dictionaries containing call information
        """
        calls = []
        
        try:
            # Pattern for individual method calls in a chain: .method(args)
            chain_pattern = self._get_pattern(
                'chained_calls',
                r'\.(\w+)(?:::<[^>]*>)?\s*(\([^)]*\))'
            )
            
            for match in chain_pattern.finditer(source_code):
                # Skip if inside a string or comment
                if self._is_in_string_or_comment(source_code, match.start()):
                    continue
                
                method_name = match.group(1)
                args = match.group(2)
                
                call_data = {
                    'name': method_name,
                    'type': 'method',
                    'start': match.start(),
                    'end': match.end(),
                    'match': match.group(0).strip(),
                    'pattern': 'chained_method_call',
                    'arguments': self._parse_arguments(args),
                    'is_chained': True,
                }
                
                calls.append(call_data)
                    
        except Exception as e:
            logger.error(f"Error finding chained method calls: {e}")
        
        return calls
    
    def find_trait_method_calls(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Find trait method calls.
        
        Args:
            source_code: Rust source code to analyze
            
        Returns:
            List of dictionaries containing call information
        """
        calls = []
        
        try:
            # Pattern for trait method calls: <Type as Trait>::method(args)
            trait_pattern = self._get_pattern(
                'trait_calls',
                r'<(\w+)\s+as\s+(\w+)>::(\w+)\s*(\([^)]*\))'
            )
            
            for match in trait_pattern.finditer(source_code):
                # Skip if inside a string or comment
                if self._is_in_string_or_comment(source_code, match.start()):
                    continue
                
                type_name = match.group(1)
                trait_name = match.group(2)
                method_name = match.group(3)
                args = match.group(4)
                
                call_data = {
                    'name': method_name,
                    'type': 'trait_method',
                    'start': match.start(),
                    'end': match.end(),
                    'match': match.group(0).strip(),
                    'pattern': 'trait_method_call',
                    'trait_name': trait_name,
                    'type_name': type_name,
                    'arguments': self._parse_arguments(args),
                }
                
                calls.append(call_data)
                
        except Exception as e:
            logger.error(f"Error finding trait method calls: {e}")
        
        return calls
    
    def _is_function_definition(self, source_code: str, position: int) -> bool:
        """Check if position is within a function definition."""
        try:
            # Look back to see if this is in a function definition line
            # Find the start of the current line
            line_start = source_code.rfind('\n', 0, position)
            if line_start == -1:
                line_start = 0
            else:
                line_start += 1
            
            # Get the current line up to the position
            line_end = source_code.find('\n', position)
            if line_end == -1:
                line_end = len(source_code)
            
            current_line = source_code[line_start:line_end]
            
            # Check if 'fn ' appears in this line before or at the position
            fn_match = re.search(r'\bfn\s+\w+', current_line)
            if fn_match:
                fn_pos = line_start + fn_match.start()
                # If the fn keyword comes before or at our position, this is likely a function definition
                if fn_pos <= position:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _is_in_string_or_comment(self, source_code: str, position: int) -> bool:
        """Check if position is inside a string literal or comment."""
        try:
            # Simple check: look backwards to see if we're in a string or comment
            before = source_code[:position]
            
            # Count unescaped quotes
            double_quotes = 0
            single_quotes = 0
            i = 0
            while i < len(before):
                if before[i] == '\\':
                    i += 2  # Skip escaped character
                    continue
                elif before[i] == '"':
                    double_quotes += 1
                elif before[i] == "'":
                    single_quotes += 1
                i += 1
            
            # If odd number of quotes, we're inside a string
            if double_quotes % 2 == 1 or single_quotes % 2 == 1:
                return True
            
            # Check for line comments
            line_start = before.rfind('\n') + 1
            line_before_pos = before[line_start:]
            if '//' in line_before_pos:
                comment_pos = line_before_pos.find('//')
                if comment_pos < len(line_before_pos):
                    return True
            
            # Check for block comments (simplified)
            if '/*' in before and '*/' not in before[before.rfind('/*'):]:
                return True
            
            return False
            
        except Exception:
            return False
    
    def _delimiters_match(self, open_delim: str, close_delim: str) -> bool:
        """Check if opening and closing delimiters match."""
        pairs = {'(': ')', '[': ']', '{': '}'}
        return pairs.get(open_delim) == close_delim
    
    def _parse_arguments(self, args_str: str) -> List[str]:
        """Parse argument string into list of arguments."""
        try:
            if not args_str or args_str == '()':
                return []
            
            # Remove parentheses
            args_str = args_str.strip('()')
            if not args_str:
                return []
            
            # Simple argument splitting (doesn't handle nested parentheses perfectly)
            arguments = []
            current_arg = ""
            paren_depth = 0
            bracket_depth = 0
            brace_depth = 0
            in_string = False
            escape_next = False
            
            for char in args_str:
                if escape_next:
                    current_arg += char
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    current_arg += char
                    continue
                
                if char == '"' and not in_string:
                    in_string = True
                elif char == '"' and in_string:
                    in_string = False
                elif not in_string:
                    if char == '(':
                        paren_depth += 1
                    elif char == ')':
                        paren_depth -= 1
                    elif char == '[':
                        bracket_depth += 1
                    elif char == ']':
                        bracket_depth -= 1
                    elif char == '{':
                        brace_depth += 1
                    elif char == '}':
                        brace_depth -= 1
                    elif char == ',' and paren_depth == 0 and bracket_depth == 0 and brace_depth == 0:
                        arguments.append(current_arg.strip())
                        current_arg = ""
                        continue
                
                current_arg += char
            
            if current_arg.strip():
                arguments.append(current_arg.strip())
            
            return arguments
            
        except Exception:
            return []
    
    def _parse_generics(self, generics_str: str) -> List[str]:
        """Parse generic parameters string into list."""
        try:
            if not generics_str:
                return []
            
            # Remove :: and outer < >
            generics_str = generics_str.strip()
            if generics_str.startswith('::'):
                generics_str = generics_str[2:]
            if generics_str.startswith('<') and generics_str.endswith('>'):
                generics_str = generics_str[1:-1]
            
            if not generics_str:
                return []
            
            # Simple splitting by comma (doesn't handle complex nested generics perfectly)
            generics = []
            current = ""
            bracket_depth = 0
            
            for char in generics_str:
                if char == '<':
                    bracket_depth += 1
                elif char == '>':
                    bracket_depth -= 1
                elif char == ',' and bracket_depth == 0:
                    if current.strip():
                        generics.append(current.strip())
                    current = ""
                    continue
                
                current += char
            
            if current.strip():
                generics.append(current.strip())
            
            return generics
            
        except Exception:
            return []