
#!/usr/bin/env python3
"""
慢工出细活 - 超复杂真实世界测试场景
创建包含真实复杂代码的完整测试项目
"""

import os
import shutil
from pathlib import Path


def create_ultra_complex_test_project():
    """创建包含真实复杂代码的测试项目"""
    base_dir = Path("/workspace/ultra_complex_test_project")
    
    # 清理和重新创建项目
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    print("创建超复杂测试项目...")
    
    # 1. 核心模块
    create_core_module(base_dir)
    
    # 2. UI 组件模块
    create_ui_components_module(base_dir)
    
    # 3. 数据管理模块
    create_data_management_module(base_dir)
    
    # 4. 网络模块
    create_network_module(base_dir)
    
    # 5. 业务逻辑模块
    create_business_logic_module(base_dir)
    
    # 6. 测试模块
    create_test_module(base_dir)
    
    # 7. 工具模块
    create_utils_module(base_dir)
    
    print(f"✅ 超复杂测试项目创建完成！路径: {base_dir}")
    
    return base_dir


def create_core_module(base_dir: Path):
    """创建核心模块 - 包含复杂数据结构和基类"""
    core_dir = base_dir / "src" / "core"
    core_dir.mkdir(parents=True, exist_ok=True)
    
    # 复杂基类文件
    core_code = '''/**
 * 复杂数据结构基类
 */
import { HashMap, LinkedList, Queue } from './Collections';

export enum DataType {
    STRING = 'string',
    NUMBER = 'number',
    BOOLEAN = 'boolean',
    OBJECT = 'object',
    ARRAY = 'array',
    FUNCTION = 'function',
    SYMBOL = 'symbol',
    UNDEFINED = 'undefined',
    NULL = 'null',
    UNION = 'union',
    INTERSECTION = 'intersection',
    TUPLE = 'tuple'
}

export interface IComplexData {
    id: string | number | symbol;
    type: DataType;
    value: any;
    timestamp: number;
    metadata: Map<string, any>;
    children?: IComplexData[];
    parentId?: string | number | symbol;
}

export abstract class BaseComplexClass {
    protected readonly id: string;
    protected readonly createdAt: number;
    protected data: IComplexData;
    private readonly listeners: Map<string, Function[]>;
    private _isDestroyed: boolean;
    
    constructor(id: string, initialData?: Partial<IComplexData> = {}) {
        this.id = id;
        this.createdAt = Date.now();
        this._isDestroyed = false;
        this.data = {
            id: id,
            type: DataType.OBJECT,
            value: {},
            timestamp: this.createdAt,
            metadata: new Map(),
            children: []
        };
        if (initialData) {
            Object.assign(this.data, initialData);
        }
        this.listeners = new Map();
        this.initialize();
    }
    
    protected abstract initialize(): void;
    
    protected emit(event: string, ...args: any[]): void {
        if (this._isDestroyed) {
            console.warn(`[${this.id}] 尝试在销毁后发射事件: ${event}');
            return;
        }
        const handlers = this.listeners.get(event) || [];
        for (const handler of handlers) {
            try {
                handler(...args);
            } catch (error) {
                console.error(`[${this.id}] 事件处理器错误:', event, error);
            }
        }
    }
    
    on(event: string, handler: Function): () => void {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        const handlers = this.listeners.get(event)!;
        handlers.push(handler);
        return () => {
            const index = handlers.indexOf(handler);
            if (index !== -1) {
                handlers.splice(index, 1);
            }
        };
    }
    
    getData(): IComplexData {
        return { ...this.data, children: [...(this.data.children || []) };
    }
    
    setData(key: string, value: any): void {
        if (this._isDestroyed) {
            console.warn(`[${this.id}] 尝试在销毁后设置数据');
            return;
        }
        this.data.value[key] = value;
        this.data.timestamp = Date.now();
        this.emit('dataChanged', key, value);
    }
    
    addChild(child: IComplexData): void {
        if (this._isDestroyed) {
            console.warn(`[${this.id}] 尝试在销毁后添加子项');
            return;
        }
        child.parentId = this.data.id;
        this.data.children = this.data.children || [];
        this.data.children.push(child);
        this.emit('childAdded', child);
    }
    
    destroy(): void {
        if (this._isDestroyed) {
            return;
        }
        this._isDestroyed = true;
        this.emit('beforeDestroy');
        this.listeners.clear();
    }
    
    get isDestroyed(): boolean {
        return this._isDestroyed;
    }
    
    protected validate(): boolean {
        return !this._isDestroyed && this.data !== null;
    }
}

export class ComplexDataProcessor extends BaseComplexClass {
    private processors: Map<string, Function>;
    private cache: HashMap<string, any>;
    
    constructor(id: string) {
        super(id);
        this.processors = new Map();
        this.cache = new HashMap();
    }
    
    protected initialize(): void {
        this.emit('initialized');
    }
    
    registerProcessor(name: string, processor: Function): void {
        this.processors.set(name, processor);
        this.emit('processorRegistered', name);
    }
    
    processData(data: IComplexData, processorName?: string): IComplexData {
        if (processorName && this.processors.has(processorName)) {
            const processor = this.processors.get(processorName)!;
            return processor(data);
        }
        return data;
    }
    
    computeComplexTransformation(source: IComplexData, transforms: string[]): IComplexData {
        let result = source;
        for (const transformName of transforms) {
            if (this.processors.has(transformName)) {
                result = this.processors.get(transformName)!(result);
            }
        }
        return result;
    }
    
    clearCache(): void {
        this.cache.clear();
        this.emit('cacheCleared');
    }
}

export class EventBus {
    private static instance: EventBus;
    private channels: Map<string, Set<Function>>;
    
    private constructor() {
        this.channels = new Map();
    }
    
    static getInstance(): EventBus {
        if (!EventBus.instance) {
            EventBus.instance = new EventBus();
        }
        return EventBus.instance;
    }
    
    subscribe(channel: string, handler: Function): () => void {
        if (!this.channels.has(channel)) {
            this.channels.set(channel, new Set());
        }
        const listeners = this.channels.get(channel)!;
        listeners.add(handler);
        return () => listeners.delete(handler);
    }
    
    publish(channel: string, ...args: any[]): void {
        if (this.channels.has(channel)) {
            for (const listener of this.channels.get(channel)!) {
                try {
                    listener(...args);
                } catch (e) {
                        console.error('事件总线错误:', e);
                    }
            }
        }
    }
    
    unsubscribeAll(): void {
        this.channels.clear();
    }
}

export class DependencyInjector {
    private static instance: DependencyInjector;
    private services: Map<string, any>;
    private factories: Map<string, Function>;
    
    private constructor() {
        this.services = new Map();
        this.factories = new Map();
    }
    
    static getInstance(): DependencyInjector {
        if (!DependencyInjector.instance) {
            DependencyInjector.instance = new DependencyInjector();
        }
        return DependencyInjector.instance;
    }
    
    register<T>(name: string, service: T): void {
        this.services.set(name, service);
    }
    
    registerFactory<T>(name: string, factory: () => T): void {
        this.factories.set(name, factory);
    }
    
    resolve<T>(name: string): T | undefined {
        if (this.services.has(name)) {
            return this.services.get(name);
        }
        if (this.factories.has(name)) {
            const factory = this.factories.get(name)!;
            const service = factory();
            this.services.set(name, service);
            return service;
        }
        return undefined;
    }
}
'''
    
    with open(core_dir / "BaseClasses.ets", 'w', encoding='utf-8') as f:
        f.write(core_code)
    
    # Collections 模块
    collections_code = '''/**
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
'''
    
    with open(core_dir / "Collections.ets", 'w', encoding='utf-8') as f:
        f.write(collections_code)
    
    # 索引文件
    index_code = '''export * from './BaseClasses';
export * from './Collections';
'''
    
    with open(core_dir / "index.ets", 'w', encoding='utf-8') as f:
        f.write(index_code)


