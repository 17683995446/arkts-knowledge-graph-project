#!/usr/bin/env python3
"""
创建超大规模测试数据 - 压力测试用
"""
import os
import sys


def create_massive_test_data():
    """创建超大规模测试数据"""
    test_dir = "/workspace/massive_chaos_project"
    os.makedirs(test_dir, exist_ok=True)
    
    print(f"创建超大规模测试项目: {test_dir}")
    
    # 创建1000个文件
    for i in range(1000):
        subdir = os.path.join(test_dir, f"module_{i // 100}")
        os.makedirs(subdir, exist_ok=True)
        
        filepath = os.path.join(subdir, f"TestClass{i}.ets")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"""// Test file {i}
// 包含复杂代码结构
import {{ Utility{i}, Helper{i} }} from './utils{i}';
import {{ Service{i} }} from './services/service{i}';

@Component
@Entry
@Preview
struct TestComponent{i} {{
    @State message{i}: string = 'Hello World {i}';
    @Prop title{i}: string = 'Title {i}';
    @Link data{i}: object;
    @StorageProp('key{i}') storageValue{i}: string;
    
    // 生命周期方法
    aboutToAppear() {{
        console.log('Component {i} about to appear');
        this.initData{i}();
    }}
    
    aboutToDisappear() {{
        console.log('Component {i} about to disappear');
        this.cleanup{i}();
    }}
    
    // 私有方法
    @Private
    initData{i}() {{
        this.fetchData{i}();
        this.processData{i}();
        this.validateData{i}();
    }}
    
    @Private
    cleanup{i}() {{
        this.clearCache{i}();
        this.releaseResources{i}();
    }}
    
    // 公共方法
    @Public
    updateState{i}(newValue: string) {{
        this.message{i} = newValue;
        this.notifyChange{i}();
        this.persistData{i}();
    }}
    
    @Public
    handleEvent{i}(event: any) {{
        this.processEvent{i}(event);
        this.validateEvent{i}(event);
        this.dispatchEvent{i}(event);
    }}
    
    // 异步方法
    async fetchData{i}() {{
        try {{
            const response = await this.apiCall{i}();
            this.processResponse{i}(response);
        }} catch (error) {{
            this.handleError{i}(error);
        }}
    }}
    
    async apiCall{i}(): Promise<any> {{
        return new Promise((resolve, reject) => {{
            setTimeout(() => {{
                resolve({{ data: 'test', id: {i} }});
            }}, 100);
        }});
    }}
    
    // 业务方法
    processData{i}() {{
        const data = this.transform{i}(this.rawData{i});
        this.cache{i}(data);
        return data;
    }}
    
    transform{i}(input: any): any {{
        return JSON.parse(JSON.stringify(input));
    }}
    
    validateData{i}() {{
        if (!this.rawData{i}) {{
            throw new Error('Data is required');
        }}
        return true;
    }}
    
    notifyChange{i}() {{
        EventHub{i}.emit('change', {{
            id: {i},
            timestamp: Date.now()
        }});
    }}
    
    persistData{i}() {{
        Storage{i}.set('data_{i}', JSON.stringify(this.rawData{i}));
    }}
    
    processEvent{i}(event: any) {{
        console.log('Processing event:', event);
    }}
    
    validateEvent{i}(event: any) {{
        if (!event) return false;
        return true;
    }}
    
    dispatchEvent{i}(event: any) {{
        this.bus{i}.emit('event', event);
    }}
    
    handleError{i}(error: any) {{
        console.error('Error:', error);
        Logger{i}.error(error);
    }}
    
    clearCache{i}() {{
        Cache{i}.clear();
    }}
    
    releaseResources{i}() {{
        this.subscription{i}.unsubscribe();
    }}
    
    // 构建方法
    build() {{
        Column() {{
            Text(this.message{i})
                .fontSize(20)
                .onClick(() => {{
                    this.onClick{i}();
                }})
            
            Button('Click {i}')
                .onClick(() => {{
                    this.updateState{i}('Clicked!');
                }})
            
            ForEach(this.items{i}, (item: any) => {{
                this.renderItem{i}(item);
            }})
        }}
        .width('100%')
        .height('100%')
    }}
    
    renderItem{i}(item: any) {{
        Row() {{
            Text(item.name)
            Text(item.value.toString())
        }}
    }}
    
    onClick{i}() {{
        this.updateState{i}('Clicked at ' + Date.now());
    }}
    
    // 辅助方法
    private rawData{i}: any = null;
    private items{i}: any[] = [];
    private subscription{i}: any = null;
    private bus{i}: any = null;
    
    @StorageLink('count{i}') count{i}: number = 0;
    
    increment{i}() {{
        this.count{i}++;
        this.updateCount{i}();
    }}
    
    updateCount{i}() {{
        this.persistCount{i}();
    }}
    
    persistCount{i}() {{
        AppStorage{i}.setOrCreate('count_{i}', this.count{i});
    }}
    
    getCount{i}(): number {{
        return this.count{i};
    }}
    
    reset{i}() {{
        this.count{i} = 0;
        this.rawData{i} = null;
        this.items{i} = [];
    }}
    
    load{i}(key: string) {{
        const value = Storage{i}.get(key);
        if (value) {{
            this.rawData{i} = JSON.parse(value);
        }}
    }}
    
    save{i}(key: string, value: any) {{
        Storage{i}.set(key, JSON.stringify(value));
    }}
    
    remove{i}(key: string) {{
        Storage{i}.delete(key);
    }}
    
    has{i}(key: string): boolean {{
        return Storage{i}.has(key);
    }}
    
    getKeys{i}(): string[] {{
        return Storage{i}.keys();
    }}
    
    clearAll{i}() {{
        Storage{i}.clear();
    }}
    
    getSize{i}(): number {{
        return this.items{i}.length;
    }}
    
    isEmpty{i}(): boolean {{
        return this.items{i}.length === 0;
    }}
    
    isNotEmpty{i}(): boolean {{
        return this.items{i}.length > 0;
    }}
    
    getFirst{i}(): any {{
        return this.items{i}[0];
    }}
    
    getLast{i}(): any {{
        return this.items{i}[this.items{i}.length - 1];
    }}
    
    addItem{i}(item: any) {{
        this.items{i}.push(item);
        this.onAdd{i}(item);
    }}
    
    removeItem{i}(item: any) {{
        const index = this.items{i}.indexOf(item);
        if (index > -1) {{
            this.items{i}.splice(index, 1);
            this.onRemove{i}(item);
        }}
    }}
    
    onAdd{i}(item: any) {{
        console.log('Item added:', item);
    }}
    
    onRemove{i}(item: any) {{
        console.log('Item removed:', item);
    }}
    
    find{i}(predicate: (item: any) => boolean): any {{
        return this.items{i}.find(predicate);
    }}
    
    filter{i}(predicate: (item: any) => boolean): any[] {{
        return this.items{i}.filter(predicate);
    }}
    
    map{i}(transformer: (item: any) => any): any[] {{
        return this.items{i}.map(transformer);
    }}
    
    reduce{i}(reducer: (acc: any, item: any) => any, initial: any): any {{
        return this.items{i}.reduce(reducer, initial);
    }}
    
    some{i}(predicate: (item: any) => boolean): boolean {{
        return this.items{i}.some(predicate);
    }}
    
    every{i}(predicate: (item: any) => boolean): boolean {{
        return this.items{i}.every(predicate);
    }}
    
    includes{i}(item: any): boolean {{
        return this.items{i}.includes(item);
    }}
    
    indexOf{i}(item: any): number {{
        return this.items{i}.indexOf(item);
    }}
    
    slice{i}(start: number, end: number): any[] {{
        return this.items{i}.slice(start, end);
    }}
    
    splice{i}(start: number, deleteCount: number, ...items: any[]): any[] {{
        return this.items{i}.splice(start, deleteCount, ...items);
    }}
    
    sort{i}(comparator?: (a: any, b: any) => number) {{
        this.items{i}.sort(comparator);
    }}
    
    reverse{i}() {{
        this.items{i}.reverse();
    }}
    
    join{i}(separator?: string): string {{
        return this.items{i}.join(separator);
    }}
    
    forEach{i}(callback: (item: any, index: number) => void) {{
        this.items{i}.forEach(callback);
    }}
    
    [Symbol.iterator{i}]() {{
        return this.items{i}[Symbol.iterator]();
    }}
}}

// 额外的工具类
class Utility{i} {{
    static format{i}(value: any): string {{
        return JSON.stringify(value);
    }}
    
    static parse{i}(value: string): any {{
        return JSON.parse(value);
    }}
    
    static clone{i}<T>(obj: T): T {{
        return JSON.parse(JSON.stringify(obj));
    }}
    
    static merge{i}(target: any, source: any): any {{
        return {{ ...target, ...source }};
    }}
    
    static isEmpty{i}(value: any): boolean {{
        if (Array.isArray(value)) return value.length === 0;
        if (typeof value === 'object') return Object.keys(value).length === 0;
        return false;
    }}
}}

class Helper{i} {{
    debounce{i}(fn: Function, delay: number): Function {{
        let timeoutId: any;
        return (...args: any[]) => {{
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn(...args), delay);
        }};
    }}
    
    throttle{i}(fn: Function, limit: number): Function {{
        let inThrottle: boolean;
        return (...args: any[]) => {{
            if (!inThrottle) {{
                fn(...args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }}
        }};
    }}
}}

class Service{i} {{
    async getData{i}(): Promise<any> {{
        return new Promise(resolve => {{
            setTimeout(() => resolve({{ data: 'service {i}' }}), 50);
        }});
    }}
    
    async postData{i}(data: any): Promise<any> {{
        return new Promise(resolve => {{
            setTimeout(() => resolve({{ success: true, data }}), 50);
        }});
    }}
    
    async deleteData{i}(id: string): Promise<boolean> {{
        return new Promise(resolve => {{
            setTimeout(() => resolve(true), 50);
        }});
    }}
    
    async updateData{i}(id: string, data: any): Promise<any> {{
        return new Promise(resolve => {{
            setTimeout(() => resolve({{ id, ...data }}), 50);
        }});
    }}
}}

// 导出
export {{ Utility{i}, Helper{i}, Service{i}, TestComponent{i} }};
""")
        
        if (i % 100 == 0):
            print(f"创建了 {i} 个文件...")
    
    print(f"✅ 超大规模测试项目创建完成!")
    print(f"   文件数量: 1000")
    print(f"   预估类数量: ~5000")
    print(f"   预估方法数量: ~50000")


if __name__ == "__main__":
    create_massive_test_data()
