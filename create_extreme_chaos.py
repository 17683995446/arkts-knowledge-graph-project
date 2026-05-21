#!/usr/bin/env python3
"""
创建极端复杂测试场景 - 第三轮深度测试
包含：混乱嵌套、特殊边界、并发场景、内存压力
"""
import os
import sys
import random
import string


def random_name(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))


def create_extreme_chaos_project():
    """创建极端混乱的测试项目"""
    test_dir = "/workspace/extreme_chaos_project"
    os.makedirs(test_dir, exist_ok=True)
    
    print("创建极端混乱测试项目...")
    
    # 场景1: 超深层嵌套类
    print("\n场景1: 创建超深层嵌套类...")
    for i in range(50):
        filepath = os.path.join(test_dir, f"DeepNested{i}.ets")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 超深层嵌套测试 {i}
class Outer{i} {{
    class Inner1 {{
        class Inner2 {{
            class Inner3 {{
                class Inner4 {{
                    class Inner5 {{
                        method{i}() {{
                            if (true) {{
                                if (true) {{
                                    if (true) {{
                                        if (true) {{
                                            if (true) {{
                                                console.log('deep');
                                            }}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
}}
""")

    # 场景2: 极长方法名和类名
    print("场景2: 创建极长名称...")
    for i in range(20):
        filepath = os.path.join(test_dir, f"LongNames{i}.ets")
        long_class_name = "Class" + "A" * 500
        long_method_name = "method" + "B" * 500
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 极长名称测试 {i}
class {long_class_name} {{
    {long_method_name}() {{
        console.log('long name');
    }}
}}
""")

    # 场景3: 混乱的装饰器组合
    print("场景3: 创建混乱装饰器组合...")
    for i in range(30):
        filepath = os.path.join(test_dir, f"ChaosDecorators{i}.ets")
        decorators = [
            "@Component", "@Entry", "@Preview", "@Observed",
            "@State", "@Prop", "@Link", "@StorageProp",
            "@Provide", "@Consume", "@Builder", "@BuilderParam",
            "@Watch", "@Skip", "@Override", "@Deprecated",
            "@Experimental", "@Since", "@SystemAPI", "@FuzzDoNotTrim"
        ]
        
        # 随机选择5-15个装饰器
        num_decorators = random.randint(5, 15)
        selected_decorators = random.sample(decorators, min(num_decorators, len(decorators)))
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 混乱装饰器测试 {i}
{chr(10).join(selected_decorators)}
struct ChaosComponent{i} {{
    @State message: string = 'test';
    @Prop title: string = 'title';
    
    build() {{
        Column() {{
            Text(this.message);
        }}
    }}
}}
""")

    # 场景4: 复杂的泛型和类型
    print("场景4: 创建复杂泛型...")
    for i in range(30):
        filepath = os.path.join(test_dir, f"ComplexGenerics{i}.ets")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 复杂泛型测试 {i}
interface GenericInterface<T, U, V, W, X> {{
    method1(arg: T): U;
    method2(arg: U): V;
    method3(arg: V): W;
    method4(arg: W): X;
}}

class ComplexGeneric{i}<A, B, C, D, E, F, G, H, I, J> implements GenericInterface<A, B, C, D, E> {{
    private data: Map<A, Map<B, Map<C, Map<D, Map<E, Map<F, Map<G, Map<H, Map<I, J>>>>>>>>>;
    
    method1(arg: A): B {{
        return null as any;
    }}
    
    method2(arg: B): C {{
        return null as any;
    }}
    
    method3(arg: C): D {{
        return null as any;
    }}
    
    method4(arg: D): E {{
        return null as any;
    }}
    
    complexMethod<T1, T2, T3>(arg1: T1, arg2: T2, arg3: T3): Map<T1, Map<T2, T3>> {{
        return new Map();
    }}
}}
""")

    # 场景5: 循环引用和相互依赖
    print("场景5: 创建循环引用...")
    for i in range(40):
        filepath = os.path.join(test_dir, f"CircularRef{i}.ets")
        next_i = (i + 1) % 40
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 循环引用测试 {i}
import {{ Class{next_i} }} from './CircularRef{next_i}';

export class Class{i} {{
    private next: Class{next_i} | null = null;
    
    method{i}() {{
        if (this.next) {{
            this.next.method{next_i}();
        }}
    }}
    
    setNext(obj: Class{next_i}) {{
        this.next = obj;
    }}
}}
""")

    # 场景6: 混合注释和字符串中的代码
    print("场景6: 创建混合注释字符串...")
    for i in range(30):
        filepath = os.path.join(test_dir, f"MixedComments{i}.ets")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 混合注释和字符串测试 {i}
class MixedClass{i} {{
    /* 
       这个注释包含看起来像代码的内容:
       class FakeClass {{
           method() {{ console.log('fake'); }}
       }}
    */
    
    method{i}() {{
        // 这也是一个注释: if (true) {{ console.log('comment'); }}
        let str1 = "字符串中的代码: class Fake {{ method() {{}} }}";
        let str2 = '另一个字符串: if (true) {{ return 42; }}';
        let str3 = `模板字符串: for (let i = 0; i < 10; i++) {{ }}`;
        
        /*
         * 多行注释中的代码:
         * function fake() {{
         *     return "fake";
         * }}
         */
        
        console.log(str1);
        console.log(str2);
        console.log(str3);
    }}
}}
""")

    # 场景7: 极端参数数量
    print("场景7: 创建极端参数...")
    for i in range(20):
        filepath = os.path.join(test_dir, f"ExtremeParams{i}.ets")
        
        # 生成100个参数
        params = ", ".join([f"param{j}: any" for j in range(100)])
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 极端参数测试 {i}
class ExtremeParams{i} {{
    methodWith100Params({params}) {{
        console.log('100 params');
    }}
    
    methodWithRest(...args: any[]) {{
        console.log('rest params');
    }}
    
    methodWithOptional(param1?: string, param2?: number, param3?: boolean, param4?: any, param5?: object) {{
        console.log('optional params');
    }}
}}
""")

    # 场景8: Unicode和特殊字符
    print("场景8: 创建Unicode特殊字符...")
    for i in range(20):
        filepath = os.path.join(test_dir, f"Unicode{i}.ets")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// Unicode和特殊字符测试 {i}
class Unicode测试{i} {{
    中文方法名() {{
        let 日本語変数 = "日本語";
        let 한국어변수 = "한국어";
        let Ελληνικά = "Greek";
        let العربية = "Arabic";
        let עברית = "Hebrew";
        let ไทย = "Thai";
        
        console.log(日本語変数);
        console.log(한국어변수);
        console.log(Ελληνικά);
        console.log(العربية);
        console.log(עברית);
        console.log(ไทย);
    }}
    
    emojiMethod() {{
        let 😊 = "happy";
        let 🎉 = "celebration";
        let ❤️ = "love";
        console.log(😊, 🎉, ❤️);
    }}
}}
""")

    # 场景9: 异步和Promise链
    print("场景9: 创建异步Promise链...")
    for i in range(30):
        filepath = os.path.join(test_dir, f"AsyncChain{i}.ets")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 异步Promise链测试 {i}
class AsyncChain{i} {{
    async method1() {{
        return await this.method2();
    }}
    
    async method2() {{
        return await this.method3();
    }}
    
    async method3() {{
        return await this.method4();
    }}
    
    async method4() {{
        return await this.method5();
    }}
    
    async method5() {{
        return new Promise<string>((resolve, reject) => {{
            setTimeout(() => {{
                resolve('done');
            }}, 100);
        }});
    }}
    
    promiseChain() {{
        return new Promise<string>((resolve) => resolve('start'))
            .then((result) => {{ console.log(result); return 'step1'; }})
            .then((result) => {{ console.log(result); return 'step2'; }})
            .then((result) => {{ console.log(result); return 'step3'; }})
            .then((result) => {{ console.log(result); return 'step4'; }})
            .then((result) => {{ console.log(result); return 'step5'; }})
            .catch((error) => {{ console.error(error); }})
            .finally(() => {{ console.log('done'); }});
    }}
}}
""")

    # 场景10: 复杂的继承和实现
    print("场景10: 创建复杂继承...")
    for i in range(30):
        filepath = os.path.join(test_dir, f"ComplexInheritance{i}.ets")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// 复杂继承测试 {i}
interface Interface1 {{
    method1(): void;
}}

interface Interface2 {{
    method2(): void;
}}

interface Interface3 extends Interface1, Interface2 {{
    method3(): void;
}}

abstract class AbstractBase {{
    abstract abstractMethod(): void;
    
    concreteMethod() {{
        console.log('concrete');
    }}
}}

class MixinClass {{
    mixinMethod() {{
        console.log('mixin');
    }}
}}

class ComplexInheritance{i} extends AbstractBase implements Interface3 {{
    method1() {{ console.log('method1'); }}
    method2() {{ console.log('method2'); }}
    method3() {{ console.log('method3'); }}
    abstractMethod() {{ console.log('abstract'); }}
}}
""")

    # 统计文件数量
    file_count = sum(1 for root, dirs, files in os.walk(test_dir)
                     for f in files if f.endswith('.ets'))
    
    print(f"\n✅ 极端混乱测试项目创建完成!")
    print(f"   文件数量: {file_count}")
    print(f"   场景类型: 10种")
    print(f"   预估类数量: ~300")
    print(f"   预估方法数量: ~2000")


if __name__ == "__main__":
    create_extreme_chaos_project()
