/**
 * 复杂集合数据结构
 */
export class Node<T> {
    value: T;
    next?: Node<T>;
    prev?: Node<T>;
    
    constructor(value: T) {
        this.value = value;
    }
}

export class LinkedList<T> {
    private _size: number = 0;
    private _head?: Node<T>;
    private _tail?: Node<T>;
    
    get size(): number {
        return this._size;
    }
    
    get isEmpty(): boolean {
        return this._size === 0;
    }
    
    addFirst(value: T): void {
        const newNode = new Node(value);
        if (this._head) {
            newNode.next = this._head;
            this._head.prev = newNode;
            this._head = newNode;
        } else {
            this._head = newNode;
            this._tail = newNode;
        }
        this._size++;
    }
    
    addLast(value: T): void {
        const newNode = new Node(value);
        if (this._tail) {
            newNode.prev = this._tail;
            this._tail.next = newNode;
            this._tail = newNode;
        } else {
            this._head = newNode;
            this._tail = newNode;
        }
        this._size++;
    }
    
    removeFirst(): T | undefined {
        if (!this._head) {
            return undefined;
        }
        const value = this._head.value;
        if (this._head === this._tail) {
            this._head = undefined;
            this._tail = undefined;
        } else {
            this._head = this._head.next;
            if (this._head) {
                this._head.prev = undefined;
            }
        }
        this._size--;
        return value;
    }
    
    removeLast(): T | undefined {
        if (!this._tail) {
            return undefined;
        }
        const value = this._tail.value;
        if (this._head === this._tail) {
            this._head = undefined;
            this._tail = undefined;
        } else {
            this._tail = this._tail.prev;
            if (this._tail) {
                this._tail.next = undefined;
            }
        }
        this._size--;
        return value;
    }
    
    clear(): void {
        this._head = undefined;
        this._tail = undefined;
        this._size = 0;
    }
    
    toArray(): T[] {
        const result: T[] = [];
        let current = this._head;
        while (current) {
            result.push(current.value);
            current = current.next;
        }
        return result;
    }
}

export class Queue<T> {
    private list: LinkedList<T>;
    
    constructor() {
        this.list = new LinkedList();
    }
    
    get size(): number {
        return this.list.size;
    }
    
    enqueue(value: T): void {
        this.list.addLast(value);
    }
    
    dequeue(): T | undefined {
        return this.list.removeFirst();
    }
    
    peek(): T | undefined {
        if (!this.list.isEmpty) {
            return undefined;
        }
        const first = this.list.removeFirst();
        if (first) {
            this.list.addFirst(first);
        }
        return first;
    }
    
    isEmpty(): boolean {
        return this.list.isEmpty;
    }
}

export class HashMap<K, V> {
    private map: Map<K, V>;
    
    constructor() {
        this.map = new Map();
    }
    
    set(key: K, value: V): void {
        this.map.set(key, value);
    }
    
    get(key: K): V | undefined {
        return this.map.get(key);
    }
    
    has(key: K): boolean {
        return this.map.has(key);
    }
    
    delete(key: K): boolean {
        return this.map.delete(key);
    }
    
    clear(): void {
        this.map.clear();
    }
    
    get size(): number {
        return this.map.size;
    }
    
    keys(): K[] {
        return Array.from(this.map.keys());
    }
    
    values(): V[] {
        return Array.from(this.map.values());
    }
    
    entries(): [K, V][] {
        return Array.from(this.map.entries());
    }
}

export class Stack<T> {
    private _data: T[];
    
    constructor() {
        this._data = [];
    }
    
    get size(): number {
        return this._data.length;
    }
    
    push(value: T): void {
        this._data.push(value);
    }
    
    pop(): T | undefined {
        return this._data.pop();
    }
    
    peek(): T | undefined {
        return this._data[this._data.length - 1];
    }
    
    isEmpty(): boolean {
        return this._data.length === 0;
    }
    
    clear(): void {
        this._data = [];
    }
}

export class Tree<T> {
    value: T;
    children: Tree<T>[];
    
    constructor(value: T) {
        this.value = value;
        this.children = [];
    }
    
    addChild(value: T): Tree<T> {
        const child = new Tree(value);
        this.children.push(child);
        return child;
    }
    
    traverseDFS(callback: (node: Tree<T>) => void): void {
        callback(this);
        for (const child of this.children) {
            child.traverseDFS(callback);
        }
    }
    
    traverseBFS(callback: (node: Tree<T>) => void): void {
        const queue = new Queue<Tree<T>>();
        queue.enqueue(this);
        while (!queue.isEmpty()) {
            const current = queue.dequeue();
            if (current) {
                callback(current);
                for (const child of current.children) {
                    queue.enqueue(child);
                }
            }
        }
    }
}
