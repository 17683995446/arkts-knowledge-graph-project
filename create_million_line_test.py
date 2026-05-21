#!/usr/bin/env python3
"""
创建超大规模测试项目 - 百万行级深度压力测试
"""
import os
import random

class MillionLineTestGenerator:
    def __init__(self, base_dir="massive_test_project"):
        self.base_dir = base_dir
        self.file_count = 0
        self.line_count = 0
        
    def generate(self):
        print("🔥 开始生成超大规模测试项目...")
        
        # 创建目录结构
        self._create_dirs()
        
        # 生成核心模块（50个文件，每个约500行）
        print("📦 生成核心模块...")
        for i in range(50):
            self._generate_core_module(i)
            
        # 生成UI组件（30个文件，每个约300行）
        print("🎨 生成UI组件...")
        for i in range(30):
            self._generate_ui_component(i)
            
        # 生成业务逻辑（40个文件，每个约400行）
        print("💼 生成业务逻辑...")
        for i in range(40):
            self._generate_business_logic(i)
            
        # 生成网络层（20个文件，每个约350行）
        print("🌐 生成网络层...")
        for i in range(20):
            self._generate_network_layer(i)
            
        # 生成工具类（25个文件，每个约250行）
        print("🔧 生成工具类...")
        for i in range(25):
            self._generate_utils(i)
            
        # 生成测试文件（15个文件，每个约200行）
        print("🧪 生成测试文件...")
        for i in range(15):
            self._generate_test_file(i)
        
        print(f"\n✅ 生成完成！")
        print(f"   文件数: {self.file_count}")
        print(f"   总行数: {self.line_count}")
        
    def _create_dirs(self):
        dirs = [
            "core",
            "core/entities",
            "core/services", 
            "core/managers",
            "core/handlers",
            "ui/components",
            "ui/pages",
            "ui/widgets",
            "ui/dialogs",
            "business/services",
            "business/workflows",
            "business/validators",
            "business/processors",
            "network/api",
            "network/websocket",
            "network/handlers",
            "utils",
            "utils/converters",
            "utils/formatters",
            "utils/validators",
            "tests/unit",
            "tests/integration",
            "tests/e2e"
        ]
        
        for d in dirs:
            path = os.path.join(self.base_dir, d)
            os.makedirs(path, exist_ok=True)
    
    def _generate_file_header(self, module_name, class_count):
        return f'''/**
 * {module_name}
 * 自动生成的超大规模测试文件
 * 包含 {class_count} 个类和大量方法
 */

'''
    
    def _generate_core_module(self, index):
        filename = f"{self.base_dir}/core/entities/entity_{index:03d}.ets"
        
        classes_html = []
        for c in range(8):
            class_name = f"EntityClass{c}{index}"
            methods_html = []
            
            # 生成方法
            for m in range(20):
                method_name = f"method{m}{c}{index}"
                method_body = self._generate_method_body(15)
                methods_html.append(f'''
    {method_name}() {{
{method_body}
    }}
''')
            
            class_html = f'''
export class {class_name} {{
{''.join(methods_html)}
}}
'''
            classes_html.append(class_html)
        
        content = self._generate_file_header(f"Core Entity Module {index}", 8) + ''.join(classes_html)
        
        with open(filename, 'w') as f:
            f.write(content)
            
        self.file_count += 1
        self.line_count += content.count('\n')
        
    def _generate_ui_component(self, index):
        filename = f"{self.base_dir}/ui/components/component_{index:03d}.ets"
        
        component_name = f"Component{index}"
        
        # 生成大量组件方法
        methods = []
        for m in range(25):
            method_name = f"handle{m}{index}"
            method_body = self._generate_method_body(10)
            methods.append(f'''
    {method_name}() {{
{method_body}
    }}
''')
        
        content = self._generate_file_header(f"UI Component {index}", 1) + f'''
@Component
struct {component_name} {{
{''.join(methods)}

    build() {{
        Column() {{
            Text("Component {index}")
        }}
    }}
}}
'''
        
        with open(filename, 'w') as f:
            f.write(content)
            
        self.file_count += 1
        self.line_count += content.count('\n')
        
    def _generate_business_logic(self, index):
        filename = f"{self.base_dir}/business/services/service_{index:03d}.ets"
        
        classes_html = []
        for c in range(5):
            class_name = f"Service{c}{index}"
            methods_html = []
            
            # 生成方法
            for m in range(30):
                method_name = f"process{m}{c}{index}"
                method_body = self._generate_method_body(12)
                methods_html.append(f'''
    async {method_name}() {{
{method_body}
    }}
''')
            
            class_html = f'''
export class {class_name} {{
{''.join(methods_html)}
}}
'''
            classes_html.append(class_html)
        
        content = self._generate_file_header(f"Business Logic {index}", 5) + ''.join(classes_html)
        
        with open(filename, 'w') as f:
            f.write(content)
            
        self.file_count += 1
        self.line_count += content.count('\n')
        
    def _generate_network_layer(self, index):
        filename = f"{self.base_dir}/network/api/api_{index:03d}.ets"
        
        class_name = f"API{index}"
        
        methods = []
        for m in range(35):
            method_name = f"fetch{m}{index}"
            method_body = self._generate_method_body(8)
            methods.append(f'''
    async {method_name}(param: string): Promise<any> {{
{method_body}
    }}
''')
        
        content = self._generate_file_header(f"Network API {index}", 1) + f'''
export class {class_name} {{
{''.join(methods)}
}}
'''
        
        with open(filename, 'w') as f:
            f.write(content)
            
        self.file_count += 1
        self.line_count += content.count('\n')
        
    def _generate_utils(self, index):
        filename = f"{self.base_dir}/utils/util_{index:03d}.ets"
        
        classes_html = []
        for c in range(4):
            class_name = f"Util{c}{index}"
            methods_html = []
            
            for m in range(20):
                method_name = f"util{m}{c}{index}"
                method_body = self._generate_method_body(6)
                methods_html.append(f'''
    static {method_name}() {{
{method_body}
    }}
''')
            
            class_html = f'''
export class {class_name} {{
{''.join(methods_html)}
}}
'''
            classes_html.append(class_html)
        
        content = self._generate_file_header(f"Utilities {index}", 4) + ''.join(classes_html)
        
        with open(filename, 'w') as f:
            f.write(content)
            
        self.file_count += 1
        self.line_count += content.count('\n')
        
    def _generate_test_file(self, index):
        filename = f"{self.base_dir}/tests/unit/test_{index:03d}.ets"
        
        class_name = f"Test{index}"
        
        methods = []
        for m in range(15):
            method_name = f"test{m}{index}"
            method_body = self._generate_method_body(8)
            methods.append(f'''
    @Test
    {method_name}() {{
{method_body}
    }}
''')
        
        content = self._generate_file_header(f"Test {index}", 1) + f'''
@Component
struct {class_name} {{
{''.join(methods)}
}}
'''
        
        with open(filename, 'w') as f:
            f.write(content)
            
        self.file_count += 1
        self.line_count += content.count('\n')
        
    def _generate_method_body(self, lines):
        """生成方法体"""
        statements = [
            "const x = 10;",
            "const y = 20;",
            "let z = x + y;",
            "console.log('test');",
            "if (z > 10) { z = 10; }",
            "for (let i = 0; i < 10; i++) { z += i; }",
            "return z;",
            "this.processData(z);",
            "await this.fetchData();",
            "const result = await API.call();",
        ]
        
        body_lines = []
        for _ in range(lines):
            body_lines.append("        " + random.choice(statements))
        
        return '\n'.join(body_lines)

if __name__ == "__main__":
    generator = MillionLineTestGenerator()
    generator.generate()
