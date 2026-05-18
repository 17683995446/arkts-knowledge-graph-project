
// LargeScaleTest.ets - 大规模测试（1000+ 行代码）
// 模拟真实的企业级应用

// ============================================================================
// 模块 1: 数据模型
// ============================================================================

export interface User {
    id: number;
    username: string;
    email: string;
    profile: UserProfile;
    roles: Role[];
    permissions: Permission[];
    createdAt: Date;
    updatedAt: Date;
}

export interface UserProfile {
    firstName: string;
    lastName: string;
    phone?: string;
    avatar?: string;
    bio?: string;
    location?: string;
    website?: string;
}

export interface Role {
    id: number;
    name: string;
    description: string;
    level: number;
}

export interface Permission {
    id: number;
    resource: string;
    action: 'read' | 'write' | 'delete' | 'admin';
    conditions?: PermissionCondition[];
}

export interface PermissionCondition {
    field: string;
    operator: 'equals' | 'contains' | 'greaterThan' | 'lessThan';
    value: any;
}

export interface Product {
    id: number;
    name: string;
    description: string;
    price: number;
    category: Category;
    tags: string[];
    inventory: Inventory;
    images: ProductImage[];
    variants: ProductVariant[];
    reviews: Review[];
    rating: number;
    salesCount: number;
    createdAt: Date;
    updatedAt: Date;
}

export interface Category {
    id: number;
    name: string;
    parent?: Category;
    children?: Category[];
    level: number;
    path: string;
}

export interface Inventory {
    quantity: number;
    reserved: number;
    available: number;
    warehouse: string;
    lastRestocked: Date;
}

export interface ProductImage {
    url: string;
    alt: string;
    width: number;
    height: number;
    isPrimary: boolean;
}

export interface ProductVariant {
    id: number;
    sku: string;
    attributes: Record<string, string>;
    price: number;
    inventory: number;
}

export interface Review {
    id: number;
    userId: number;
    rating: number;
    title: string;
    content: string;
    helpful: number;
    createdAt: Date;
}

export interface Order {
    id: number;
    orderNumber: string;
    customer: User;
    items: OrderItem[];
    subtotal: number;
    tax: number;
    shipping: number;
    discount: number;
    total: number;
    status: OrderStatus;
    shippingAddress: Address;
    billingAddress: Address;
    paymentMethod: PaymentMethod;
    notes?: string;
    createdAt: Date;
    updatedAt: Date;
}

export interface OrderItem {
    productId: number;
    productName: string;
    variantId?: number;
    quantity: number;
    unitPrice: number;
    totalPrice: number;
    discount: number;
}

export interface OrderStatus {
    code: string;
    name: string;
    description: string;
    isCompleted: boolean;
}

export interface Address {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
    isDefault: boolean;
}

export interface PaymentMethod {
    type: 'credit_card' | 'debit_card' | 'paypal' | 'bank_transfer';
    last4?: string;
    expiryMonth?: number;
    expiryYear?: number;
    isDefault: boolean;
}

// ============================================================================
// 模块 2: 服务层
// ============================================================================

class UserService {
    private users: Map<number, User> = new Map();
    private emailIndex: Map<string, number> = new Map();