def create_ui_components_module(base_dir: Path):
    """创建 UI 组件模块"""
    ui_dir = base_dir / "src" / "ui"
    ui_dir.mkdir(parents=True, exist_ok=True)
    
    button_code = '''/**
 * 复杂 UI 组件
 */
import { BaseComplexClass } from '../core';

export interface IButtonProps {
    id: string;
    text: string;
    onClick?: () => void;
    disabled?: boolean;
    variant?: 'primary' | 'secondary' | 'danger' | 'success';
    size?: 'small' | 'medium' | 'large';
}

@Component
export class Button extends BaseComplexClass {
    props: IButtonProps;
    private _isPressed: boolean;
    private _hover: boolean;
    
    constructor(props: IButtonProps) {
        super(props.id);
        this.props = props;
        this._isPressed = false;
        this._hover = false;
    }
    
    protected initialize(): void {
    }
    
    handlePress(): void {
        if (this.props.disabled || this.isDestroyed) {
            return;
        }
        this._isPressed = true;
        this.emit('press');
        if (this.props.onClick) {
            this.props.onClick();
        }
        setTimeout(() => {
            this._isPressed = false;
            this.emit('release');
        }, 200);
    }
    
    handleMouseEnter(): void {
        this._hover = true;
        this.emit('hover', true);
    }
    
    handleMouseLeave(): void {
        this._hover = false;
        this.emit('hover', false);
    }
    
    render(): string {
        const classes = ['button', this.props.variant || 'primary', this.props.size || 'medium'];
        if (this._isPressed) {
            classes.push('pressed');
        }
        if (this._hover) {
            classes.push('hover');
        }
        if (this.props.disabled) {
            classes.push('disabled');
        }
        return `<button class="${classes.join(' ')}">${this.props.text}</button>`;
    }
}

@Entry
@Component
export struct MainPage {
    @State message: string = 'Hello World';
    @State count: number = 0;
    @State isLoading: boolean = false;
    button: Button | undefined;
    
    build() {
        Column() {
            Text(this.message).fontSize(20).margin(10);
            Button() {
                Text('点击计数: ' + this.count).fontSize(16)
            }.onClick(() => {
                this.count++;
                if (this.button) {
                    this.button.handlePress();
                }
            }).margin(10);
        }.width('100%').height('100%');
    }
    
    aboutToAppear() {
        this.button = new Button({
            id: 'mainButton', text: '主按钮'
        });
        this.button.on('press', () => {
            console.log('按钮被按下');
        });
    }
}

@Component
export struct UserProfile {
    @State userName: string = '';
    @State avatarUrl: string = '';
    @State bio: string = '';
    
    build() {
        Column() {
            if (this.avatarUrl) {
                Image(this.avatarUrl).width(100).height(100).borderRadius(50);
            }
            Text(this.userName).fontSize(18).fontWeight(FontWeight.Bold);
            Text(this.bio).fontSize(14).opacity(0.8).margin(5);
        }.padding(20).backgroundColor('#f5f5f5');
    }
}

@Component
export struct DataList {
    @State items: string[] = [];
    
    build() {
        List() {
            ForEach(this.items, (item: string) => {
                ListItem() {
                    Text(item).padding(10)
                }
            })
        }.height('100%');
    }
    
    addItem(item: string) {
        this.items.push(item);
    }
    
    removeItem(index: number) {
        this.items.splice(index, 1);
    }
}

@Component
export struct LoadingIndicator {
    @State isLoading: boolean = false;
    
    build() {
        if (this.isLoading) {
            Column() {
                LoadingProgress().width(50).height(50);
                Text('加载中...');
            }.justifyContent(FlexAlign.Center);
        }
    }
}
'''
    
    with open(ui_dir / "Buttons.ets", 'w', encoding='utf-8') as f:
        f.write(button_code)
    
    # 表单组件
    form_code = '''/**
 * 复杂表单组件
 */
@Component
export interface IFormField {
    name: string;
    label: string;
    type: 'text' | 'number' | 'email' | 'password' | 'textarea';
    value: any;
    required?: boolean;
    validator?: (value: any) => boolean;
    errorMessage?: string;
}

@Component
export class FormField {
    @State value: any = '';
    @State error: string = '';
    @State isTouched: boolean = false;
    
    config: IFormField;
    
    constructor(config: IFormField) {
        this.config = config;
        this.value = config.value;
    }
    
    validate(): boolean {
        this.isTouched = true;
        if (this.config.required && !this.value) {
            this.error = this.config.errorMessage || '此项为必填';
            return false;
        }
        if (this.config.validator) {
            const isValid = this.config.validator(this.value);
            if (!isValid) {
                this.error = this.config.errorMessage || '验证失败';
                return false;
            }
        }
        this.error = '';
        return true;
    }
    
    build() {
        Column() {
            Text(this.config.label).fontSize(14);
            TextInput({ placeholder: '请输入 ' + this.config.label)
                .text(this.value)
                .onChange((value: string) => {
                    this.value = value;
                    if (this.isTouched) {
                        this.validate();
                    }
                }
            if (this.error) {
                Text(this.error).fontColor(Color.Red).fontSize(12);
            }
        }.width('100%');
    }
}

@Component
export struct ComplexForm {
    @State fields: FormField[] = [];
    @State isSubmitting: boolean = false;
    @State submitSuccess: boolean = false;
    
    build() {
        Column() {
            ForEach(this.fields, (field: FormField) => {
                field
            });
            
            Button('提交')
                .onClick(() => {
                    this.handleSubmit();
                })
                .enabled(!this.isSubmitting)
                .margin({ top: 20 });
            
            if (this.submitSuccess) {
                Text('提交成功！').fontColor(Color.Green);
            }
        }.padding(20);
    }
    
    addField(config: IFormField) {
        const field = new FormField(config);
        this.fields.push(field);
    }
    
    handleSubmit() {
        let allValid = true;
        for (const field of this.fields) {
            if (!field.validate()) {
                allValid = false;
            }
        }
        if (allValid) {
            this.isSubmitting = true;
            setTimeout(() => {
                this.isSubmitting = false;
                this.submitSuccess = true;
            }, 1000);
        }
    }
}

@Component
export struct LoginForm {
    @State email: string = '';
    @State password: string = '';
    @State emailError: string = '';
    @State passwordError: string = '';
    
    build() {
        Column() {
            Text('登录').fontSize(24).fontWeight(FontWeight.Bold).margin({ bottom: 20 });
            
            TextInput({ placeholder: '请输入邮箱' })
                .text(this.email)
                .onChange((value: string) => {
                    this.email = value;
                    this.validateEmail();
                };
            
            if (this.emailError) {
                Text(this.emailError).fontColor(Color.Red);
            }
            
            TextInput({ placeholder: '请输入密码', type: InputType.Password })
                .text(this.password)
                .onChange((value: string) => {
                    this.password = value;
                    this.validatePassword();
                });
            
            if (this.passwordError) {
                Text(this.passwordError).fontColor(Color.Red);
            }
            
            Button('登录')
                .onClick(() => {
                    this.handleLogin();
                })
                .margin({ top: 20 });
        }.padding(20);
    }
    
    validateEmail() {
        if (!this.email) {
            this.emailError = '邮箱不能为空';
            return false;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(this.email)) {
            this.emailError = '请输入有效的邮箱地址';
            return false;
        }
        this.emailError = '';
        return true;
    }
    
    validatePassword() {
        if (!this.password) {
            this.passwordError = '密码不能为空';
            return false;
        }
        if (this.password.length < 6) {
            this.passwordError = '密码长度至少 6 位';
            return false;
        }
        this.passwordError = '';
        return true;
    }
    
    handleLogin() {
        const isEmailValid = this.validateEmail();
        const isPasswordValid = this.validatePassword();
        if (isEmailValid && isPasswordValid) {
            console.log('登录成功');
        }
    }
}
'''
    
    with open(ui_dir / "Forms.ets", 'w', encoding='utf-8') as f:
        f.write(form_code)


