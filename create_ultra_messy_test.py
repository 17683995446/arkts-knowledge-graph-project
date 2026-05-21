#!/usr/bin/env python3
"""
创建超级混乱、复杂、高难度的测试场景 - 慢工出细活
包含各种边界情况、错误格式、混乱代码，用于测试系统健壮性
"""
import os

def create_messy_files():
    test_dir = "ultra_messy_test_project/src"
    os.makedirs(test_dir, exist_ok=True)
    os.makedirs(test_dir + "/utils", exist_ok=True)
    os.makedirs(test_dir + "/components", exist_ok=True)
    os.makedirs(test_dir + "/api", exist_ok=True)
    
    print("🔥 创建超级混乱的测试项目...")
    
    # 文件1: 包含各种混乱代码
    with open(test_dir + "/messy1.ets", "w") as f:
        f.write('''/**
 * 超级混乱的测试文件 - 包含各种错误格式、混合注释、嵌套
 */
import { SomeType } from './some-module'
import { AnotherType, ThirdType } from './another-module'
// 行内注释

@Entry
@Component
/* 多行注释 */
struct MessyComponent {
  // 各种属性
  private state1: string = "hello"
  public state2: number = 42;
  protected state3: boolean = true
  
  @State
  messyState: string = "test"
  
  // 方法定义 - 混乱格式
  aboutToAppear() {
    console.log("about to appear")
    this.initStuff()
  }
  
  initStuff() {
    let x = 10;
    let y = "test"
    this.doSomething(x, y);
  }
  
  private doSomething(a: number, b: string) {
    console.log("doing something", a, b)
  }
  
  build() {
    Column() {
      Text("Hello Messy World")
    }
  }
}

// 嵌套类
export class NestedClass {
  constructor() {
    this.init()
  }
  
  init() {
    console.log("init")
  }
}

export interface MessyInterface {
  name: string;
  value: number;
}

export enum MessyEnum {
  Option1,
  Option2,
  Option3
}

function standaloneFunc(x: number) {
  return x * 2;
}

async function asyncFunc() {
  await new Promise(resolve => setTimeout(resolve, 100))
}
''')
        
    # 文件2: 包含各种格式错误和混乱的注释
    with open(test_dir + "/messy2.ets", "w") as f:
        f.write('''/*
 * 文件2 - 更多混乱
 * 包含格式错误、未闭合括号、嵌套调用等
 */
export class ComplexUtils {
  static calculate(a: number, b: number): number {
    return (a + b) * (a - b) / 2
  }
  
  formatString(input: string): string {
    if (!input) {
      return "";
    }
    return input.trim().toUpperCase()
  }
  
  static async fetchData(url: string): Promise<any> {
    try {
      const response = await fetch(url)
      return await response.json()
    } catch (e) {
      console.error("Error fetching", e)
      return null
    }
  }
}

@Component
struct AnotherComponent {
  @State count: number = 0;
  
  increment() {
    this.count++;
  }
  
  build() {
    Column() {
      Text("Count: " + this.count)
        .onClick(() => {
          this.increment();
          ComplexUtils.calculate(this.count, 2);
        })
    }
  }
}

/* 未闭合的类 - 混乱测试
export class BrokenClass {
  doSomething() {
    // 未闭合
*/

export class WorkingClass {
  doWork() {
    console.log("working...");
  }
}
''')
        
    # 文件3: 极复杂的调用链和嵌套
    with open(test_dir + "/messy3.ets", "w") as f:
        f.write('''/**
 * 文件3 - 极复杂的调用链
 */
import { ComplexUtils } from './messy2'
import { NestedClass } from './messy1'

@Entry
@Component
struct ComplexApp {
  aboutToAppear() {
    const util = new ComplexUtil();
    util.initialize();
    util.processData("test", 42);
  }
  
  build() {
    Column() {
      Text("Complex App")
    }
  }
}

class ComplexUtil {
  private nested: NestedClass;
  
  constructor() {
    this.nested = new NestedClass();
  }
  
  initialize() {
    this.setupLogging();
    this.configureSettings();
    this.nested.init();
  }
  
  setupLogging() {
    console.log("logging setup");
    this.logInfo("started");
  }
  
  configureSettings() {
    console.log("configuring");
  }
  
  logInfo(msg: string) {
    console.info(msg);
  }
  
  processData(input: string, value: number) {
    const formatted = this.formatInput(input);
    const calculated = this.calculate(formatted, value);
    this.validate(calculated);
    return calculated;
  }
  
  formatInput(input: string) {
    return input.toUpperCase();
  }
  
  calculate(a: string, b: number) {
    return a.length + b;
  }
  
  validate(result: number) {
    if (result <= 0) {
      throw new Error("Invalid result");
    }
  }
}
''')
        
    # 文件4: 包含大量类型声明和接口
    with open(test_dir + "/messy4.ets", "w") as f:
        f.write('''/**
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
''')
        
    # 文件5: 超复杂的工具类
    with open(test_dir + "/utils/messy_utils.ets", "w") as f:
        f.write('''// 工具类 - 超多方法
export class SuperUtils {
  static add(a: number, b: number) { return a + b; }
  static subtract(a: number, b: number) { return a - b; }
  static multiply(a: number, b: number) { return a * b; }
  static divide(a: number, b: number) { return b ? a / b : 0; }
  
  static stringToNumber(s: string) { return parseInt(s); }
  static numberToString(n: number) { return n.toString(); }
  
  static arraySum(arr: number[]) {
    return arr.reduce((sum, n) => sum + n, 0);
  }
  
  static arrayAverage(arr: number[]) {
    return this.arraySum(arr) / arr.length;
  }
  
  static arrayMax(arr: number[]) {
    return Math.max(...arr);
  }
  
  static arrayMin(arr: number[]) {
    return Math.min(...arr);
  }
  
  static capitalize(s: string) {
    return s.charAt(0).toUpperCase() + s.slice(1);
  }
  
  static truncate(s: string, max: number) {
    return s.length > max ? s.slice(0, max) + '...' : s;
  }
  
  static isEmpty(s: string | null | undefined) {
    return !s || s.trim() === '';
  }
  
  static formatDate(date: Date) {
    return date.toISOString().split('T')[0];
  }
  
  static parseDate(dateStr: string) {
    return new Date(dateStr);
  }
  
  static random(min: number, max: number) {
    return Math.random() * (max - min) + min;
  }
  
  static randomInt(min: number, max: number) {
    return Math.floor(this.random(min, max));
  }
}

export class StringUtils {
  static reverse(s: string) {
    return s.split('').reverse().join('');
  }
  
  static countOccurrences(s: string, search: string) {
    return (s.match(new RegExp(search, 'g')) || []).length;
  }
  
  static replaceAll(s: string, search: string, replace: string) {
    return s.split(search).join(replace);
  }
}

@Component
struct UtilsComponent {
  build() {
    Column() {
      Text("Utils Component")
    }
  }
}
''')
        
    # 文件6: 组件地狱
    with open(test_dir + "/components/messy_components.ets", "w") as f:
        f.write('''// 超多组件
@Component
struct ButtonComponent {
  label: string = "Click";
  onClick?: () => void;
  
  build() {
    Button(this.label)
      .onClick(() => {
        if (this.onClick) {
          this.onClick();
        }
      })
  }
}

@Component
struct InputComponent {
  value: string = "";
  onChange?: (value: string) => void;
  
  build() {
    TextInput({ text: this.value })
      .onChange((value: string) => {
        if (this.onChange) {
          this.onChange(value);
        }
      })
  }
}

@Component
struct CardComponent {
  title: string = "";
  content: string = "";
  
  build() {
    Column() {
      Text(this.title).fontSize(18)
      Text(this.content).fontSize(14)
    }.padding(16)
  }
}

@Component
struct ListComponent {
  items: string[] = [];
  
  build() {
    List() {
      ForEach(this.items, (item: string) => {
        ListItem() {
          Text(item)
        }
      })
    }
  }
}

@Component
struct FormComponent {
  @State name: string = "";
  @State email: string = "";
  
  build() {
    Column() {
      InputComponent({
        value: this.name,
        onChange: (v) => this.name = v
      })
      InputComponent({
        value: this.email,
        onChange: (v) => this.email = v
      })
      ButtonComponent({
        label: "Submit",
        onClick: () => {
          console.log("Submit", this.name, this.email);
        }
      })
    }
  }
}

@Entry
@Component
struct MainComponent {
  build() {
    Column() {
      CardComponent({ title: "Welcome", content: "Hello!" })
      FormComponent()
    }
  }
}
''')
        
    # 文件7: API相关混乱代码
    with open(test_dir + "/api/messy_api.ets", "w") as f:
        f.write('''// API 相关
export interface ApiRequest {
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  success: boolean;
}

export class HttpClient {
  async request<T>(request: ApiRequest): Promise<ApiResponse<T>> {
    try {
      const response = await this.execute(request);
      return {
        data: response,
        status: 200,
        success: true
      };
    } catch (error) {
      return {
        data: null,
        status: 500,
        success: false
      };
    }
  }
  
  private async execute(request: ApiRequest): Promise<any> {
    console.log("Executing", request.method, request.url);
    return { result: "success" };
  }
  
  get<T>(url: string) {
    return this.request<T>({ url, method: 'GET' });
  }
  
  post<T>(url: string, data: any) {
    return this.request<T>({ url, method: 'POST', data });
  }
}

export class UserApi {
  constructor(private http: HttpClient) { }
  
  async getUsers() {
    return this.http.get('/users');
  }
  
  async getUser(id: string) {
    return this.http.get('/users/' + id);
  }
}

export class ProductApi {
  constructor(private http: HttpClient) { }
  
  async getProducts() {
    return this.http.get('/products');
  }
  
  async createProduct(data: any) {
    return this.http.post('/products', data);
  }
}

@Component
struct ApiTestComponent {
  private http: HttpClient = new HttpClient();
  private userApi: UserApi = new UserApi(this.http);
  
  aboutToAppear() {
    this.loadData();
  }
  
  async loadData() {
    const response = await this.userApi.getUsers();
    console.log("Users", response);
  }
  
  build() {
    Column() {
      Text("API Test")
    }
  }
}
''')
        
    # 文件8: 主入口
    with open(test_dir + "/messy_main.ets", "w") as f:
        f.write('''// 主入口
import { MainComponent } from './components/messy_components'
import { SuperUtils } from './utils/messy_utils'
import { HttpClient, UserApi } from './api/messy_api'
import { OrderProcessor } from './messy4'
import { ComplexUtils } from './messy2'

@Entry
@Component
struct MessyApp {
  aboutToAppear() {
    console.log("App started");
    this.initEverything();
  }
  
  initEverything() {
    const utilsResult = SuperUtils.add(1, 2);
    console.log("Utils", utilsResult);
    
    const http = new HttpClient();
    const userApi = new UserApi(http);
    
    const processor = new OrderProcessor();
    
    const calc = ComplexUtils.calculate(10, 5);
    console.log("Calc", calc);
  }
  
  build() {
    Column() {
      MainComponent()
    }
  }
}

// 独立函数
function testFunction(x: number, y: number) {
  return SuperUtils.multiply(x, y);
}

async function testAsync() {
  const http = new HttpClient();
  const result = await http.get('/test');
  return result;
}
''')
        
    # 创建一些边界情况的文件
    # 空文件
    with open(test_dir + "/empty.ets", "w") as f:
        f.write("")
        
    # 只有注释的文件
    with open(test_dir + "/only_comments.ets", "w") as f:
        f.write('''// 只有注释
/* 多行注释
这里也是注释
*/
// 结束
''')
        
    # 只有导入的文件
    with open(test_dir + "/only_imports.ets", "w") as f:
        f.write('''import { A } from './a'
import { B } from './b'
import { C, D } from './c'
''')
        
    print("✅ 超级混乱的测试项目创建完成！")
    print("📁 项目路径: " + test_dir)
    print("📄 包含12个文件，包含各种混乱情况、边界情况和错误格式!")

if __name__ == "__main__":
    create_messy_files()
