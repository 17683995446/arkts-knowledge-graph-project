/**
 * 文件4 - 类型声明地狱
 */
interface User {
  id: string;
  name: string;
  email: string;
}

interface Product {
  id: number;
  name: string;
  price: number;
  category: Category;
}

interface Category {
  id: string;
  name: string;
}

interface Order {
  id: string;
  user: User;
  products: Product[];
  total: number;
  status: OrderStatus;
}

enum OrderStatus {
  PENDING,
  SHIPPED,
  DELIVERED
}

class OrderProcessor {
  processOrder(order: Order) {
    this.validateOrder(order);
    this.calculateTotal(order);
    this.updateStatus(order, OrderStatus.SHIPPED);
    this.notifyUser(order.user);
  }
  
  validateOrder(order: Order) {
    if (!order.products.length) {
      throw new Error("No products");
    }
  }
  
  calculateTotal(order: Order) {
    order.total = order.products.reduce((sum, p) => sum + p.price, 0);
  }
  
  updateStatus(order: Order, status: OrderStatus) {
    order.status = status;
  }
  
  notifyUser(user: User) {
    console.log("Notifying", user.email);
  }
}

@Component
struct OrderComponent {
  @State orders: Order[] = [];
  
  build() {
    Column() {
      Text("Orders: " + this.orders.length)
    }
  }
}
