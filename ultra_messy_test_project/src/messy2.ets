/*
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
