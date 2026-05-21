// 超多组件
@Component
struct ButtonComponent {
  label: string = "Click";
  onClick?: () => void;
  
  build() {
    Button(this.label)
      .onClick(() => {
        if (this.onClick) {
          this.onClick();
        }
      })
  }
}

@Component
struct InputComponent {
  value: string = "";
  onChange?: (value: string) => void;
  
  build() {
    TextInput({ text: this.value })
      .onChange((value: string) => {
        if (this.onChange) {
          this.onChange(value);
        }
      })
  }
}

@Component
struct CardComponent {
  title: string = "";
  content: string = "";
  
  build() {
    Column() {
      Text(this.title).fontSize(18)
      Text(this.content).fontSize(14)
    }.padding(16)
  }
}

@Component
struct ListComponent {
  items: string[] = [];
  
  build() {
    List() {
      ForEach(this.items, (item: string) => {
        ListItem() {
          Text(item)
        }
      })
    }
  }
}

@Component
struct FormComponent {
  @State name: string = "";
  @State email: string = "";
  
  build() {
    Column() {
      InputComponent({
        value: this.name,
        onChange: (v) => this.name = v
      })
      InputComponent({
        value: this.email,
        onChange: (v) => this.email = v
      })
      ButtonComponent({
        label: "Submit",
        onClick: () => {
          console.log("Submit", this.name, this.email);
        }
      })
    }
  }
}

@Entry
@Component
struct MainComponent {
  build() {
    Column() {
      CardComponent({ title: "Welcome", content: "Hello!" })
      FormComponent()
    }
  }
}
