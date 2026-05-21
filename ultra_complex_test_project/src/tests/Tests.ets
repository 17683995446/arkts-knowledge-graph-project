/**
 * 测试模块
 */
import { LinkedList, Queue, Stack, HashMap, Tree } from '../core';

export class TestRunner {
    private results: { passed: number; failed: number; errors: any[];
    
    constructor() {
        this.results = { passed: 0, failed: 0, errors: [] };
    }
    
    test(name: string, fn: () => void | Promise<void>): void {
        try {
            fn();
            this.results.passed++;
            console.log(`✅ ${name}');
        } catch (error) {
            this.results.failed++;
            this.results.errors.push({ name, error });
            console.error(`❌ ${name}:`, error);
        }
    }
    
    async testAsync(name: string, fn: () => Promise<void>): Promise<void> {
        try {
            await fn();
            this.results.passed++;
            console.log(`✅ ${name}');
        } catch (error) {
            this.results.failed++;
            this.results.errors.push({ name, error });
            console.error(`❌ ${name}:`, error);
        }
    }
    
    getResults() {
        return this.results;
    }
}

export class CollectionTests {
    static run(): void {
        const runner = new TestRunner();
        
        console.log('\n=== LinkedList 测试 ===');
        runner.test('LinkedList.addFirst', () => {
            const list = new LinkedList<number>();
            list.addFirst(1);
            list.addFirst(2);
            if (list.size !== 2) throw new Error('大小应为 2');
        });
        
        runner.test('LinkedList.removeFirst', () => {
            const list = new LinkedList<number>();
            list.addFirst(1);
            list.addFirst(2);
            const value = list.removeFirst();
            if (value !== 2) throw new Error('应为 2');
            if (list.size !== 1) throw new Error('大小应为 1');
        });
        
        runner.test('LinkedList.removeLast', () => {
            const list = new LinkedList<number>();
            list.addLast(1);
            list.addLast(2);
            const value = list.removeLast();
            if (value !== 2) throw new Error('应为 2');
        });
        
        console.log('\n=== Queue 测试 ===');
        runner.test('Queue.enqueue', () => {
            const queue = new Queue<number>();
            queue.enqueue(1);
            queue.enqueue(2);
            queue.enqueue(3);
            if (queue.size !== 3) throw new Error('大小应为 3');
        });
        
        runner.test('Queue.dequeue', () => {
            const queue = new Queue<number>();
            queue.enqueue(1);
            queue.enqueue(2);
            if (queue.dequeue() !== 1) throw new Error('应为 1');
            if (queue.size !== 1) throw new Error('大小应为 1');
        });
        
        console.log('\n=== Stack 测试 ===');
        runner.test('Stack.push', () => {
            const stack = new Stack<number>();
            stack.push(1);
            stack.push(2);
            if (stack.size !== 2) throw new Error('大小应为 2');
        });
        
        console.log('\n=== HashMap 测试 ===');
        runner.test('HashMap.set', () => {
            const map = new HashMap<string, number>();
            map.set('a', 1);
            map.set('b', 2);
            if (map.size !== 2) throw new Error('大小应为 2');
        });
        
        runner.test('HashMap.get', () => {
            const map = new HashMap<string, number>();
            map.set('a', 1);
            if (map.get('a') !== 1) throw new Error('应为 1');
        });
        
        console.log('\n=== Tree 测试 ===');
        runner.test('Tree.addChild', () => {
            const tree = new Tree<number>(1);
            tree.addChild(2);
            tree.addChild(3);
            if (tree.children.length !== 2) throw new Error('子节点应为 2');
        });
        
        const results = runner.getResults();
        console.log(`\n=== 测试结果 ===');
        console.log(`✅ 通过: ${results.passed}');
        console.log(`❌ 失败: ${results.failed}');
        if (results.errors.forEach(error => {
            console.error(error);
        });
    }
}

export class PerformanceTests {
    static run(): void {
        console.log('\n=== 性能测试 ===');
        
        const iterations = 10000;
        
        console.log('LinkedList 性能:');
        const listStart = Date.now();
        const list = new LinkedList<number>();
        for (let i = 0; i < iterations; i++) {
            list.addLast(i);
        }
        const listEnd = Date.now();
        console.log(`  ${iterations} 次 addLast 耗时: ${listEnd - listStart}ms');
        
        console.log('\nHashMap 性能:');
        const mapStart = Date.now();
        const map = new HashMap<string, number>();
        for (let i = 0; i < iterations; i++) {
            map.set(`key_${i}`, i);
        }
        const mapEnd = Date.now();
        console.log(`  ${iterations} 次 set 耗时: ${mapEnd - mapStart}ms');
        
        console.log('\nQueue 性能:');
        const queueStart = Date.now();
        const queue = new Queue<number>();
        for (let i = 0; i < iterations; i++) {
            queue.enqueue(i);
        }
        for (let i = 0; i < iterations; i++) {
            queue.dequeue();
        }
        const queueEnd = Date.now();
        console.log(`  ${iterations} 次 enqueue/dequeue 耗时: ${queueEnd - queueStart}ms');
    }
}

export function runAllTests(): void {
    CollectionTests.run();
    PerformanceTests.run();
    console.log('\n🎉 所有测试完成！');
}
