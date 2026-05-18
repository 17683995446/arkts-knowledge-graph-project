
// TestUtils.ets - 工具类
export class TestUtils {
    static logger: Logger = new Logger();
    
    static log(message: string): void {
        this.logger.log(message);
    }
    
    static calculateSum(a: number, b: number): number {
        return a + b;
    }
    
    static formatNumber(num: number): string {
        return num.toString();
    }
}

class Logger {
    log(message: string): void {
        console.log(message);
    }
}
