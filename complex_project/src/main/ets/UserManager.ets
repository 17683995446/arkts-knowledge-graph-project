
// UserManager.ets - 用户管理模块
import { TestUtils } from './TestUtils';

export interface User {
    id: number;
    name: string;
    email: string;
}

export class UserManager {
    private users: User[] = [];
    private nextId: number = 1;
    
    constructor() {
        TestUtils.log('UserManager initialized');
    }
    
    addUser(name: string, email: string): User {
        const user: User = {
            id: this.nextId++,
            name: name,
            email: email
        };
        this.users.push(user);
        TestUtils.log(`Added user: ${name}`);
        return user;
    }
    
    getUserById(id: number): User | null {
        return this.users.find(user =&gt; user.id === id) || null;
    }
    
    getAllUsers(): User[] {
        return [...this.users];
    }
    
    removeUser(id: number): boolean {
        const index = this.users.findIndex(user =&gt; user.id === id);
        if (index !== -1) {
            this.users.splice(index, 1);
            TestUtils.log(`Removed user with id: ${id}`);
            return true;
        }
        return false;
    }
    
    updateUser(id: number, name?: string, email?: string): boolean {
        const user = this.getUserById(id);
        if (user) {
            if (name) user.name = name;
            if (email) user.email = email;
            TestUtils.log(`Updated user: ${user.name}`);
            return true;
        }
        return false;
    }
}
