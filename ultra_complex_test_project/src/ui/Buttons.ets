/**
 * 复杂 UI 组件
 */
import { BaseComplexClass } from '../core';

export interface IButtonProps {
    id: string;
    text: string;
    onClick?: () => void;
    disabled?: boolean;
    variant?: 'primary' | 'secondary' | 'danger' | 'success';
    size?: 'small' | 'medium' | 'large';
}

@Component
export class Button extends BaseComplexClass {
    props: IButtonProps;
    private _isPressed: boolean;
    private _hover: boolean;
    
    constructor(props: IButtonProps) {
        super(props.id);
        this.props = props;
        this._isPressed = false;
        this._hover = false;
    }
    
    protected initialize(): void {
    }
    
    handlePress(): void {
        if (this.props.disabled || this.isDestroyed) {
            return;
        }
        this._isPressed = true;
        this.emit('press');
        if (this.props.onClick) {
            this.props.onClick();
        }
        setTimeout(() => {
            this._isPressed = false;
            this.emit('release');
        }, 200);
    }
    
    handleMouseEnter(): void {
        this._hover = true;
        this.emit('hover', true);
    }
    
    handleMouseLeave(): void {
        this._hover = false;
        this.emit('hover', false);
    }
    
    render(): string {
        const classes = ['button', this.props.variant || 'primary', this.props.size || 'medium'];
        if (this._isPressed) {
            classes.push('pressed');
        }
        if (this._hover) {
            classes.push('hover');
        }
        if (this.props.disabled) {
            classes.push('disabled');
        }
        return `<button class="${classes.join(' ')}">${this.props.text}</button>`;
    }
}

@Entry
@Component
export struct MainPage {
    @State message: string = 'Hello World';
    @State count: number = 0;
    @State isLoading: boolean = false;
    button: Button | undefined;
    
    build() {
        Column() {
            Text(this.message).fontSize(20).margin(10);
            Button() {
                Text('点击计数: ' + this.count).fontSize(16)
            }.onClick(() => {
                this.count++;
                if (this.button) {
                    this.button.handlePress();
                }
            }).margin(10);
        }.width('100%').height('100%');
    }
    
    aboutToAppear() {
        this.button = new Button({
            id: 'mainButton', text: '主按钮'
        });
        this.button.on('press', () => {
            console.log('按钮被按下');
        });
    }
}

@Component
export struct UserProfile {
    @State userName: string = '';
    @State avatarUrl: string = '';
    @State bio: string = '';
    
    build() {
        Column() {
            if (this.avatarUrl) {
                Image(this.avatarUrl).width(100).height(100).borderRadius(50);
            }
            Text(this.userName).fontSize(18).fontWeight(FontWeight.Bold);
            Text(this.bio).fontSize(14).opacity(0.8).margin(5);
        }.padding(20).backgroundColor('#f5f5f5');
    }
}

@Component
export struct DataList {
    @State items: string[] = [];
    
    build() {
        List() {
            ForEach(this.items, (item: string) => {
                ListItem() {
                    Text(item).padding(10)
                }
            })
        }.height('100%');
    }
    
    addItem(item: string) {
        this.items.push(item);
    }
    
    removeItem(index: number) {
        this.items.splice(index, 1);
    }
}

@Component
export struct LoadingIndicator {
    @State isLoading: boolean = false;
    
    build() {
        if (this.isLoading) {
            Column() {
                LoadingProgress().width(50).height(50);
                Text('加载中...');
            }.justifyContent(FlexAlign.Center);
        }
    }
}
