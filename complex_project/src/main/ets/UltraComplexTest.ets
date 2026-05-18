
// UltraComplexTest.ets - 超复杂测试文件，包含各种边缘情况

// 1. 嵌套多层继承
class BaseClass<T> {
    protected data: T;
    constructor(data: T) {
        this.data = data;
    }
    process(): T {
        return this.data;
    }
    transform<U>(fn: (t: T) => U): U {
        return fn(this.data);
    }
}

class IntermediateClass<T, U> extends BaseClass<T> {
    secondary: U;
    constructor(data: T, secondary: U) {
        super(data);
        this.secondary = secondary;
    }
    combine(): string {
        return `${this.data}-${this.secondary}`;
    }
}

class FinalClass extends IntermediateClass<string, number> {
    private id: number;
    constructor(data: string, num: number) {
        super(data, num);
        this.id = Date.now();
    }
    execute(): string {
        const processed = this.process();
        const combined = this.combine();
        const transformed = this.transform(x => x.toUpperCase());
        return `${processed} -> ${combined} -> ${transformed}`;
    }
}

// 2. 递归数据结构
class TreeNode<T> {
    value: T;
    children: TreeNode<T>[] = [];
    parent: TreeNode<T> | null = null;

    constructor(value: T) {
        this.value = value;
    }

    addChild(value: T): TreeNode<T> {
        const child = new TreeNode<T>(value);
        child.parent = this;
        this.children.push(child);
        return child;
    }

    traverse(fn: (node: TreeNode<T>) => void): void {
        fn(this);
        this.children.forEach(child => child.traverse(fn));
    }

    find(predicate: (node: TreeNode<T>) => boolean): TreeNode<T> | null {
        if (predicate(this)) return this;
        for (const child of this.children) {
            const found = child.find(predicate);
            if (found) return found;
        }
        return null;
    }
}

// 3. 复杂的状态机
class StateMachine<S, E> {
    private states: Map<S, (event: E) => S> = new Map();
    private currentState: S;
    private history: S[] = [];

    constructor(initialState: S) {
        this.currentState = initialState;
        this.history.push(initialState);
    }

    addTransition(state: S, handler: (event: E) => S): void {
        this.states.set(state, handler);
    }

    transition(event: E): S {
        const handler = this.states.get(this.currentState);
        if (handler) {
            this.currentState = handler(event);
            this.history.push(this.currentState);
        }
        return this.currentState;
    }

    getHistory(): S[] {
        return [...this.history];
    }
}

// 4. 异步链式调用
class AsyncChain<T> {
    private value: T;

    constructor(value: T) {
        this.value = value;
    }

    async map<U>(fn: (value: T) => Promise<U>): Promise<AsyncChain<U>> {
        const result = await fn(this.value);
        return new AsyncChain<U>(result);
    }

    async flatMap<U>(fn: (value: T) => Promise<AsyncChain<U>>): Promise<AsyncChain<U>> {
        return await fn(this.value);
    }

    async filter(predicate: (value: T) => Promise<boolean>): Promise<AsyncChain<T> | null> {
        const result = await predicate(this.value);
        return result ? this : null;
    }
}

// 5. 装饰器模式多层包装
interface Component {
    operation(): string;
}

class ConcreteComponent implements Component {
    operation(): string {
        return "ConcreteComponent";
    }
}

abstract class Decorator implements Component {
    protected component: Component;

    constructor(component: Component) {
        this.component = component;
    }

    operation(): string {
        return this.component.operation();
    }
}

class LoggingDecorator extends Decorator {
    operation(): string {
        console.log("Before operation");
        const result = super.operation();
        console.log("After operation");
        return `[LOG] ${result}`;
    }
}

class ValidationDecorator extends Decorator {
    operation(): string {
        const result = super.operation();
        return `[VALIDATED] ${result}`;
    }
}

class CachingDecorator extends Decorator {
    private cache: Map<string, string> = new Map();