def create_data_management_module(base_dir: Path):
    """创建数据管理模块"""
    data_dir = base_dir / "src" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    manager_code = '''/**
 * 数据管理模块
 */
import { BaseComplexClass, HashMap, Queue } from '../core';

export interface IDataStoreConfig {
    name: string;
    version: number;
    data: any;
    createdAt: number;
    updatedAt: number;
}

export class DataStore extends BaseComplexClass {
    private config: IDataStoreConfig;
    private _persistKey: string;
    private _autoSave: boolean;
    private _saveTimeout: number | null = null;
    private _subscribers: Set<() => void> = new Set();
    
    constructor(id: string, persistKey: string, autoSave: boolean = true) {
        super(id);
        this._persistKey = persistKey;
        this._autoSave = autoSave;
        this.loadFromStorage();
    }
    
    protected initialize(): void {
        this.emit('storeInitialized', this.config);
    }
    
    private loadFromStorage(): void {
        try {
            if (localStorage.getItem(this._persistKey);
            if (stored) {
                this.config = JSON.parse(stored);
            } else {
                    this.config = {
                        name: this.id,
                        version: 1,
                        data: {},
                        createdAt: Date.now(),
                        updatedAt: Date.now()
                    };
                }
        } catch (e) {
            console.error('加载数据失败:', e);
            this.config = {
                name: this.id,
                version: 1,
                data: {},
                createdAt: Date.now(),
                updatedAt: Date.now()
            };
        }
    }
    
    get<T>(key: string, defaultValue?: T): T {
        if (key in this.config.data) {
            return this.config.data[key];
        }
        return defaultValue as T;
    }
    
    set(key: string, value: any): void {
        this.config.data[key] = value;
        this.config.updatedAt = Date.now();
        this.notifySubscribers();
        if (this._autoSave) {
            this.scheduleSave();
        }
        this.emit('dataUpdated', key, value);
    }
    
    delete(key: string): boolean {
        if (key in this.config.data) {
            delete this.config.data[key];
            this.config.updatedAt = Date.now();
            this.notifySubscribers();
            if (this._autoSave) {
                this.scheduleSave();
            }
            this.emit('dataDeleted', key);
            return true;
        }
        return false;
    }
    
    clear(): void {
        this.config.data = {};
        this.config.updatedAt = Date.now();
        this.notifySubscribers();
        if (this._autoSave) {
            this.scheduleSave();
        }
        this.emit('storeCleared');
    }
    
    getAll(): any {
        return { ...this.config.data };
    }
    
    subscribe(callback: () => void): () => void {
        this._subscribers.add(callback);
        return () => {
            this._subscribers.delete(callback);
        };
    }
    
    private notifySubscribers(): void {
        for (const callback of this._subscribers) {
            try {
                callback();
            } catch (e) {
                console.error('数据订阅回调错误:', e);
            }
        }
    }
    
    private scheduleSave(): void {
        if (this._saveTimeout) {
            clearTimeout(this._saveTimeout);
        }
        this._saveTimeout = setTimeout(() => {
            this.saveToStorage();
        }, 300);
    }
    
    saveToStorage(): void {
        try {
            localStorage.setItem(this._persistKey, JSON.stringify(this.config));
            this.emit('saved');
        } catch (e) {
            console.error('保存数据失败:', e);
        }
        this._saveTimeout = null;
    }
    
    forceSave(): void {
        if (this._saveTimeout) {
            clearTimeout(this._saveTimeout);
            this._saveTimeout = null;
        }
        this.saveToStorage();
    }
}

export class CacheManager {
    private static instance: CacheManager;
    private cache: HashMap<string, any>;
    private ttl: HashMap<string, number>;
    private defaultTTL: number;
    
    private constructor(defaultTTL: number = 300000) {
        this.cache = new HashMap();
        this.ttl = new HashMap();
        this.defaultTTL = defaultTTL;
    }
    
    static getInstance(): CacheManager {
        if (!CacheManager.instance) {
            CacheManager.instance = new CacheManager();
        }
        return CacheManager.instance;
    }
    
    set(key: string, value: any, ttl?: number): void {
        this.cache.set(key, value);
        const expiry = Date.now() + (ttl || this.defaultTTL);
        this.ttl.set(key, expiry);
    }
    
    get<T>(key: string): T | null {
        if (!this.cache.has(key)) {
            return null;
        }
        const expiry = this.ttl.get(key);
        if (expiry && Date.now() > expiry) {
            this.cache.delete(key);
            this.ttl.delete(key);
            return null;
        }
        return this.cache.get(key);
    }
    
    has(key: string): boolean {
        if (!this.cache.has(key)) {
            return false;
        }
        const expiry = this.ttl.get(key);
        if (expiry && Date.now() > expiry) {
            this.cache.delete(key);
            this.ttl.delete(key);
            return false;
        }
        return true;
    }
    
    delete(key: string): boolean {
        this.cache.delete(key);
        return this.ttl.delete(key);
    }
    
    clear(): void {
        this.cache.clear();
        this.ttl.clear();
    }
}

export class TransactionManager {
    private queue: Queue<() => Promise<any>>;
    private isProcessing: boolean = false;
    private history: any[];
    
    constructor() {
        this.queue = new Queue();
        this.history = [];
    }
    
    enqueue<T>(operation: () => Promise<T>): Promise<T> {
        return new Promise((resolve, reject) => {
            const wrapped = async () => {
                try {
                    const result = await operation();
                    this.history.push({ success: true, timestamp: Date.now() });
                    resolve(result);
                } catch (error) {
                    this.history.push({ success: false, error, timestamp: Date.now() });
                    reject(error);
                }
            };
            this.queue.enqueue(wrapped);
            this.processQueue();
        });
    }
    
    private async processQueue(): Promise<void> {
        if (this.isProcessing) {
            return;
        }
        this.isProcessing = true;
        while (!this.queue.isEmpty()) {
            const operation = this.queue.dequeue();
            if (operation) {
                await operation();
            }
        }
        this.isProcessing = false;
    }
    
    getHistory(): any[] {
        return [...this.history];
    }
    
    clearHistory(): void {
        this.history = [];
    }
}
'''
    
    with open(data_dir / "DataStore.ets", 'w', encoding='utf-8') as f:
        f.write(manager_code)


