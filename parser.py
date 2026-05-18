"""ArkTS/TypeScript parser for extracting code entities and relationships."""
import re
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass, field


@dataclass
class ParsedClass:
    """Represents a parsed class or struct."""
    name: str
    start_line: int
    end_line: int
    flags: int
    methods: List['ParsedMethod'] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)


@dataclass
class ParsedMethod:
    """Represents a parsed method or function."""
    name: str
    start_line: int
    end_line: int
    params: str = ""
    return_type: str = ""
    calls: List[str] = field(default_factory=list)
    is_async: bool = False
    is_static: bool = False
    visibility: str = "public"
    decorators: List[str] = field(default_factory=list)


# Flag constants
CLASS_FLAG_COMPONENT = 1 << 0
CLASS_FLAG_ENTRY = 1 << 1
CLASS_FLAG_STATE = 1 << 2
CLASS_FLAG_PROP = 1 << 3


class ArkTSParser:
    """Parser for ArkTS/TypeScript source files."""
    
    def __init__(self):
        # Method patterns
        self.method_pattern = re.compile(
            r'(?:(@[a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*)?'  # Optional decorator
            r'(?:(async)\s+)?'  # Optional async
            r'(?:(public|private|protected)\s+)?'  # Optional visibility
            r'(?:(static)\s+)?'  # Optional static
            r'([a-zA-Z_]\w*)'  # Method name
            r'\s*'  # Optional whitespace
            r'\(([^)]*)\)'  # Parameters
            r'(?:\s*:\s*([a-zA-Z_][\w<\[\]]*))?'  # Optional return type
            r'\s*',
            re.MULTILINE
        )
        
        # Struct/class pattern
        self.struct_pattern = re.compile(
            r'(?:@([a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*\n\s*)*'  # Decorators
            r'(?:export\s+)?'  # Optional export
            r'(?:(abstract)\s+)?'  # Optional abstract
            r'(class|struct)\s+'  # Class or struct
            r'([a-zA-Z_]\w*)',  # Name
            re.MULTILINE
        )
        
        # Function pattern
        self.function_pattern = re.compile(
            r'(?:export\s+)?'
            r'function\s+'
            r'([a-zA-Z_]\w*)'
            r'\s*\(([^)]*)\)'
            r'(?:\s*:\s*([a-zA-Z_][\w<\[\]]*))?',
            re.MULTILINE
        )
        
        # Call pattern
        self.call_pattern = re.compile(r'\b([a-zA-Z_]\w*)\s*\(', re.MULTILINE)

    def parse_file(self, content: str, file_path: str) -> List[ParsedClass]:
        """Parse a file and extract all entities and relationships."""
        entities = []
        lines = content.split('\n')
        
        # Find all classes and structs
        struct_matches = self._find_structs(content)
        for match_info in struct_matches:
            parsed_class = self._parse_struct(content, match_info, lines)
            entities.append(parsed_class)
        
        return entities

    def extract_standalone_functions(self, content: str) -> List[ParsedMethod]:
        """Extract standalone functions (not in classes)."""
        functions = []
        lines = content.split('\n')
        
        for match in self.function_pattern.finditer(content):
            name = match.group(1)
            params = match.group(2) or ''
            return_type = match.group(3) or ''
            
            start_line = content[:match.start()].count('\n') + 1
            
            # Find the end of the function
            func_body_start = content.find('{', match.end())
            if func_body_start == -1:
                continue
                
            brace_count = 1
            end_pos = func_body_start + 1
            for i in range(func_body_start + 1, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i
                        break
            
            end_line = content[:end_pos].count('\n') + 1
            
            # Extract calls from the function body
            func_body = content[func_body_start+1:end_pos]
            calls = list(set(self.call_pattern.findall(func_body)))
            
            functions.append(ParsedMethod(
                name=name,
                params=params,
                return_type=return_type,
                start_line=start_line,
                end_line=end_line,
                calls=calls
            ))
        
        return functions

    def _find_structs(self, content: str) -> List[Tuple]:
        """Find all struct/class definitions in content."""
        results = []
        pos = 0
        
        while pos < len(content):
            match = self.struct_pattern.search(content, pos)
            if not match:
                break
                
            decorator_part = match.group(1)
            abstract = match.group(2)
            struct_type = match.group(3)
            name = match.group(4)
            
            # Find all decorators before this struct
            decorators = []
            before = content[:match.start()]
            for decorator_match in re.finditer(r'@([a-zA-Z_]\w*)\s*(?:\([^)]*\))?', before):
                decorator_name = decorator_match.group(1)
                decorators.append(decorator_name)
            
            # Also check decorators in the current match
            if decorator_part:
                decorators.append(decorator_part)
            
            # Calculate flags from decorators
            flags = 0
            for d in decorators:
                if d == 'Component':
                    flags |= CLASS_FLAG_COMPONENT
                elif d == 'Entry':
                    flags |= CLASS_FLAG_ENTRY
                elif d == 'State':
                    flags |= CLASS_FLAG_STATE
            
            start_line = content[:match.start()].count('\n') + 1
            
            # Find the closing }
            brace_pos = content.find('{', match.end())
            if brace_pos == -1:
                pos = match.end()
                continue
                
            brace_count = 1
            end_brace_pos = brace_pos
            for i in range(brace_pos + 1, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_brace_pos = i
                        break
            
            end_line = content[:end_brace_pos].count('\n') + 1
            
            results.append((name, start_line, end_line, flags, decorators, brace_pos, end_brace_pos, struct_type))
            pos = end_brace_pos + 1
        
        return results

    def _parse_struct(self, content: str, match_info: Tuple, lines: List[str]) -> ParsedClass:
        """Parse a struct/class body and extract methods."""
        name, start_line, end_line, flags, decorators, body_start, body_end, _ = match_info
        
        parsed_class = ParsedClass(
            name=name,
            start_line=start_line,
            end_line=end_line,
            flags=flags,
            decorators=decorators
        )
        
        # Extract body content
        body = content[body_start + 1:body_end]
        
        # Find methods using our parser
        methods = self._extract_methods_from_body(body, start_line, body_start)
        parsed_class.methods = methods
        
        return parsed_class

    def _extract_methods_from_body(self, body: str, base_line: int, body_start: int) -> List[ParsedMethod]:
        """Extract methods from a class/struct body."""
        methods = []
        
        # Look for methods using pattern matching
        pos = 0
        while pos < len(body):
            match = self.method_pattern.search(body, pos)
            if not match:
                break
                
            decorator = match.group(1)
            async_flag = match.group(2)
            visibility = match.group(3) or "public"
            static_flag = match.group(4)
            name = match.group(5)
            params = match.group(6) or ''
            return_type = match.group(7) or ''
            
            # Skip if this looks like a control statement
            if name in ['if', 'for', 'while', 'do', 'switch', 'catch', 'try', 'return', 'let', 'const']:
                pos = match.end()
                continue
                
            # Find the opening brace to extract method body
            brace_pos = body.find('{', match.end())
            if brace_pos == -1:
                pos = match.end()
                continue
                
            # Count braces to find the end
            brace_count = 1
            end_brace_pos = brace_pos
            for i in range(brace_pos + 1, len(body)):
                if body[i] == '{':
                    brace_count += 1
                elif body[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_brace_pos = i
                        break
            
            # Calculate line numbers
            method_start_line = base_line + body[:match.start()].count('\n')
            method_end_line = base_line + body[:end_brace_pos].count('\n')
            
            # Extract calls from method body
            method_body = body[brace_pos + 1:end_brace_pos]
            calls = list(set(self.call_pattern.findall(method_body)))
            
            method = ParsedMethod(
                name=name,
                params=params,
                return_type=return_type,
                start_line=method_start_line,
                end_line=method_end_line,
                calls=calls,
                is_async=async_flag is not None,
                is_static=static_flag is not None,
                visibility=visibility,
                decorators=[decorator] if decorator else []
            )
            
            methods.append(method)
            pos = end_brace_pos + 1
        
        return methods
