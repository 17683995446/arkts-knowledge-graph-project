/**
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
