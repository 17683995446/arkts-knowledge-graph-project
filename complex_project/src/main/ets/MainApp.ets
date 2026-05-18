
// MainApp.ets - 主应用入口
import { TestUtils } from './TestUtils';
import { UserManager, User } from './UserManager';
import { ProductService, Product, Order } from './ProductService';

@Entry
@Component
struct MainApp {
    @State message: string = 'Hello World';
    @State products: Product[] = [];
    @State users: User[] = [];
    @State totalSales: number = 0;
    
    private userManager: UserManager = new UserManager();
    private productService: ProductService = new ProductService();
    private nextOrderId: number = 1;
    
    build() {
        Column() {
            Text(this.message)
                .fontSize(30)
                .fontWeight(FontWeight.Bold)
                .margin({ bottom: 20 });
            
            Button('Initialize Demo')
                .onClick(() =&gt; {
                    this.initializeDemo();
                })
                .margin({ bottom: 10 });
            
            Text(`Total Sales: $${TestUtils.formatNumber(this.totalSales)}`)
                .fontSize(20)
                .fontColor(Color.Blue)
                .margin({ bottom: 20 });
            
            Text('Products:')
                .fontSize(20)
                .fontWeight(FontWeight.Bold)
                .margin({ bottom: 10 });
            
            ForEach(this.products, (product: Product) =&gt; {
                Row() {
                    Text(`${product.name}: $${product.price}, Stock: ${product.stock}`)
                        .fontSize(16);
                }
                .margin({ bottom: 5 });
            });
        }
        .padding(20)
        .width('100%')
        .height('100%');
    }
    
    aboutToAppear(): void {
        TestUtils.log('MainApp about to appear');
    }
    
    initializeDemo(): void {
        TestUtils.log('Initializing demo...');
        
        // Add users
        const alice = this.userManager.addUser('Alice', 'alice@example.com');
        const bob = this.userManager.addUser('Bob', 'bob@example.com');
        const charlie = this.userManager.addUser('Charlie', 'charlie@example.com');
        
        // Add products
        const laptop = this.productService.addProduct('Laptop', 999.99, 10);
        const phone = this.productService.addProduct('Phone', 699.99, 25);
        const tablet = this.productService.addProduct('Tablet', 299.99, 15);
        
        // Update state
        this.products = this.productService.getAllProducts();
        this.users = this.userManager.getAllUsers();
        
        // Create some orders
        this.createOrder(alice.id, [
            { productId: laptop.id, quantity: 1 },
            { productId: phone.id, quantity: 2 }
        ]);
        
        this.createOrder(bob.id, [
            { productId: tablet.id, quantity: 3 }
        ]);
        
        this.createOrder(charlie.id, [
            { productId: laptop.id, quantity: 2 },
            { productId: tablet.id, quantity: 1 }
        ]);
        
        this.message = 'Demo Initialized!';
        TestUtils.log('Demo initialization complete');
    }
    
    createOrder(userId: number, items: { productId: number; quantity: number }[]): boolean {
        TestUtils.log(`Creating order for user ${userId}`);
        
        // Check availability first
        for (const item of items) {
            if (!this.productService.checkAvailability(item.productId, item.quantity)) {
                TestUtils.log(`Product ${item.productId} not available in quantity ${item.quantity}`);
                return false;
            }
        }
        
        // Create order
        const order = new Order(this.nextOrderId++, userId);
        
        let orderTotal = 0;
        for (const item of items) {
            const product = this.productService.getProductById(item.productId);
            if (product) {
                order.addItem(item.productId, item.quantity, product.price);
                orderTotal += item.quantity * product.price;
                this.productService.updateStock(item.productId, -item.quantity);
            }
        }
        
        this.totalSales += orderTotal;
        this.products = this.productService.getAllProducts();
        
        TestUtils.log(`Order created successfully, total: $${orderTotal}`);
        return true;
    }
}
