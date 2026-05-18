
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
            r'(?:(@[a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*)?'
            r'(?:(async)\s+)?'
            r'(?:(public|private|protected)\s+)?'
            r'(?:(static)\s+)?'
            r'([a-zA-Z_]\w*)'
            r'\s*'
            r'\(([^)]*)\)',
            re.MULTILINE
        )
        
        # Struct/class pattern
        self.struct_pattern = re.compile(
            r'(?:@([a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*\n\s*)*'
            r'(?:export\s+)?'
            r'(?:(abstract)\s+)?'
            r'(class|struct)\s+'
            r'([a-zA-Z_]\w*)',
            re.MULTILINE
        )
        
        # Function pattern
        self.function_pattern = re.compile(
            r'(?:export\s+)?'
            r'function\s+'
            r'([a-zA-Z_]\w*)'
            r'\s*\(([^)]*)\)',
            re.MULTILINE
        )
        
        # Call pattern
        self.call_pattern = re.compile(r'\b([a-zA-Z_]\w*)\s*\(', re.MULTILINE)
        
        # Pattern to skip
        self.keywords = {
            'if', 'for', 'while', 'do', 'switch', 'catch', 'try',
            'return', 'let', 'const', 'var', 'typeof', 'instanceof',
            'new', 'throw', 'delete', 'void', 'await', 'yield',
            'async', 'function', 'import', 'export', 'from',
            'as', 'default', 'extends', 'implements', 'interface',
            'type', 'enum', 'namespace', 'module', 'declare'
        }
    
    def _strip_comments(self, content: str) -> str:
        """Strip all comments from content (line comments and block comments)."""
        # Pattern for block comments
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        # Pattern for line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        return content
    
    def parse_file(self, content: str, file_path: str) -> List[ParsedClass]:
        """Parse a file and extract all entities and relationships."""
        entities = []
        lines = content.split('\n')
        
        # Strip comments to avoid parsing them
        clean_content = self._strip_comments(content)
        
        # Find all classes and structs
        struct_matches = self._find_structs(clean_content, content)
        for match_info in struct_matches:
            parsed_class = self._parse_struct(content, match_info, lines)
            entities.append(parsed_class)
        
        return entities
    
    def extract_standalone_functions(self, content: str) -> List[ParsedMethod]:
        """Extract standalone functions (not in classes)."""
        functions = []
        lines = content.split('\n')
        
        # Strip comments first
        clean_content = self._strip_comments(content)
        
        for match in self.function_pattern.finditer(clean_content):
            name = match.group(1)
            params = match.group(2) or ''
            
            # Validate - skip if it looks like a keyword
            if name in self.keywords:
                continue
                
            # Find original position in full content to get proper line numbers
            original_pos = self._find_original_match(content, clean_content, match.start(), match.end())
            if original_pos is None:
                continue
                
            start, end = original_pos
            start_line = content[:start].count('\n') + 1
            
            # Find the end of the function
            func_body_start = content.find('{', end)
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
            func_body = self._strip_comments(content[func_body_start+1:end_pos])
            calls = list(set(self.call_pattern.findall(func_body)))
            # Filter out library functions
            calls = [c for c in calls if c not in self.keywords]
            
            functions.append(ParsedMethod(
                name=name,
                params=params,
                return_type='',
                start_line=start_line,
                end_line=end_line,
                calls=calls
            ))
        
        return functions
    
    def _find_original_match(self, full_content: str, clean_content: str,
                           clean_start: int, clean_end: int) -> Optional[Tuple[int, int]]:
        """Find original position in unstripped content corresponding to clean content position."""
        # Find the substring in the original content
        target_sub = clean_content[clean_start:clean_end]
        original_pos = full_content.find(target_sub)
        if original_pos != -1:
            return (original_pos, original_pos + len(target_sub))
        return None
    
    def _find_structs(self, clean_content: str, full_content: str) -> List[Tuple]:
        """Find all struct/class definitions in content."""
        results = []
        pos = 0
        
        while pos < len(clean_content):
            match = self.struct_pattern.search(clean_content, pos)
            if not match:
                break
                
            decorator_part = match.group(1)
            abstract = match.group(2)
            struct_type = match.group(3)
            name = match.group(4)
            
            # Find original position
            original_match = self._find_original_match(full_content, clean_content,
                                                       match.start(), match.end())
            if original_match is None:
                pos = match.end()
                continue
                
            original_start, original_end = original_match
            
            # Find all decorators before this struct
            decorators = []
            before = full_content[:original_start]
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
            
            start_line = full_content[:original_start].count('\n') + 1
            
            # Find the closing }
            brace_pos = full_content.find('{', original_end)
            if brace_pos == -1:
                pos = match.end()
                continue
                
            brace_count = 1
            end_brace_pos = brace_pos
            for i in range(brace_pos + 1, len(full_content)):
                if full_content[i] == '{':
                    brace_count += 1
                elif full_content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_brace_pos = i
                        break
            
            end_line = full_content[:end_brace_pos].count('\n') + 1
            
            results.append((name, start_line, end_line, flags, decorators, brace_pos, end_brace_pos, struct_type))
            pos = match.end() + 1
        
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
        
        # Extract body content and strip comments
        body = content[body_start + 1:body_end]
        clean_body = self._strip_comments(body)
        
        # Find methods using our parser
        methods = self._extract_methods_from_body(clean_body, body, start_line, body_start)
        parsed_class.methods = methods
        
        return parsed_class
    
    def _extract_methods_from_body(self, clean_body: str, full_body: str,
                                  base_line: int, body_start: int) -> List[ParsedMethod]:
        """Extract methods from a class/struct body."""
        methods = []
        
        # Look for methods using pattern matching
        pos = 0
        while pos < len(clean_body):
            match = self.method_pattern.search(clean_body, pos)
            if not match:
                break
                
            decorator = match.group(1)
            async_flag = match.group(2)
            visibility = match.group(3) or "public"
            static_flag = match.group(4)
            name = match.group(5)
            params = match.group(6) or ''
            
            # Skip keywords
            if name in self.keywords:
                pos = match.end()
                continue
                
            # Find original position
            original_match = self._find_original_match(full_body, clean_body,
                                                       match.start(), match.end())
            if original_match is None:
                pos = match.end()
                continue
                
            orig_start, orig_end = original_match
            
            # Find the opening brace to extract method body
            brace_pos = full_body.find('{', orig_end)
            if brace_pos == -1:
                pos = match.end()
                continue
                
            # Count braces to find the end
            brace_count = 1
            end_brace_pos = brace_pos
            for i in range(brace_pos + 1, len(full_body)):
                if full_body[i] == '{':
                    brace_count += 1
                elif full_body[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_brace_pos = i
                        break
            
            # Calculate line numbers
            method_start_line = base_line + full_body[:orig_start].count('\n')
            method_end_line = base_line + full_body[:end_brace_pos].count('\n')
            
            # Extract calls from method body
            method_body = self._strip_comments(full_body[brace_pos + 1:end_brace_pos])
            calls = list(set(self.call_pattern.findall(method_body)))
            # Filter out library keywords
            calls = [c for c in calls if c not in self.keywords]
            
            method = ParsedMethod(
                name=name,
                params=params,
                return_type='',
                start_line=method_start_line,
                end_line=method_end_line,
                calls=calls,
                is_async=async_flag is not None,
                is_static=static_flag is not None,
                visibility=visibility,
                decorators=[decorator] if decorator else []
            )
            
            methods.append(method)
            pos = match.end() + 1
        
        return methods

