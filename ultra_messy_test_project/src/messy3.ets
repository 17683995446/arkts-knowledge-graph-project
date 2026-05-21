/**
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
