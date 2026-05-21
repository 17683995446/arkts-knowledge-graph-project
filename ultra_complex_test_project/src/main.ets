/**
 * 项目入口
 */
import { MainPage } from './ui/Buttons';
import { UserService, ItemService, NotificationService } from './business/BusinessLogic';
import { Logger } from './utils/Utils';

@Entry
@Component
struct App {
    private userService: UserService = new UserService('user_service');
    private itemService: ItemService = new ItemService('item_service');
    private notificationService: NotificationService = new NotificationService('notification_service');
    private logger: Logger = Logger.getInstance('App');
    
    aboutToAppear() {
        this.logger.info('应用启动');
        this.userService.on('loginSuccess', (user) => {
            this.logger.info('用户登录:', user.name);
            this.notificationService.addNotification({
                title: '欢迎回来',
                message: `欢迎 ${user.name} 回来！'
            });
        });
    }
    
    build() {
        MainPage();
    }
}
