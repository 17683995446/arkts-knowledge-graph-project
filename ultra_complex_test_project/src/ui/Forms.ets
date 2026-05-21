/**
 * 复杂表单组件
 */
@Component
export interface IFormField {
    name: string;
    label: string;
    type: 'text' | 'number' | 'email' | 'password' | 'textarea';
    value: any;
    required?: boolean;
    validator?: (value: any) => boolean;
    errorMessage?: string;
}

@Component
export class FormField {
    @State value: any = '';
    @State error: string = '';
    @State isTouched: boolean = false;
    
    config: IFormField;
    
    constructor(config: IFormField) {
        this.config = config;
        this.value = config.value;
    }
    
    validate(): boolean {
        this.isTouched = true;
        if (this.config.required && !this.value) {
            this.error = this.config.errorMessage || '此项为必填';
            return false;
        }
        if (this.config.validator) {
            const isValid = this.config.validator(this.value);
            if (!isValid) {
                this.error = this.config.errorMessage || '验证失败';
                return false;
            }
        }
        this.error = '';
        return true;
    }
    
    build() {
        Column() {
            Text(this.config.label).fontSize(14);
            TextInput({ placeholder: '请输入 ' + this.config.label)
                .text(this.value)
                .onChange((value: string) => {
                    this.value = value;
                    if (this.isTouched) {
                        this.validate();
                    }
                }
            if (this.error) {
                Text(this.error).fontColor(Color.Red).fontSize(12);
            }
        }.width('100%');
    }
}

@Component
export struct ComplexForm {
    @State fields: FormField[] = [];
    @State isSubmitting: boolean = false;
    @State submitSuccess: boolean = false;
    
    build() {
        Column() {
            ForEach(this.fields, (field: FormField) => {
                field
            });
            
            Button('提交')
                .onClick(() => {
                    this.handleSubmit();
                })
                .enabled(!this.isSubmitting)
                .margin({ top: 20 });
            
            if (this.submitSuccess) {
                Text('提交成功！').fontColor(Color.Green);
            }
        }.padding(20);
    }
    
    addField(config: IFormField) {
        const field = new FormField(config);
        this.fields.push(field);
    }
    
    handleSubmit() {
        let allValid = true;
        for (const field of this.fields) {
            if (!field.validate()) {
                allValid = false;
            }
        }
        if (allValid) {
            this.isSubmitting = true;
            setTimeout(() => {
                this.isSubmitting = false;
                this.submitSuccess = true;
            }, 1000);
        }
    }
}

@Component
export struct LoginForm {
    @State email: string = '';
    @State password: string = '';
    @State emailError: string = '';
    @State passwordError: string = '';
    
    build() {
        Column() {
            Text('登录').fontSize(24).fontWeight(FontWeight.Bold).margin({ bottom: 20 });
            
            TextInput({ placeholder: '请输入邮箱' })
                .text(this.email)
                .onChange((value: string) => {
                    this.email = value;
                    this.validateEmail();
                };
            
            if (this.emailError) {
                Text(this.emailError).fontColor(Color.Red);
            }
            
            TextInput({ placeholder: '请输入密码', type: InputType.Password })
                .text(this.password)
                .onChange((value: string) => {
                    this.password = value;
                    this.validatePassword();
                });
            
            if (this.passwordError) {
                Text(this.passwordError).fontColor(Color.Red);
            }
            
            Button('登录')
                .onClick(() => {
                    this.handleLogin();
                })
                .margin({ top: 20 });
        }.padding(20);
    }
    
    validateEmail() {
        if (!this.email) {
            this.emailError = '邮箱不能为空';
            return false;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(this.email)) {
            this.emailError = '请输入有效的邮箱地址';
            return false;
        }
        this.emailError = '';
        return true;
    }
    
    validatePassword() {
        if (!this.password) {
            this.passwordError = '密码不能为空';
            return false;
        }
        if (this.password.length < 6) {
            this.passwordError = '密码长度至少 6 位';
            return false;
        }
        this.passwordError = '';
        return true;
    }
    
    handleLogin() {
        const isEmailValid = this.validateEmail();
        const isPasswordValid = this.validatePassword();
        if (isEmailValid && isPasswordValid) {
            console.log('登录成功');
        }
    }
}
