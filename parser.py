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
        # Unicode 字符支持
        # 包含：中文、日文、韩文、以及其他Unicode字母
        unicode_letter = (
            r'a-zA-Z_\u4e00-\u9fff'  # 中文
            r'\u3040-\u309f'  # 日文平假名
            r'\u30a0-\u30ff'  # 日文片假名
            r'\uac00-\ud7af'  # 韩文
            r'\u0400-\u04ff'  # 西里尔字母
            r'\u0370-\u03ff'  # 希腊字母
            r'\u0600-\u06ff'  # 阿拉伯字母
            r'\u0590-\u05ff'  # 希伯来字母
        )
        
        # 更严格的方法正则表达式（支持Unicode）
        self.method_pattern = re.compile(
            r'^\s*(?:(?:@[' + unicode_letter + r']\w*\s*(?:\([^)]*\))?\s*)*)\s*'
            r'(?:(async)\s+)?'
            r'(?:(public|private|protected)\s+)?'
            r'(?:(static)\s+)?'
            r'([' + unicode_letter + r']\w*)\s*'
            r'\(([^)]*)\)',
            re.MULTILINE
        )
        
        # 类/结构模式（支持Unicode）
        self.struct_pattern = re.compile(
            r'(?:@([' + unicode_letter + r']\w*)\s*(?:\([^)]*\))?\s*(?:\n\s*@)?)*'
            r'(?:export\s+)?'
            r'(?:(abstract)\s+)?'
            r'(class|struct)\s+'
            r'([' + unicode_letter + r']\w*)',
            re.MULTILINE
        )
        
        # 函数模式（支持Unicode）
        self.function_pattern = re.compile(
            r'(?:export\s+)?'
            r'function\s+'
            r'([' + unicode_letter + r']\w*)'
            r'\s*\(([^)]*)\)',
            re.MULTILINE
        )
        
        self.call_pattern = re.compile(r'\b([' + unicode_letter + r']\w*)\s*\(', re.MULTILINE)
        
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
    
    def _strip_comments_and_map(self, content: str) -> Tuple[str, List[int]]:
        """Strip comments and return clean content + position map.

        Args:
            content: Original content.

        Returns:
            Tuple of (clean_content, position_map), where position_map[i] is
            the index in the original content that corresponds to clean_content[i].
        """
        clean_chars = []
        pos_map = []
        i = 0
        n = len(content)
        
        while i < n:
            if i + 1 < n and content[i] == '/' and content[i+1] == '/':
                # Line comment
                while i < n and content[i] != '\n':
                    i += 1
            elif i + 1 < n and content[i] == '/' and content[i+1] == '*':
                # Block comment
                i += 2
                while i + 1 < n and not (content[i] == '*' and content[i+1] == '/'):
                    i += 1
                i += 2
            elif content[i] in ('"', "'", '`'):
                # String literal
                quote = content[i]
                clean_chars.append(content[i])
                pos_map.append(i)
                i += 1
                while i < n:
                    if content[i] == '\\' and i + 1 < n:
                        clean_chars.append(content[i])
                        pos_map.append(i)
                        clean_chars.append(content[i+1])
                        pos_map.append(i+1)
                        i += 2
                    elif content[i] == quote:
                        break
                    else:
                        clean_chars.append(content[i])
                        pos_map.append(i)
                        i += 1
                if i < n:
                    clean_chars.append(content[i])
                    pos_map.append(i)
                    i += 1
            else:
                clean_chars.append(content[i])
                pos_map.append(i)
                i += 1
        
        return (''.join(clean_chars), pos_map)
    
    def _strip_comments(self, content: str) -> str:
        """Strip comments from content (backward compatible)."""
        clean, _ = self._strip_comments_and_map(content)
        return clean
    
    def parse_file(self, content: str, file_path: str) -> List[ParsedClass]:
        entities = []
        self.known_class_names.clear()
        
        clean_content, pos_map = self._strip_comments_and_map(content)
        
        # 先收集类名
        struct_matches = self._find_structs(clean_content, content, pos_map)
        
        for match_info in struct_matches:
            self.known_class_names.add(match_info[0])
        
        # 然后解析
        for match_info in struct_matches:
            parsed_class = self._parse_struct(content, match_info, pos_map)
            entities.append(parsed_class)
        
        return entities
    
    def extract_standalone_functions(self, content: str) -> List[ParsedMethod]:
        functions = []
        
        clean_content, pos_map = self._strip_comments_and_map(content)
        
        for match in self.function_pattern.finditer(clean_content):
            name = match.group(1)
            params = match.group(2) or ''
            
            if name in self.SKIP_METHOD_NAMES or name in self.known_class_names:
                continue
                
            orig_positions = self._map_positions(match.start(), match.end(), pos_map)
            if orig_positions is None:
                continue
                
            start, end = orig_positions
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
    
    def _map_positions(self, clean_start: int, clean_end: int, 
                      pos_map: List[int]) -> Optional[Tuple[int, int]]:
        """Map clean content positions back to original positions using pos_map."""
        if clean_start < 0 or clean_end > len(pos_map):
            return None
        if clean_start >= clean_end:
            return None
        
        orig_start = pos_map[clean_start]
        orig_end = pos_map[clean_end - 1] + 1
        return (orig_start, orig_end)
    
    def _find_structs(self, clean_content: str, full_content: str, 
                     pos_map: List[int]) -> List[Tuple]:
        results = []
        pos = 0
        
        while pos < len(clean_content):
            match = self.struct_pattern.search(clean_content, pos)
            if not match:
                break
                
            # 正则表达式匹配了从装饰器到 class/struct 的完整范围
            # 我们需要找到 class/struct 关键字的位置
            struct_type = match.group(3)
            name = match.group(4)
            
            # 找到 class/struct 关键字在清理后内容中的位置
            struct_keyword_match = re.search(r'\b(class|struct)\s+', clean_content[match.start():])
            if not struct_keyword_match:
                pos = match.end()
                continue
            
            # class/struct 关键字在匹配区域内的偏移量
            struct_offset_in_match = struct_keyword_match.start()
            clean_struct_pos = match.start() + struct_offset_in_match
            
            # 映射到原始位置
            if clean_struct_pos >= len(pos_map):
                pos = match.end()
                continue
            
            original_struct_pos = pos_map[clean_struct_pos]
            
            # 装饰器在 class/struct 关键字之前
            decorators = []
            
            # 在原始内容中查找装饰器
            before = full_content[:original_struct_pos]
            lines = before.split('\n')
            for line in lines:
                stripped = line.lstrip()
                if stripped.startswith('@'):
                    match_dec = re.match(r'@([a-zA-Z_]\w*)', stripped)
                    if match_dec:
                        decorator_name = match_dec.group(1)
                        decorators.append(decorator_name)
            
            flags = 0
            for d in decorators:
                if d == 'Component':
                    flags |= CLASS_FLAG_COMPONENT
                elif d == 'Entry':
                    flags |= CLASS_FLAG_ENTRY
                elif d == 'State':
                    flags |= CLASS_FLAG_STATE
            
            start_line = full_content[:original_struct_pos].count('\n') + 1
            
            # 找到 class/struct 关键字结束的位置
            clean_struct_end = clean_struct_pos + len(struct_keyword_match.group(0))
            if clean_struct_end > len(pos_map):
                pos = match.end()
                continue
            
            original_struct_end = pos_map[clean_struct_end - 1] + 1
            
            brace_pos = full_content.find('{', original_struct_end)
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
            
            results.append((name, start_line, end_line, flags, decorators, brace_pos, end_brace_pos, struct_type, pos_map))
            pos = match.end() + 1
        
        return results
    
    def _parse_struct(self, content: str, match_info: Tuple, pos_map: List[int]) -> ParsedClass:
        name, start_line, end_line, flags, decorators, brace_pos, end_brace_pos, _, _ = match_info
        
        parsed_class = ParsedClass(
            name=name,
            start_line=start_line,
            end_line=end_line,
            flags=flags,
            decorators=decorators
        )
        
        body = content[brace_pos + 1:end_brace_pos]
        clean_body, body_pos_map = self._strip_comments_and_map(body)
        
        methods = self._extract_methods_from_body(clean_body, body, body_pos_map, start_line, brace_pos)
        parsed_class.methods = methods
        
        return parsed_class
    
    def _extract_methods_from_body(self, clean_body: str, full_body: str,
                                  body_pos_map: List[int],
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
            
            orig_positions = self._map_positions(match.start(), match.end(), body_pos_map)
            if orig_positions is None:
                pos = match.end()
                continue
                
            orig_start, orig_end = orig_positions
            
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
            
            method_body = self._strip_comments(full_body[brace_pos+1:end_brace_pos])
            calls = list(set(self.call_pattern.findall(method_body)))
            calls = [c for c in calls if c not in self.SKIP_METHOD_NAMES and c not in self.known_class_names]
            
            methods.append(ParsedMethod(
                name=name,
                start_line=method_start_line,
                end_line=method_end_line,
                params=params,
                calls=calls,
                is_async=bool(async_flag),
                is_static=bool(static_flag),
                visibility=visibility
            ))
            
            pos = match.end() + 1
        
        return methods
