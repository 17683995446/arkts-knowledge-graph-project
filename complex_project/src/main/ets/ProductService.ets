
// ProductService.ets - 产品服务
import { TestUtils } from './TestUtils';
import { UserManager } from './UserManager';

export interface Product {
    id: number;
    name: string;
    price: number;
    stock: number;
}

export class ProductService {
    private products: Product[] = [];
    private nextProductId: number = 1;
    
    constructor() {
        TestUtils.log('ProductService initialized');
    }
    
    addProduct(name: string, price: number, stock: number): Product {
        const product: Product = {
            id: this.nextProductId++,
            name: name,
            price: price,
            stock: stock
        };
        this.products.push(product);
        TestUtils.log(`Added product: ${name}, price: $${price}`);
        return product;
    }
    
    getProductById(id: number): Product | null {
        return this.products.find(product =&gt; product.id === id) || null;
    }
    
    getAllProducts(): Product[] {
        return [...this.products];
    }
    
    updateStock(id: number, quantity: number): boolean {
        const product = this.getProductById(id);
        if (product) {
            product.stock += quantity;
            TestUtils.log(`Updated stock for ${product.name}: ${product.stock}`);
            return true;
        }
        return false;
    }
    
    checkAvailability(productId: number, quantity: number): boolean {
        const product = this.getProductById(productId);
        return product ? product.stock &gt;= quantity : false;
    }
}

export class Order {
    id: number;
    userId: number;
    items: {
        productId: number;
        quantity: number;
    }[];
    total: number;
    createdAt: number;
    
    constructor(id: number, userId: number) {
        this.id = id;
        this.userId = userId;
        this.items = [];
        this.total = 0;
        this.createdAt = Date.now();
    }
    
    addItem(productId: number, quantity: number, price: number): void {
        this.items.push({ productId, quantity });
        this.total += quantity * price;
    }
}
