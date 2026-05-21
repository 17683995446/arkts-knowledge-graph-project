#!/usr/bin/env python3
"""
创建终极混乱测试场景 - 慢工出细活
包含各种极端混乱情况
"""
import os
import random
import string

def create_ultimate_chaos_project():
    project_dir = "ultimate_chaos_project"
    os.makedirs(project_dir, exist_ok=True)
    
    print("🔥 创建终极混乱测试项目...")
    
    # 创建目录结构
    dirs = [
        "src/core",
        "src/utils",
        "src/components",
        "src/services",
        "src/tests",
        "src/api",
        "src/models",
        "src/views",
        "src/legacy",
        "src/experimental"
    ]
    
    for d in dirs:
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)
    
    total_files = 0
    total_lines = 0
    
    # 1. 创建大量核心文件
    print("📝 生成核心模块...")
    for i in range(100):
        filename = os.path.join(project_dir, "src/core", f"core_{i:03d}.ets")
        content = generate_chaos_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 2. 创建工具类
    print("🔧 生成工具类...")
    for i in range(80):
        filename = os.path.join(project_dir, "src/utils", f"util_{i:03d}.ets")
        content = generate_util_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 3. 创建组件
    print("🎨 生成组件...")
    for i in range(70):
        filename = os.path.join(project_dir, "src/components", f"component_{i:03d}.ets")
        content = generate_component_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 4. 创建服务
    print("🚀 生成服务...")
    for i in range(60):
        filename = os.path.join(project_dir, "src/services", f"service_{i:03d}.ets")
        content = generate_service_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 5. 创建测试文件
    print("🧪 生成测试...")
    for i in range(40):
        filename = os.path.join(project_dir, "src/tests", f"test_{i:03d}.ets")
        content = generate_test_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 6. 创建API相关
    print("🌐 生成API...")
    for i in range(50):
        filename = os.path.join(project_dir, "src/api", f"api_{i:03d}.ets")
        content = generate_api_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 7. 创建模型
    print("📦 生成模型...")
    for i in range(40):
        filename = os.path.join(project_dir, "src/models", f"model_{i:03d}.ets")
        content = generate_model_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 8. 创建视图
    print("📺 生成视图...")
    for i in range(30):
        filename = os.path.join(project_dir, "src/views", f"view_{i:03d}.ets")
        content = generate_view_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 9. 创建遗留代码（最混乱）
    print("📜 生成遗留代码...")
    for i in range(20):
        filename = os.path.join(project_dir, "src/legacy", f"legacy_{i:03d}.ets")
        content = generate_legacy_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    # 10. 创建实验代码（异常格式）
    print("🧪 生成实验代码...")
    for i in range(20):
        filename = os.path.join(project_dir, "src/experimental", f"exp_{i:03d}.ets")
        content = generate_experimental_content(i)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        total_files += 1
        total_lines += content.count('\n')
    
    print(f"\n✅ 终极混乱测试项目创建完成！")
    print(f"📁 文件总数: {total_files}")
    print(f"📝 代码行数: {total_lines:,}")
    
    return project_dir

def generate_chaos_content(i):
    """生成混乱的核心代码"""
    class_name = f"ChaosClass{i}"
    
    methods = []
    for m in range(random.randint(5, 20)):
        method_name = f"chaosMethod{m}_{i}"
        body_lines = []
        for l in range(random.randint(5, 30)):
            stmt = random.choice([
                "console.log('chaos');",
                "let x = Math.random();",
                "if (x > 0.5) { x = x / 2; }",
                "for (let j = 0; j < 10; j++) { x += j; }",
                "this.someOtherMethod();"
            ])
            body_lines.append(stmt)
        method = f"""    {method_name}() {{
        {"\n        ".join(body_lines)}
    }}"""
        methods.append(method)
    
    return f"""// 混乱核心模块 {i}
// 包含各种格式问题
export class {class_name} {{
{chr(10).join(methods)}
}}

"""