    operation(): string {
        const key = "cached_key";
        if (this.cache.has(key)) {
            return this.cache.get(key) + " [CACHED]";
        }
        const result = super.operation();
        this.cache.set(key, result);
        return result;
    }
}

// 6. 图结构
class Graph<T> {
    private adjacencyList: Map<T, T[]> = new Map();

    addVertex(vertex: T): void {
        if (!this.adjacencyList.has(vertex)) {
            this.adjacencyList.set(vertex, []);
        }
    }

    addEdge(v1: T, v2: T): void {
        this.adjacencyList.get(v1)?.push(v2);
        this.adjacencyList.get(v2)?.push(v1);
    }

    bfs(start: T): T[] {
        const visited = new Set<T>();
        const queue: T[] = [start];
        const result: T[] = [];

        while (queue.length > 0) {
            const vertex = queue.shift()!;
            if (!visited.has(vertex)) {
                visited.add(vertex);
                result.push(vertex);
                const neighbors = this.adjacencyList.get(vertex) || [];
                queue.push(...neighbors);
            }
        }
        return result;
    }

    dfs(start: T): T[] {
        const visited = new Set<T>();
        const result: T[] = [];

        const dfsHelper = (vertex: T): void => {
            visited.add(vertex);
            result.push(vertex);
            const neighbors = this.adjacencyList.get(vertex) || [];
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    dfsHelper(neighbor);
                }
            }
        };

        dfsHelper(start);
        return result;
    }
}

// 7. 观察者模式
interface Observer {
    update(data: any): void;
}

class Subject {
    private observers: Observer[] = [];

    attach(observer: Observer): void {
        this.observers.push(observer);
    }

    detach(observer: Observer): void {
        const index = this.observers.indexOf(observer);
        if (index > -1) {
            this.observers.splice(index, 1);
        }
    }

    notify(data: any): void {
        this.observers.forEach(observer => observer.update(data));
    }
}

// 8. 生成器模式
class Builder {
    private parts: string[] = [];

    addPart(part: string): Builder {
        this.parts.push(part);
        return this;
    }

    addParts(parts: string[]): Builder {
        this.parts.push(...parts);
        return this;
    }

    build(): string {
        return this.parts.join("-");
    }
}

// 9. 策略模式
interface Strategy {
    execute(data: string[]): string;
}

class ConcreteStrategyA implements Strategy {
    execute(data: string[]): string {
        return data.join(", ");
    }
}

class ConcreteStrategyB implements Strategy {
    execute(data: string[]): string {
        return data.reverse().join(" | ");
    }
}

class Context {
    private strategy: Strategy;

    constructor(strategy: Strategy) {
        this.strategy = strategy;
    }

    setStrategy(strategy: Strategy): void {
        this.strategy = strategy;
    }

    executeStrategy(data: string[]): string {
        return this.strategy.execute(data);
    }
}

// 10. 复杂的泛型约束
class Container<T extends { id: number; name: string }> {
    private items: T[] = [];

    add(item: T): void {
        this.items.push(item);
    }

    findById(id: number): T | undefined {
        return this.items.find(item => item.id === id);
    }

    findByName(name: string): T[] {
        return this.items.filter(item => item.name.includes(name));
    }

    map<U>(fn: (item: T) => U): U[] {
        return this.items.map(fn);
    }

    reduce<U>(fn: (acc: U, item: T) => U, initial: U): U {
        return this.items.reduce(fn, initial);
    }
}

// 11. 多线程模拟（Promise.all）
async function parallelTask(id: number): Promise<number> {
    return new Promise(resolve => {
        setTimeout(() => resolve(id * 2), Math.random() * 100);
    });
}

async function runParallelTasks(): Promise<number[]> {
    const tasks = [1, 2, 3, 4, 5].map(id => parallelTask(id));
    return await Promise.all(tasks);
}

