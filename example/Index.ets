@Component
export struct UserCard {
    @Prop name: string = "";
    @Prop email: string = "";
    @State isExpanded: boolean = false;

    build(): void {
        Column() {
            Text(this.name)
                .fontSize(20)
                .fontWeight(FontWeight.Bold)

            if (this.isExpanded) {
                Text(this.email)
                    .fontSize(14)
                    .opacity(0.7)
            }

            Button(this.isExpanded ? "Collapse" : "Expand")
                .onClick(() => {
                    this.isExpanded = !this.isExpanded;
                })
        }
        .padding(16)
        .backgroundColor("#f5f5f5")
        .borderRadius(8)
    }

    private animateExpansion(): void {
        console.log("Animating expansion");
    }
}

@Entry
@Component
struct MainPage {
    @State users: User[] = [];
    @State selectedUser: User | null = null;

    aboutToAppear(): void {
        this.loadUsers();
    }

    build(): void {
        Column() {
            this.renderHeader()
            this.renderUserList()
        }
        .width("100%")
        .height("100%")
    }

    @Builder
    renderHeader(): void {
        Row() {
            Text("User Management")
                .fontSize(24)
                .fontWeight(FontWeight.Bold)
        }
        .width("100%")
        .padding(16)
        .backgroundColor("#2196F3")
    }

    @Builder
    renderUserList(): void {
        List() {
            ForEach(this.users, (user: User) => {
                ListItem() {
                    UserCard({
                        name: user.name,
                        email: user.email
                    })
                    .onClick(() => {
                        this.selectUser(user);
                    })
                }
            })
        }
        .width("100%")
    }

    private loadUsers(): void {
        this.users = [
            { id: 1, name: "Alice", email: "alice@example.com" },
            { id: 2, name: "Bob", email: "bob@example.com" },
            { id: 3, name: "Charlie", email: "charlie@example.com" }
        ];
    }

    private selectUser(user: User): void {
        this.selectedUser = user;
        console.log("Selected user:", user.name);
    }
}

interface User {
    id: number;
    name: string;
    email: string;
}

function validateEmail(email: string): boolean {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}

function formatUserDisplay(user: User): string {
    return `${user.name} <${user.email}>`