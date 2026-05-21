// 主入口
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