def create_network_module(base_dir: Path):
    """创建网络模块"""
    net_dir = base_dir / "src" / "network"
    net_dir.mkdir(parents=True, exist_ok=True)
    
    network_code = '''/**
 * 网络模块
 */
import { BaseComplexClass, HashMap } from '../core';

export interface INetworkRequest {
    url: string;
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    headers?: Record<string, string>;
    body?: any;
    timeout?: number;
}

export interface INetworkResponse {
    success: boolean;
    status: number;
    data: any;
    headers: Record<string, string>;
}

export class NetworkClient extends BaseComplexClass {
    private baseURL: string;
    private defaultHeaders: Record<string, string>;
    private timeout: number;
    private requestQueue: HashMap<() => Promise<any>>;
    private requestCount: number = 0;
    
    constructor(id: string, baseURL: string = '', defaultHeaders: Record<string, string> = {}, timeout: number = 30000) {
        super(id);
        this.baseURL = baseURL;
        this.defaultHeaders = defaultHeaders;
        this.timeout = timeout;
        this.requestQueue = new HashMap();
    }
    
    protected initialize(): void {
    }
    
    async get<T>(url: string, config?: Partial<INetworkRequest> = {}): Promise<INetworkResponse> {
        return this.request<T>({
            ...config,
            url,
            method: 'GET'
        });
    }
    
    async post<T>(url: string, body?: any, config?: Partial<INetworkRequest> = {}): Promise<INetworkResponse> {
        return this.request<T>({
            ...config,
            url,
            method: 'POST',
            body
        });
    }
    
    async put<T>(url: string, body?: any, config?: Partial<INetworkRequest> = {}): Promise<INetworkResponse> {
        return this.request<T>({
            ...config,
            url,
            method: 'PUT',
            body
        });
    }
    
    async delete<T>(url: string, config?: Partial<INetworkRequest> = {}): Promise<INetworkResponse> {
        return this.request<T>({
            ...config,
            url,
            method: 'DELETE'
        });
    }
    
    private async request<T>(config: INetworkRequest): Promise<INetworkResponse> {
        this.requestCount++;
        const requestId = `request_${this.requestCount}`;
        const fullURL = this.baseURL + config.url;
        const headers = { ...this.defaultHeaders, ...config.headers };
        this.emit('requestStart', requestId, config);
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => {
                controller.abort();
            }, config.timeout || this.timeout);
            
            const response = await fetch(fullURL, {
                method: config.method,
                headers,
                body: config.body ? JSON.stringify(config.body) : undefined,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const result: INetworkResponse = {
                success: response.ok,
                status: response.status,
                data: await response.json(),
                headers: {}
            };
            
            response.headers.forEach((value, key) => {
                result.headers[key] = value;
            });
            
            this.emit('requestComplete', requestId, result);
            
            return result;
        } catch (error) {
            this.emit('requestError', requestId, error);
            return {
                success: false,
                status: 0,
                data: error,
                headers: {}
            };
        }
    }
    
    setHeader(key: string, value: string): void {
        this.defaultHeaders[key] = value;
        this.emit('headerSet', key, value);
    }
    
    removeHeader(key: string): void {
        delete this.defaultHeaders[key];
        this.emit('headerRemoved', key);
    }
    
    setBaseURL(url: string): void {
        this.baseURL = url;
        this.emit('baseURLChanged', url);
    }
}

export class APIClient {
    private client: NetworkClient;
    private token?: string;
    private refreshToken?: string;
    
    constructor(baseURL: string) {
        this.client = new NetworkClient('api_client', baseURL, {
            'Content-Type': 'application/json'
        });
    }
    
    setAuthToken(token: string): void {
        this.token = token;
        this.client.setHeader('Authorization', `Bearer ${token}');
    }
    
    clearAuthToken(): void {
        this.token = undefined;
        this.client.removeHeader('Authorization');
    }
    
    async login(credentials: { email: string, password: string }): Promise<any> {
        const response = await this.client.post('/auth/login', credentials);
        if (response.success && response.data.token) {
            this.setAuthToken(response.data.token);
            if (response.data.refreshToken) {
                this.refreshToken = response.data.refreshToken;
            }
        }
        return response;
    }
    
    async logout(): Promise<void> {
        await this.client.post('/auth/logout');
        this.clearAuthToken();
        this.refreshToken = undefined;
    }
    
    async getUser(): Promise<any> {
        return this.client.get('/user/me');
    }
    
    async updateUser(data: any): Promise<any> {
        return this.client.put('/user/me', data);
    }
    
    async getItems(params?: Record<string, any>): Promise<any> {
        return this.client.get('/items', { body: params });
    }
    
    async createItem(data: any): Promise<any> {
        return this.client.post('/items', data);
    }
    
    async updateItem(id: string, data: any): Promise<any> {
        return this.client.put(`/items/${id}`, data);
    }
    
    async deleteItem(id: string): Promise<any> {
        return this.client.delete(`/items/${id}`);
    }
}

export class WebSocketClient extends BaseComplexClass {
    private url: string;
    private socket?: WebSocket;
    private reconnectAttempts: number = 0;
    private maxReconnectAttempts: number = 5;
    private reconnectInterval: number = 3000;
    private autoReconnect: boolean = true;
    
    constructor(id: string, url: string) {
        super(id);
        this.url = url;
    }
    
    protected initialize(): void {
    }
    
    connect(): void {
        try {
            this.socket = new WebSocket(this.url);
            
            this.socket.onopen = () => {
                this.reconnectAttempts = 0;
                this.emit('connected');
            };
            
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.emit('message', data);
                } catch (e) {
                    this.emit('message', event.data);
                }
            };
            
            this.socket.onerror = (error) => {
                this.emit('error', error);
            };
            
            this.socket.onclose = (event) => {
                this.emit('disconnected', event);
                if (this.autoReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };
        } catch (e) {
            console.error('WebSocket 连接失败:', e);
        }
    }
    
    disconnect(): void {
        this.autoReconnect = false;
        if (this.socket) {
            this.socket.close();
            this.socket = undefined;
        }
    }
    
    send(data: any): void {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }
    
    private scheduleReconnect(): void {
        this.reconnectAttempts++;
        this.emit('reconnecting', this.reconnectAttempts);
        setTimeout(() => {
            if (this.autoReconnect) {
                this.connect();
            }
        }, this.reconnectInterval * this.reconnectAttempts);
    }
}
'''
    
    with open(net_dir / "NetworkClient.ets", 'w', encoding='utf-8') as f:
        f.write(network_code)


