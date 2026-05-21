/**
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
