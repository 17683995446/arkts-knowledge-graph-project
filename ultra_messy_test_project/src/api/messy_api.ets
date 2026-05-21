// API 相关
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