def create_business_logic_module(base_dir: Path):
    """创建业务逻辑模块"""
    business_dir = base_dir / "src" / "business"
    business_dir.mkdir(parents=True, exist_ok=True)
    
    logic_code = '''/**
 * 业务逻辑模块
 */
import { BaseComplexClass, EventBus, DependencyInjector } from '../core';
import { DataStore, CacheManager } from '../data';
import { APIClient } from '../network';

export interface User {
    id: string;
    name: string;
    email: string;
    avatar?: string;
    bio?: string;
    createdAt: number;
    updatedAt: number;
}

export interface Item {
    id: string;
    title: string;
    description?: string;
    userId: string;
    createdAt: number;
    updatedAt: number;
    tags?: string[];
}

export class UserService extends BaseComplexClass {
    private apiClient: APIClient;
    private dataStore: DataStore;
    private cache: CacheManager;
    private currentUser?: User;
    
    constructor(id: string) {
        super(id);
        this.apiClient = new APIClient('https://api.example.com');
        this.dataStore = new DataStore('user_store', 'user_data');
        this.cache = CacheManager.getInstance();
    }
    
    protected initialize(): void {
        this.loadCurrentUser();
    }
    
    async login(email: string, password: string): Promise<User | null> {
        this.emit('loginStart');
        const response = await this.apiClient.login({ email, password });
        if (response.success) {
            this.currentUser = response.data.user;
            this.dataStore.set('currentUser', this.currentUser);
            this.cache.set('currentUser', this.currentUser);
            this.emit('loginSuccess', this.currentUser);
            return this.currentUser;
        } else {
            this.emit('loginFailed', response.data);
            return null;
        }
    }
    
    async logout(): Promise<void> {
        await this.apiClient.logout();
        this.currentUser = undefined;
        this.dataStore.delete('currentUser');
        this.cache.delete('currentUser');
        this.emit('loggedOut');
    }
    
    async fetchCurrentUser(): Promise<User | null> {
        const cached = this.cache.get<User>('currentUser');
        if (cached) {
            return cached;
        }
        const response = await this.apiClient.getUser();
        if (response.success) {
            this.currentUser = response.data;
            this.cache.set('currentUser', this.currentUser);
            this.dataStore.set('currentUser', this.currentUser);
            return this.currentUser;
        }
        return null;
    }
    
    async updateProfile(data: Partial<User>): Promise<User | null> {
        const response = await this.apiClient.updateUser(data);
        if (response.success) {
            this.currentUser = { ...this.currentUser, ...response.data };
            this.cache.set('currentUser', this.currentUser);
            this.dataStore.set('currentUser', this.currentUser);
            this.emit('profileUpdated', this.currentUser);
            return this.currentUser;
        }
        return null;
    }
    
    private loadCurrentUser(): void {
        const stored = this.dataStore.get<User>('currentUser');
        if (stored) {
            this.currentUser = stored;
            this.cache.set('currentUser', stored);
        }
    }
    
    getCurrentUser(): User | undefined {
        return this.currentUser;
    }
    
    isLoggedIn(): boolean {
        return this.currentUser !== undefined;
    }
}

export class ItemService extends BaseComplexClass {
    private apiClient: APIClient;
    private dataStore: DataStore;
    private cache: CacheManager;
    private items: Item[] = [];
    
    constructor(id: string) {
        super(id);
        this.apiClient = new APIClient('https://api.example.com');
        this.dataStore = new DataStore('item_store', 'item_data');
        this.cache = CacheManager.getInstance();
    }
    
    protected initialize(): void {
        this.loadItems();
    }
    
    async fetchItems(forceRefresh: boolean = false): Promise<Item[]> {
        if (!forceRefresh) {
            const cached = this.cache.get<Item[]>('items');
            if (cached) {
                return cached;
            }
        }
        const response = await this.apiClient.getItems();
        if (response.success) {
            this.items = response.data;
            this.cache.set('items', this.items);
            this.dataStore.set('items', this.items);
            this.emit('itemsFetched', this.items);
            return this.items;
        }
        return [];
    }
    
    async createItem(item: Omit<Item, 'id' | 'createdAt' | 'updatedAt'>): Promise<Item | null> {
        const response = await this.apiClient.createItem(item);
        if (response.success) {
            const newItem = response.data;
            this.items.push(newItem);
            this.cache.set('items', this.items);
            this.dataStore.set('items', this.items);
            this.emit('itemCreated', newItem);
            return newItem;
        }
        return null;
    }
    
    async updateItem(id: string, data: Partial<Item>): Promise<Item | null> {
        const response = await this.apiClient.updateItem(id, data);
        if (response.success) {
            const updatedItem = response.data;
            const index = this.items.findIndex(item => item.id === id);
            if (index !== -1) {
                this.items[index] = updatedItem;
            }
            this.cache.set('items', this.items);
            this.dataStore.set('items', this.items);
            this.emit('itemUpdated', updatedItem);
            return updatedItem;
        }
        return null;
    }
    
    async deleteItem(id: string): Promise<boolean> {
        const response = await this.apiClient.deleteItem(id);
        if (response.success) {
            this.items = this.items.filter(item => item.id !== id);
            this.cache.set('items', this.items);
            this.dataStore.set('items', this.items);
            this.emit('itemDeleted', id);
            return true;
        }
        return false;
    }
    
    private loadItems(): void {
        const stored = this.dataStore.get<Item[]>('items', []);
        this.items = stored;
    }
    
    getItems(): Item[] {
        return [...this.items];
    }
    
    getItemById(id: string): Item | undefined {
        return this.items.find(item => item.id === id);
    }
}

export class NotificationService extends BaseComplexClass {
    private notifications: any[] = [];
    private unreadCount: number = 0;
    
    constructor(id: string) {
        super(id);
    }
    
    protected initialize(): void {
    }
    
    addNotification(notification: any): void {
        this.notifications.unshift({
            ...notification,
            id: Date.now().toString(),
            timestamp: Date.now(),
            read: false
        });
        this.unreadCount++;
        this.emit('notificationAdded', notification);
    }
    
    markAsRead(id: string): void {
        const notification = this.notifications.find(n => n.id === id);
        if (notification && !notification.read) {
            notification.read = true;
            this.unreadCount--;
            this.emit('notificationRead', id);
        }
    }
    
    markAllAsRead(): void {
        this.notifications.forEach(n => {
            n.read = true;
        });
        this.unreadCount = 0;
        this.emit('allNotificationsRead');
    }
    
    removeNotification(id: string): void {
        const index = this.notifications.findIndex(n => n.id === id);
        if (index !== -1) {
            const notification = this.notifications[index];
            if (!notification.read) {
                this.unreadCount--;
            }
            this.notifications.splice(index, 1);
            this.emit('notificationRemoved', id);
        }
    }
    
    clearAll(): void {
        this.notifications = [];
        this.unreadCount = 0;
        this.emit('notificationsCleared');
    }
    
    getNotifications(): any[] {
        return [...this.notifications];
    }
    
    getUnreadCount(): number {
        return this.unreadCount;
    }
}
'''
    
    with open(business_dir / "BusinessLogic.ets", 'w', encoding='utf-8') as f:
        f.write(logic_code)