// 12. 深度拷贝
function deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }

    if (obj instanceof Date) {
        return new Date(obj.getTime()) as any;
    }

    if (obj instanceof Array) {
        return obj.map(item => deepClone(item)) as any;
    }

    if (obj instanceof Object) {
        const clonedObj = {} as T;
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = deepClone(obj[key]);
            }
        }
        return clonedObj;
    }

    return obj;
}

// 13. 复杂计算
function fibonacci(n: number): number {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

function memoize<T extends (...args: any[]) => any>(fn: T): T {
    const cache = new Map();
    return ((...args: any[]) => {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
            return cache.get(key);
        }
        const result = fn(...args);
        cache.set(key, result);
        return result;
    }) as T;
}

const memoizedFib = memoize(fibonacci);

// 14. 事件发射器
class EventEmitter {
    private events: Map<string, Function[]> = new Map();

    on(event: string, listener: Function): void {
        if (!this.events.has(event)) {
            this.events.set(event, []);
        }
        this.events.get(event)!.push(listener);
    }

    emit(event: string, ...args: any[]): void {
        const listeners = this.events.get(event);
        if (listeners) {
            listeners.forEach(listener => listener(...args));
        }
    }

    off(event: string, listener: Function): void {
        const listeners = this.events.get(event);
        if (listeners) {
            const index = listeners.indexOf(listener);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }
}

// 15. 管道模式
function pipe<T>(...fns: Array<(input: T) => T>): (input: T) => T {
    return (input: T): T => {
        return fns.reduce((acc, fn) => fn(acc), input);
    };
}

// 使用示例
@Entry
@Component
struct UltraComplexTest {
    @State message: string = 'Ultra Complex Test';

    build() {
        Column() {
            Text(this.message)
                .fontSize(30)
        }
        .padding(20)
    }

    aboutToAppear(): void {
        // 运行所有复杂测试
        this.runComplexTests();
    }

    runComplexTests(): void {
        // 测试继承链
        const final = new FinalClass("test", 123);
        console.log(final.execute());

        // 测试树结构
        const tree = new TreeNode<string>("root");
        tree.addChild("child1").addChild("grandchild1");
        tree.addChild("child2");
        tree.traverse(node => console.log(node.value));

        // 测试状态机
        const machine = new StateMachine<string, string>("idle");
        machine.addTransition("idle", () => "loading");
        machine.addTransition("loading", () => "success");
        machine.transition("start");
        machine.transition("start");

        // 测试装饰器
        let component: Component = new ConcreteComponent();
        component = new LoggingDecorator(component);
        component = new ValidationDecorator(component);
        component = new CachingDecorator(component);
        console.log(component.operation());

        // 测试图
        const graph = new Graph<number>();
        [1, 2, 3, 4, 5].forEach(v => graph.addVertex(v));
        graph.addEdge(1, 2);
        graph.addEdge(1, 3);
        graph.addEdge(2, 4);
        graph.addEdge(3, 4);
        graph.addEdge(4, 5);
        console.log(graph.bfs(1));
        console.log(graph.dfs(1));

        // 测试生成器
        const builder = new Builder();
        const result = builder
            .addPart("part1")
            .addParts(["part2", "part3"])
            .addPart("part4")
            .build();
        console.log(result);

        // 测试策略
        const context = new Context(new ConcreteStrategyA());
        console.log(context.executeStrategy(["a", "b", "c"]));
        context.setStrategy(new ConcreteStrategyB());
        console.log(context.executeStrategy(["a", "b", "c"]));

        // 测试复杂计算
        console.log(memoizedFib(10));
        console.log(memoizedFib(20));
        console.log(memoizedFib(30));

        // 测试管道
        const process = pipe(
            (x: number) => x * 2,
            (x: number) => x + 1,
            (x: number) => x.toString()
        );
        console.log(process(5));

        // 测试深度克隆
        const original = { a: 1, b: { c: 2, d: [1, 2, 3] } };
        const cloned = deepClone(original);
        console.log(JSON.stringify(cloned));

        this.message = 'All Tests Complete!';
    }
}
