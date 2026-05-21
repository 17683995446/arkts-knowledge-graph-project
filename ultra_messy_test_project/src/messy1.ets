/**
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
