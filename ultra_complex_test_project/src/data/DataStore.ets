/**
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