    createUser(data: Partial<User>): User {
        const user: User = {
            id: this.generateId(),
            username: data.username || '',
            email: data.email || '',
            profile: data.profile || {
                firstName: '',
                lastName: ''
            },
            roles: data.roles || [],
            permissions: data.permissions || [],
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.users.set(user.id, user);
        this.emailIndex.set(user.email.toLowerCase(), user.id);
        return user;
    }

    getUserById(id: number): User | undefined {
        return this.users.get(id);
    }

    getUserByEmail(email: string): User | undefined {
        const id = this.emailIndex.get(email.toLowerCase());
        return id ? this.users.get(id) : undefined;
    }

    updateUser(id: number, data: Partial<User>): User | undefined {
        const user = this.users.get(id);
        if (!user) return undefined;
        
        const updated = {
            ...user,
            ...data,
            id: user.id,
            createdAt: user.createdAt,
            updatedAt: new Date()
        };
        this.users.set(id, updated);
        return updated;
    }

    deleteUser(id: number): boolean {
        const user = this.users.get(id);
        if (!user) return false;
        this.emailIndex.delete(user.email.toLowerCase());
        return this.users.delete(id);
    }

    searchUsers(query: string): User[] {
        const results: User[] = [];
        const lowerQuery = query.toLowerCase();
        
        this.users.forEach(user => {
            if (user.username.toLowerCase().includes(lowerQuery) ||
                user.email.toLowerCase().includes(lowerQuery) ||
                user.profile.firstName.toLowerCase().includes(lowerQuery) ||
                user.profile.lastName.toLowerCase().includes(lowerQuery)) {
                results.push(user);
            }
        });
        
        return results;
    }

    assignRole(userId: number, role: Role): boolean {
        const user = this.users.get(userId);
        if (!user) return false;
        
        if (!user.roles.find(r => r.id === role.id)) {
            user.roles.push(role);
            this.recalculatePermissions(user);
        }
        return true;
    }

    private recalculatePermissions(user: User): void {
        user.permissions = [];
        user.roles.forEach(role => {
            console.log(`Adding permissions for role: ${role.name}`);
        });
    }

    private generateId(): number {
        return Date.now() + Math.random();
    }
}

class ProductService {
    private products: Map<number, Product> = new Map();
    private categoryIndex: Map<string, Product[]> = new Map();

    createProduct(data: Partial<Product>): Product {
        const product: Product = {
            id: this.generateId(),
            name: data.name || '',
            description: data.description || '',
            price: data.price || 0,
            category: data.category || { id: 0, name: '', level: 0, path: '' },
            tags: data.tags || [],
            inventory: data.inventory || {
                quantity: 0,
                reserved: 0,
                available: 0,
                warehouse: '',
                lastRestocked: new Date()
            },
            images: data.images || [],
            variants: data.variants || [],
            reviews: data.reviews || [],
            rating: data.rating || 0,
            salesCount: data.salesCount || 0,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.products.set(product.id, product);
        return product;
    }

    getProductById(id: number): Product | undefined {
        return this.products.get(id);
    }

    getProductsByCategory(categoryId: number): Product[] {
        const results: Product[] = [];
        this.products.forEach(product => {
            if (product.category.id === categoryId) {
                results.push(product);
            }
        });
        return results;
    }

    searchProducts(query: string): Product[] {
        const results: Product[] = [];
        const lowerQuery = query.toLowerCase();
        
        this.products.forEach(product => {
            if (product.name.toLowerCase().includes(lowerQuery) ||
                product.description.toLowerCase().includes(lowerQuery) ||
                product.tags.some(tag => tag.toLowerCase().includes(lowerQuery))) {
                results.push(product);
            }
        });
        
        return results;
    }

    updateInventory(productId: number, quantity: number): boolean {
        const product = this.products.get(productId);
        if (!product) return false;
        
        product.inventory.quantity += quantity;
        product.inventory.available = product.inventory.quantity - product.inventory.reserved;
        product.inventory.lastRestocked = new Date();
        product.updatedAt = new Date();
        return true;
    }

    addReview(productId: number, review: Review): boolean {
        const product = this.products.get(productId);
        if (!product) return false;
        
        product.reviews.push(review);
        this.recalculateRating(product);
        return true;
    }

    private recalculateRating(product: Product): void {
        if (product.reviews.length === 0) {
            product.rating = 0;
            return;
        }
        
        const sum = product.reviews.reduce((acc, r) => acc + r.rating, 0);
        product.rating = sum / product.reviews.length;
    }

    private generateId(): number {
        return Date.now() + Math.random();
    }
}

class OrderService {
    private orders: Map<number, Order> = new Map();
    private userOrderIndex: Map<number, number[]> = new Map();