def create_test_module(base_dir: Path):
    """创建测试模块"""
    test_dir = base_dir / "src" / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_code = '''/**
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
        
        console.log('\\n=== LinkedList 测试 ===');
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
        
        console.log('\\n=== Queue 测试 ===');
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
        
        console.log('\\n=== Stack 测试 ===');
        runner.test('Stack.push', () => {
            const stack = new Stack<number>();
            stack.push(1);
            stack.push(2);
            if (stack.size !== 2) throw new Error('大小应为 2');
        });
        
        console.log('\\n=== HashMap 测试 ===');
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
        
        console.log('\\n=== Tree 测试 ===');
        runner.test('Tree.addChild', () => {
            const tree = new Tree<number>(1);
            tree.addChild(2);
            tree.addChild(3);
            if (tree.children.length !== 2) throw new Error('子节点应为 2');
        });
        
        const results = runner.getResults();
        console.log(`\\n=== 测试结果 ===');
        console.log(`✅ 通过: ${results.passed}');
        console.log(`❌ 失败: ${results.failed}');
        if (results.errors.forEach(error => {
            console.error(error);
        });
    }
}

export class PerformanceTests {
    static run(): void {
        console.log('\\n=== 性能测试 ===');
        
        const iterations = 10000;
        
        console.log('LinkedList 性能:');
        const listStart = Date.now();
        const list = new LinkedList<number>();
        for (let i = 0; i < iterations; i++) {
            list.addLast(i);
        }
        const listEnd = Date.now();
        console.log(`  ${iterations} 次 addLast 耗时: ${listEnd - listStart}ms');
        
        console.log('\\nHashMap 性能:');
        const mapStart = Date.now();
        const map = new HashMap<string, number>();
        for (let i = 0; i < iterations; i++) {
            map.set(`key_${i}`, i);
        }
        const mapEnd = Date.now();
        console.log(`  ${iterations} 次 set 耗时: ${mapEnd - mapStart}ms');
        
        console.log('\\nQueue 性能:');
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
    console.log('\\n🎉 所有测试完成！');
}
'''
    
    with open(test_dir / "Tests.ets", 'w', encoding='utf-8') as f:
        f.write(test_code)


