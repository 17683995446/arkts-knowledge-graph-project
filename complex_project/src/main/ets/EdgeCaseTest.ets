
// EdgeCaseTest.ets - 边界情况测试
@Entry
@Component
struct EdgeCaseTest {
    // 空字符串和特殊字符
    private emptyString: string = "";
    private specialChars: string = "你好世界🎉<>\"'&";
    private unicode: string = "Unicode: \u0041\u0042\u0043 中文测试";
    private regex: string = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}";

    // 数字边界值
    private maxInt: number = Number.MAX_SAFE_INTEGER;
    private minInt: number = Number.MIN_SAFE_INTEGER;
    private positiveInfinity: number = Infinity;
    private negativeInfinity: number = -Infinity;
    private nan: number = NaN;
    private zero: number = 0;
    private negativeZero: number = -0;

    // 数组边界
    private emptyArray: number[] = [];
    private singleElement: number[] = [1];
    private largeArray: number[] = Array(10000).fill(0).map((_, i) => i);
    private sparseArray: (number | undefined)[] = [];
    sparseArray[0] = 1;
    sparseArray[1000] = 2;

    // 对象边界
    private emptyObject: object = {};
    private nestedObject: object = {
        level1: {
            level2: {
                level3: {
                    value: "deep"
                }
            }
        }
    };

    // null 和 undefined
    private nullValue: string | null = null;
    private undefinedValue: string | undefined = undefined;

    // 函数引用
    private funcRef: (() => void) | null = null;
    private arrowFunc: () => string = () => "arrow";

    build() {
        Column() {
            Text("Edge Cases")
                .fontSize(30)
        }
    }

    aboutToAppear(): void {
        this.testEdgeCases();
    }

    testEdgeCases(): void {
        // 测试空值
        if (this.emptyString === "") {
            console.log("Empty string test passed");
        }

        // 测试特殊字符
        console.log(`Special chars: ${this.specialChars}`);
        console.log(`Unicode: ${this.unicode}`);

        // 测试数字边界
        console.log(`Max Int: ${this.maxInt}`);
        console.log(`Min Int: ${this.minInt}`);
        console.log(`Is NaN: ${isNaN(this.nan)}`);

        // 测试数组
        console.log(`Empty array length: ${this.emptyArray.length}`);
        console.log(`Large array length: ${this.largeArray.length}`);
        console.log(`Sparse array length: ${this.sparseArray.length}`);

        // 测试对象
        console.log(`Empty object keys: ${Object.keys(this.emptyObject).length}`);
        console.log(`Nested object: ${JSON.stringify(this.nestedObject)}`);

        // 测试 null/undefined
        console.log(`Null value: ${this.nullValue}`);
        console.log(`Undefined value: ${this.undefinedValue}`);

        // 测试函数
        if (this.funcRef === null) {
            console.log("Function ref is null");
        }
        console.log(`Arrow function: ${this.arrowFunc()}`);

        // 深度嵌套调用
        this.deepNestedCall(10);

        // 递归测试
        console.log(`Fibonacci(20): ${this.fibonacci(20)}`);

        // 循环引用
        const circular: any = { name: "test" };
        circular.self = circular;

        // try-catch 测试
        try {
            throw new Error("Test error");
        } catch (e) {
            console.log(`Caught error: ${e}`);
        }
    }

    deepNestedCall(depth: number): void {
        if (depth <= 0) {
            return;
        }
        this.processLevel(depth);
        this.deepNestedCall(depth - 1);
    }

    processLevel(level: number): void {
        console.log(`Processing level ${level}`);
    }

    fibonacci(n: number): number {
        if (n <= 1) return n;
        return this.fibonacci(n - 1) + this.fibonacci(n - 2);
    }
}