    createOrder(data: Partial<Order>): Order {
        const order: Order = {
            id: this.generateId(),
            orderNumber: this.generateOrderNumber(),
            customer: data.customer!,
            items: data.items || [],
            subtotal: data.subtotal || 0,
            tax: data.tax || 0,
            shipping: data.shipping || 0,
            discount: data.discount || 0,
            total: data.total || 0,
            status: data.status || {
                code: 'pending',
                name: 'Pending',
                description: 'Order is pending',
                isCompleted: false
            },
            shippingAddress: data.shippingAddress!,
            billingAddress: data.billingAddress!,
            paymentMethod: data.paymentMethod!,
            notes: data.notes,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        
        this.orders.set(order.id, order);
        
        if (!this.userOrderIndex.has(order.customer.id)) {
            this.userOrderIndex.set(order.customer.id, []);
        }
        this.userOrderIndex.get(order.customer.id)!.push(order.id);
        
        return order;
    }

    getOrderById(id: number): Order | undefined {
        return this.orders.get(id);
    }

    getOrdersByUserId(userId: number): Order[] {
        const orderIds = this.userOrderIndex.get(userId) || [];
        return orderIds.map(id => this.orders.get(id)).filter(o => o !== undefined) as Order[];
    }

    updateOrderStatus(orderId: number, status: OrderStatus): boolean {
        const order = this.orders.get(orderId);
        if (!order) return false;
        
        order.status = status;
        order.updatedAt = new Date();
        return true;
    }

    calculateTotals(order: Order): Order {
        order.subtotal = order.items.reduce((sum, item) => 
            sum + (item.unitPrice * item.quantity - item.discount), 0);
        order.tax = order.subtotal * 0.1;
        order.total = order.subtotal + order.tax + order.shipping - order.discount;
        order.updatedAt = new Date();
        return order;
    }

    private generateOrderNumber(): string {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substring(2, 8);
        return `ORD-${timestamp}-${random}`.toUpperCase();
    }

    private generateId(): number {
        return Date.now() + Math.random();
    }
}

// ============================================================================
// 模块 3: 工具类
// ============================================================================

class Validator {
    static isEmail(email: string): boolean {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    static isPhone(phone: string): boolean {
        const regex = /^\+?[\d\s-()]+$/;
        return regex.test(phone);
    }

    static isUrl(url: string): boolean {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    static isZipCode(zipCode: string): boolean {
        const patterns = [
            /^\d{5}(-\d{4})?$/, // US
            /^[A-Z]\d[A-Z] \d[A-Z]\d$/, // Canada
            /^\d{4,5}$/ // Generic
        ];
        return patterns.some(pattern => pattern.test(zipCode));
    }

    static validatePassword(password: string): ValidationResult {
        const errors: string[] = [];
        
        if (password.length < 8) {
            errors.push('Password must be at least 8 characters');
        }
        if (!/[A-Z]/.test(password)) {
            errors.push('Password must contain at least one uppercase letter');
        }
        if (!/[a-z]/.test(password)) {
            errors.push('Password must contain at least one lowercase letter');
        }
        if (!/\d/.test(password)) {
            errors.push('Password must contain at least one digit');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

interface ValidationResult {
    isValid: boolean;
    errors: string[];
}

class Formatter {
    static formatCurrency(amount: number, currency: string = 'USD'): string {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency
        }).format(amount);
    }

    static formatDate(date: Date, format: string = 'short'): string {
        if (format === 'short') {
            return date.toLocaleDateString();
        } else if (format === 'long') {
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
        return date.toISOString();
    }

    static formatPhone(phone: string): string {
        const cleaned = phone.replace(/\D/g, '');
        if (cleaned.length === 10) {
            return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
        }
        return phone;
    }

    static truncate(text: string, maxLength: number, suffix: string = '...'): string {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - suffix.length) + suffix;
    }
}

class Logger {
    private logs: LogEntry[] = [];
    private maxLogs: number = 1000;

    log(level: LogLevel, message: string, data?: any): void {
        const entry: LogEntry = {
            timestamp: new Date(),
            level,
            message,
            data
        };
        
        this.logs.push(entry);
        
        if (this.logs.length > this.maxLogs) {
            this.logs.shift();
        }
        
        console.log(`[${level}] ${message}`, data || '');
    }

    info(message: string, data?: any): void {
        this.log(LogLevel.INFO, message, data);
    }

    warn(message: string, data?: any): void {
        this.log(LogLevel.WARN, message, data);
    }

    error(message: string, data?: any): void {
        this.log(LogLevel.ERROR, message, data);
    }

    debug(message: string, data?: any): void {
        this.log(LogLevel.DEBUG, message, data);
    }

    getLogs(level?: LogLevel): LogEntry[] {
        if (level) {
            return this.logs.filter(log => log.level === level);
        }
        return [...this.logs];
    }

    clearLogs(): void {
        this.logs = [];
    }
}

enum LogLevel {
    DEBUG,
    INFO,
    WARN,
    ERROR
}

interface LogEntry {
    timestamp: Date;
    level: LogLevel;
    message: string;
    data?: any;
}

class Cache<T> {
    private cache: Map<string, CacheEntry<T>> = new Map();
    private maxSize: number;
    private ttl: number;

    constructor(maxSize: number = 100, ttl: number = 60000) {
        this.maxSize = maxSize;
        this.ttl = ttl;
    }

    set(key: string, value: T): void {
        if (this.cache.size >= this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        
        this.cache.set(key, {
            value,
            expiresAt: Date.now() + this.ttl
        });
    }

    get(key: string): T | undefined {
        const entry = this.cache.get(key);
        
        if (!entry) return undefined;
        
        if (Date.now() > entry.expiresAt) {
            this.cache.delete(key);
            return undefined;
        }
        
        return entry.value;
    }

    has(key: string): boolean {
        return this.get(key) !== undefined;
    }

    delete(key: string): boolean {
        return this.cache.delete(key);
    }

    clear(): void {
        this.cache.clear();
    }
}

interface CacheEntry<T> {
    value: T;
    expiresAt: number;
}

// ============================================================================
// 模块 4: 主应用
// ============================================================================

@Entry
@Component
struct LargeScaleTest {
    @State message: string = 'Large Scale Test';
    
    private userService: UserService = new UserService();
    private productService: ProductService = new ProductService();
    private orderService: OrderService = new OrderService();
    private logger: Logger = new Logger();
    private cache: Cache<any> = new Cache<any>();

    build() {
        Column() {
            Text(this.message)
                .fontSize(30)
        }
        .padding(20)
    }

    aboutToAppear(): void {
        this.runLargeScaleTests();
    }

    runLargeScaleTests(): void {
        this.logger.info('Starting large scale tests');
        
        // 创建大量用户
        this.createBulkUsers(100);
        
        // 创建大量产品
        this.createBulkProducts(200);
        
        // 创建大量订单
        this.createBulkOrders(50);
        
        // 测试搜索功能
        this.testSearch();
        
        // 测试缓存
        this.testCache();
        
        // 测试验证器
        this.testValidators();
        
        // 测试格式化
        this.testFormatters();
        
        this.message = 'Large Scale Tests Complete!';
        this.logger.info('All tests completed');
    }

    private createBulkUsers(count: number): void {
        this.logger.info(`Creating ${count} users`);
        for (let i = 0; i < count; i++) {
            this.userService.createUser({
                username: `user${i}`,
                email: `user${i}@example.com`,
                profile: {
                    firstName: `User`,
                    lastName: `${i}`
                }
            });
        }
        this.logger.info(`Created ${count} users`);
    }

    private createBulkProducts(count: number): void {
        this.logger.info(`Creating ${count} products`);
        for (let i = 0; i < count; i++) {
            this.productService.createProduct({
                name: `Product ${i}`,
                description: `Description for product ${i}`,
                price: Math.random() * 1000,
                category: {
                    id: i % 10,
                    name: `Category ${i % 10}`,
                    level: 1,
                    path: `/category/${i % 10}`
                },
                tags: [`tag${i}`, `tag${i+1}`, `tag${i+2}`],
                inventory: {
                    quantity: Math.floor(Math.random() * 100),
                    reserved: Math.floor(Math.random() * 10),
                    available: Math.floor(Math.random() * 90),
                    warehouse: 'Main',
                    lastRestocked: new Date()
                }
            });
        }
        this.logger.info(`Created ${count} products`);
    }

    private createBulkOrders(count: number): void {
        this.logger.info(`Creating ${count} orders`);
        for (let i = 0; i < count; i++) {
            const user = this.userService.getUserById((i % 100) + 1);
            if (!user) continue;
            
            const order = this.orderService.createOrder({
                customer: user,
                items: [
                    {
                        productId: (i % 200) + 1,
                        productName: `Product ${i}`,
                        quantity: Math.floor(Math.random() * 5) + 1,
                        unitPrice: Math.random() * 100,
                        totalPrice: Math.random() * 500,
                        discount: Math.random() * 50
                    }
                ],
                shippingAddress: {
                    street: `${i} Main St`,
                    city: 'City',
                    state: 'State',
                    zipCode: '12345',
                    country: 'USA',
                    isDefault: true
                },
                billingAddress: {
                    street: `${i} Main St`,
                    city: 'City',
                    state: 'State',
                    zipCode: '12345',
                    country: 'USA',
                    isDefault: true
                },
                paymentMethod: {
                    type: 'credit_card',
                    last4: '1234',
                    expiryMonth: 12,
                    expiryYear: 2025,
                    isDefault: true
                }
            });
            
            this.orderService.calculateTotals(order);
        }
        this.logger.info(`Created ${count} orders`);
    }

    private testSearch(): void {
        this.logger.info('Testing search functionality');
        
        const userResults = this.userService.searchUsers('user50');
        this.logger.info(`Found ${userResults.length} users matching 'user50'`);
        
        const productResults = this.productService.searchProducts('Product 100');
        this.logger.info(`Found ${productResults.length} products matching 'Product 100'`);
    }

    private testCache(): void {
        this.logger.info('Testing cache');
        
        this.cache.set('test1', { data: 'value1' });
        this.cache.set('test2', { data: 'value2' });
        
        const cached1 = this.cache.get('test1');
        const cached2 = this.cache.get('test2');
        const cached3 = this.cache.get('test3');
        
        this.logger.info(`Cache test: test1=${cached1 !== undefined}, test2=${cached2 !== undefined}, test3=${cached3 !== undefined}`);
    }

    private testValidators(): void {
        this.logger.info('Testing validators');
        
        const emailTests = [
            'test@example.com',
            'invalid-email',
            'another@test.org'
        ];
        
        emailTests.forEach(email => {
            const isValid = Validator.isEmail(email);
            this.logger.info(`Email ${email} is ${isValid ? 'valid' : 'invalid'}`);
        });
        
        const passwordResult = Validator.validatePassword('Weak');
        this.logger.info(`Password validation: ${passwordResult.isValid ? 'valid' : 'invalid'}`);
        if (!passwordResult.isValid) {
            this.logger.warn(`Password errors: ${passwordResult.errors.join(', ')}`);
        }
    }

    private testFormatters(): void {
        this.logger.info('Testing formatters');
        
        const currency = Formatter.formatCurrency(1234.56);
        this.logger.info(`Formatted currency: ${currency}`);
        
        const date = Formatter.formatDate(new Date(), 'long');
        this.logger.info(`Formatted date: ${date}`);
        
        const phone = Formatter.formatPhone('1234567890');
        this.logger.info(`Formatted phone: ${phone}`);
        
        const truncated = Formatter.truncate('This is a very long text', 10);
        this.logger.info(`Truncated text: ${truncated}`);
    }
}
