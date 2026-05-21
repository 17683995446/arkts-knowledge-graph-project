/**
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
