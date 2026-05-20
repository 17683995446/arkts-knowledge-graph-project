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
        # 更严格的方法正则表达式
        self.method_pattern = re.compile(
            r'^\s*(?:(?:@[a-zA-Z_]\w*\s*(?:\([^)]*\))?\s*)*)\s*'
            r'(?:(async)\s+)?'
            r'(?:(public|private|protected)\s+)?'
            r'(?:(static)\s+)?'
            r'([a-zA-Z_]\w+)\s*'
            r'\(([^)]*)\)',
            re.MULTILINE
        )
        
        # 类/结构模式
        self.struct_pattern = re.compile(
            r'(?:@([a-zA-Z_]\w*)\s*(?:\([^)]*\))?\s*\n\s*)*'
            r'(?:export\s+)?'
            r'(?:(abstract)\s+)?'
            r'(class|struct)\s+'
            r'([a-zA-Z_]\w*)',
            re.MULTILINE
        )
        
        # 函数模式
        self.function_pattern = re.compile(
            r'(?:export\s+)?'
            r'function\s+'
            r'([a-zA-Z_]\w*)'
            r'\s*\(([^)]*)\)',
            re.MULTILINE
        )
        
        self.call_pattern = re.compile(r'\b([a-zA-Z_]\w*)\s*\(', re.MULTILINE)
        
        # 跳过的关键字和通用方法/组件
        self.SKIP_METHOD_NAMES = {
            # 关键字
            'if', 'for', 'while', 'do', 'switch', 'catch', 'try',
            'return', 'let', 'const', 'var', 'typeof', 'instanceof',
            'new', 'throw', 'delete', 'void', 'await', 'yield',
            'async', 'function', 'import', 'export', 'from',
            'as', 'default', 'extends', 'implements', 'interface',
            'type', 'enum', 'namespace', 'module', 'declare',
            'constructor', 'get', 'set',
            
            # 通用字符串/数组方法
            'toString', 'toUpperCase', 'toLowerCase', 'trim', 'trimStart',
            'trimEnd', 'substring', 'substr', 'slice', 'split', 'join',
            'indexOf', 'lastIndexOf', 'startsWith', 'endsWith', 'includes',
            'replace', 'replaceAll', 'match', 'search', 'padStart', 'padEnd',
            'concat', 'push', 'pop', 'shift', 'unshift', 'splice', 'sort',
            'reverse', 'map', 'filter', 'reduce', 'reduceRight', 'forEach',
            'find', 'findIndex', 'some', 'every', 'flat', 'flatMap',
            'keys', 'values', 'entries', 'has', 'get', 'set', 'clear', 'delete',
            'size', 'length',
            
            # ArkTS UI 组件
            'Text', 'Button', 'Column', 'Row', 'Stack', 'List', 'ListItem',
            'ForEach', 'If', 'Else', 'Image', 'TextInput', 'Checkbox', 'Radio',
            'Slider', 'Progress', 'Scroll', 'Swiper', 'Grid', 'GridItem',
            'Tabs', 'TabContent', 'Badge', 'Divider', 'Span', 'Blank', 'Flex',
            'RelativeContainer', 'GridRow', 'GridCol', 'Circle', 'Ellipse',
            'Polyline', 'Polygon', 'Path', 'Shape', 'Rect',
            
            # UI 事件和属性
            'onClick', 'onChange', 'onSubmit', 'onFocus', 'onBlur',
            'onAppear', 'onDisappear', 'width', 'height', 'size',
            'padding', 'margin', 'fontSize', 'fontColor', 'backgroundColor',
            
            # Promise/async 相关
            'then', 'catch', 'finally', 'resolve', 'reject', 'all', 'race', 'any',
            'Promise', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
            
            # 控制台
            'console', 'log', 'error', 'warn', 'info', 'debug', 'trace',
            
            # 其他常见的库方法
            'Date', 'Math', 'JSON', 'parse', 'stringify', 'random', 'floor',
            'ceil', 'round', 'abs', 'max', 'min', 'sqrt', 'pow', 'exp', 'log',
            
            # 类型转换
            'Number', 'String', 'Boolean', 'Array', 'Object'
        }
        
        self.known_class_names = set()
    
    def _strip_comments(self, content: str) -> str:
        content = re.sub(r'/\*[\s\S]*?\*/', '', content)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        return content
    
    def parse_file(self, content: str, file_path: str) -> List[ParsedClass]:
        entities = []
        self.known_class_names.clear()
        
        clean_content = self._strip_comments(content)
        
        # 先收集类名
        struct_matches = self._find_structs(clean_content, content)
        
        for match_info in struct_matches:
            self.known_class_names.add(match_info[0])
        
        # 然后解析
        for match_info in struct_matches:
            parsed_class = self._parse_struct(content, match_info)
            entities.append(parsed_class)
        
        return entities
    
    def extract_standalone_functions(self, content: str) -> List[ParsedMethod]:
        functions = []
        lines = content.split('\n')
        clean_content = self._strip_comments(content)
        
        for match in self.function_pattern.finditer(clean_content):
            name = match.group(1)
            params = match.group(2) or ''
            
            if name in self.SKIP_METHOD_NAMES or name in self.known_class_names:
                continue
                
            original_pos = self._find_original_match(content, clean_content, match.start(), match.end())
            if original_pos is None:
                continue
                
            start, end = original_pos
            start_line = content[:start].count('\n') + 1
            
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
            
            func_body = self._strip_comments(content[func_body_start+1:end_pos])
            calls = list(set(self.call_pattern.findall(func_body)))
            calls = [c for c in calls if c not in self.SKIP_METHOD_NAMES and c not in self.known_class_names]
            
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
        target_sub = clean_content[clean_start:clean_end]
        original_pos = full_content.find(target_sub)
        if original_pos != -1:
            return (original_pos, original_pos + len(target_sub))
        return None
    
    def _find_structs(self, clean_content: str, full_content: str) -> List[Tuple]:
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
            
            original_match = self._find_original_match(full_content, clean_content,
                                                       match.start(), match.end())
            if original_match is None:
                pos = match.end()
                continue
                
            original_start, original_end = original_match
            
            decorators = []
            before = full_content[:original_start]
            for decorator_match in re.finditer(r'@([a-zA-Z_]\w*)\s*(?:\([^)]*\))?', before):
                decorator_name = decorator_match.group(1)
                decorators.append(decorator_name)
            
            if decorator_part:
                decorators.append(decorator_part)
            
            flags = 0
            for d in decorators:
                if d == 'Component':
                    flags |= CLASS_FLAG_COMPONENT
                elif d == 'Entry':
                    flags |= CLASS_FLAG_ENTRY
                elif d == 'State':
                    flags |= CLASS_FLAG_STATE
            
            start_line = full_content[:original_start].count('\n') + 1
            
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
    
    def _parse_struct(self, content: str, match_info: Tuple) -> ParsedClass:
        name, start_line, end_line, flags, decorators, brace_pos, end_brace_pos, _ = match_info
        
        parsed_class = ParsedClass(
            name=name,
            start_line=start_line,
            end_line=end_line,
            flags=flags,
            decorators=decorators
        )
        
        body = content[brace_pos + 1:end_brace_pos]
        clean_body = self._strip_comments(body)
        
        methods = self._extract_methods_from_body(clean_body, body, start_line, brace_pos)
        parsed_class.methods = methods
        
        return parsed_class
    
    def _extract_methods_from_body(self, clean_body: str, full_body: str,
                                  base_line: int, body_start: int) -> List[ParsedMethod]:
        methods = []
        
        pos = 0
        while pos < len(clean_body):
            match = self.method_pattern.search(clean_body, pos)
            if not match:
                break
                
            async_flag = match.group(1)
            visibility = match.group(2) or "public"
            static_flag = match.group(3)
            name = match.group(4)
            params = match.group(5) or ''
            
            # 关键过滤
            if name in self.SKIP_METHOD_NAMES or name in self.known_class_names:
                pos = match.end()
                continue
            
            original_match = self._find_original_match(full_body, clean_body,
                                                       match.start(), match.end())
            if original_match is None:
                pos = match.end()
                continue
                
            orig_start, orig_end = original_match
            
            # 关键验证：确保这是一个方法定义，而不是函数调用或其他
            start_line_index = full_body[:orig_start].rfind('\n') + 1
            line_before = full_body[start_line_index:orig_start].strip()
            
            # 如果有'='或':'在前面，很可能是变量声明或类型声明
            if '=' in line_before or ':' in line_before:
                pos = match.end()
                continue
                
            brace_pos = full_body.find('{', orig_end)
            if brace_pos == -1:
                pos = match.end()
                continue
                
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
            
            method_start_line = base_line + full_body[:orig_start].count('\n')
            method_end_line = base_line + full_body[:end_brace_pos].count('\n')
            
            method_body = self._strip_comments(full_body[brace_pos + 1:end_brace_pos])
            calls = list(set(self.call_pattern.findall(method_body)))
            calls = [c for c in calls if c not in self.SKIP_METHOD_NAMES and c not in self.known_class_names]
            
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
                decorators=[]
            )
            
            methods.append(method)
            pos = match.end() + 1
        
        return methods