def generate_util_content(i):
    """生成工具类代码"""
    class_name = f"UtilClass{i}"
    
    methods = []
    for m in range(random.randint(8, 30)):
        method_name = f"utilFunc{m}_{i}"
        params = random.choice(["", "x", "x, y", "x, y, z"])
        
        method = f"""    static {method_name}({params}) {{
        return Math.random() * 100;
    }}"""
        methods.append(method)
    
    return f"""// 工具类 {i}
export class {class_name} {{
{chr(10).join(methods)}
}}

"""

def generate_component_content(i):
    """生成组件代码"""
    component_name = f"ChaosComponent{i}"
    
    return f"""@Entry
@Component
struct {component_name} {{
    @State count: number = 0;
    
    increment() {{
        this.count++;
        console.log('count', this.count);
    }}
    
    build() {{
        Column() {{
            Text('Component {i}')
                .onClick(() => this.increment())
        }}
    }}
}}

"""

def generate_service_content(i):
    """生成服务代码"""
    service_name = f"Service{i}"
    
    methods = []
    for m in range(random.randint(3, 15)):
        method_name = f"serviceMethod{m}"
        
        method = f"""    async {method_name}() {{
        await new Promise(r => setTimeout(r, 100));
        return {{ success: true }};
    }}"""
        methods.append(method)
    
    return f"""// 服务 {i}
export class {service_name} {{
{chr(10).join(methods)}
}}

"""

def generate_test_content(i):
    """生成测试代码"""
    test_suite = f"TestSuite{i}"
    
    tests = []
    for t in range(random.randint(2, 10)):
        test_name = f"test{random.randint(100, 999)}"
        tests.append(f"""    {test_name}() {{
        console.log('Testing {test_name}...');
    }}""")
    
    return f"""// 测试模块 {i}
@Component
struct {test_suite} {{
{chr(10).join(tests)}
}}

"""

def generate_api_content(i):
    """生成API代码"""
    class_name = f"API{i}"
    
    methods = []
    for m in range(random.randint(5, 20)):
        method_name = f"fetchData{m}"
        methods.append(f"""    {method_name}() {{
        return {{ data: 'test' }};
    }}""")
    
    return f"""// API {i}
export class {class_name} {{
{chr(10).join(methods)}
}}

"""

def generate_model_content(i):
    """生成模型代码"""
    model_name = f"Model{i}"
    
    fields = []
    for f in range(random.randint(3, 10)):
        field_name = f"field{random.randint(1, 100)}"
        field_type = random.choice(["string", "number", "boolean", "any"])
        fields.append(f"    {field_name}: {field_type};")
    
    return f"""// 模型 {i}
interface {model_name} {{
{chr(10).join(fields)}
}}

"""

def generate_view_content(i):
    """生成视图代码"""
    view_name = f"View{i}"
    
    return f"""@Component
struct {view_name} {{
    build() {{
        Column() {{
            Text('View {i}')
        }}
    }}
}}

"""

def generate_legacy_content(i):
    """生成遗留代码（最混乱）"""
    legacy_class = f"Legacy{i}"
    
    return f"""// 遗留代码 - 混乱格式 {i}
// 包含各种奇怪的格式
export class {legacy_class} {{
    method1() {{
        // 混乱的代码
        if (true) {{
            console.log('legacy');
        }}
    }}
    
    // 更多方法...
    method2() {{
        for (let i = 0; i < 100; i++) {{
            console.log(i);
        }}
    }}
}}

// 混乱的函数
function doSomething(x, y, z) {{
    return x + y + z;
}}

"""

def generate_experimental_content(i):
    """生成实验代码（异常格式）"""
    
    weird_code = random.choice([
        f"""// 实验代码 {i}
interface Test{{
    x: string;
    y: number
}}
""",
        f"""// 实验代码 {i}
export class Exp{{
    do(x){{
        return x
    }}
}}
""",
        f"""// 实验代码 {i}
let a = 1;
let b = 2;
let c = a + b;
"""
    ])
    
    return weird_code

if __name__ == "__main__":
    create_ultimate_chaos_project()