def create_utils_module(base_dir: Path):
    """创建工具模块"""
    utils_dir = base_dir / "src" / "utils"
    utils_dir.mkdir(parents=True, exist_ok=True)
    
    utils_code = '''/**
 * 工具模块
 */

export function deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    if (obj instanceof Date) {
        return new Date(obj.getTime()) as T;
    }
    if (obj instanceof Array) {
        return obj.map(item => deepClone(item)) as T;
    }
    if (obj instanceof Set) {
        const result = new Set();
        obj.forEach(item => result.add(deepClone(item)));
        return result as T;
    }
    if (obj instanceof Map) {
        const result = new Map();
        obj.forEach((value, key) => result.set(deepClone(key), deepClone(value)));
        return result as T;
    }
    const result: any = {};
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            result[key] = deepClone(obj[key]);
        }
    }
    return result;
}

export function debounce<T extends (...args: any[]) => any>(func: T, wait: number): (...args: Parameters<T>) => void {
    let timeoutId: number | null = null;
    return function (this: any, ...args: Parameters<T>) {
        if (timeoutId !== null) {
            clearTimeout(timeoutId);
        }
        timeoutId = setTimeout(() => {
            func.apply(this, args);
            timeoutId = null;
        }, wait);
    };
}

export function throttle<T extends (...args: any[]) => any>(func: T, wait: number): (...args: Parameters<T>) => void {
    let lastCall = 0;
    return function (this: any, ...args: Parameters<T>) {
        const now = Date.now();
        if (now - lastCall >= wait) {
            lastCall = now;
            func.apply(this, args);
        }
    };
}

export function formatDate(timestamp: number, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
    const date = new Date(timestamp);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return format
        .replace('YYYY', String(year))
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}

export function uuid(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

export function generateId(): string {
    return `${Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

export function isValidEmail(email: string): boolean {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

export function isValidPhoneNumber(phone: string): boolean {
    const regex = /^1[3-9]\d{9}$/;
    return regex.test(phone);
}

export function isEmpty(value: any): boolean {
    if (value === null || value === undefined) {
        return true;
    }
    if (typeof value === 'string' && value.trim() === '') {
        return true;
    }
    if (Array.isArray(value) && value.length === 0) {
        return true;
    }
    if (typeof value === 'object' && Object.keys(value).length === 0) {
        return true;
    }
    return false;
}

export function chunk<T>(array: T[], size: number): T[][] {
    const result: T[][] = [];
    for (let i = 0; i < array.length; i += size) {
        result.push(array.slice(i, i + size));
    }
    return result;
}

export function unique<T>(array: T[]): T[] {
    return [...new Set(array)];
}

export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
    return array.reduce((result, item) => {
        const groupKey = String(item[key]);
        if (!result[groupKey]) {
            result[groupKey] = [];
        }
        result[groupKey].push(item);
        return result;
    }, {} as Record<string, T[]>);
}

export class Logger {
    private static instance: Logger;
    private prefix: string;
    private enabled: boolean = true;
    
    private constructor(prefix: string = 'App') {
        this.prefix = prefix;
    }
    
    static getInstance(prefix?: string): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger(prefix);
        }
        return Logger.instance;
    }
    
    info(...args: any[]): void {
        if (this.enabled) {
            console.log(`[${this.prefix}] [INFO]', ...args);
        }
    }
    
    warn(...args: any[]): void {
        if (this.enabled) {
            console.warn(`[${this.prefix}] [WARN]', ...args);
        }
    }
    
    error(...args: any[]): void {
        if (this.enabled) {
            console.error(`[${this.prefix}] [ERROR]', ...args);
        }
    }
    
    debug(...args: any[]): void {
        if (this.enabled) {
            console.debug(`[${this.prefix}] [DEBUG]', ...args);
        }
    }
    
    setEnabled(enabled: boolean): void {
        this.enabled = enabled;
    }
}

export class Timer {
    private startTime: number = 0;
    private laps: { name: string; time: number }[] = [];
    
    start(): void {
        this.startTime = Date.now();
        this.laps = [];
    }
    
    lap(name: string): void {
        this.laps.push({
            name,
            time: Date.now() - this.startTime
        });
    }
    
    stop(): number {
        return Date.now() - this.startTime;
    }
    
    getLaps(): { name: string; time: number }[] {
        return [...this.laps;
    }
    
    getTotalTime(): number {
        return this.laps.length > 0 ? this.laps[this.laps.length - 1].time : 0;
    }
    
    printReport(): void {
        console.log('计时报告:');
        this.laps.forEach(lap => {
            console.log(`  ${lap.name}: ${lap.time}ms');
        });
        console.log(`  总计: ${this.getTotalTime()}ms`);
    }
}
'''
    
    with open(utils_dir / "Utils.ets", 'w', encoding='utf-8') as f:
        f.write(utils_code)
    
    # 入口文件
    index_code = '''/**
 * 项目入口
 */
import { MainPage } from './ui/Buttons';
import { UserService, ItemService, NotificationService } from './business/BusinessLogic';
import { Logger } from './utils/Utils';

@Entry
@Component
struct App {
    private userService: UserService = new UserService('user_service');
    private itemService: ItemService = new ItemService('item_service');
    private notificationService: NotificationService = new NotificationService('notification_service');
    private logger: Logger = Logger.getInstance('App');
    
    aboutToAppear() {
        this.logger.info('应用启动');
        this.userService.on('loginSuccess', (user) => {
            this.logger.info('用户登录:', user.name);
            this.notificationService.addNotification({
                title: '欢迎回来',
                message: `欢迎 ${user.name} 回来！'
            });
        });
    }
    
    build() {
        MainPage();
    }
}
'''
    
    with open(base_dir / "src" / "main.ets", 'w', encoding='utf-8') as f:
        f.write(index_code)


if __name__ == "__main__":
    print('开始创建超复杂测试项目...')
    create_ultra_complex_test_project()
    print('完成！')

