class Parent:
    def show(self):
        print("This is Parent Class")

class Child(Parent):
    def display(self):
        super().show()
        print("This is Child Class")

obj = Child()
obj.display()