// 工具类 - 超多方法
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
