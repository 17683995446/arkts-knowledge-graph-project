/**
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
