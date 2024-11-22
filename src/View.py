import tkinter as tk
from typing import Protocol

class Presenter(Protocol):
    ...

class View:
    # Define the fields of this class
    root: tk.Tk
    label: tk.Label
    button: tk.Button

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("MVC Example")
        self.root.geometry("400x200")
        self.label = tk.Label(self.root, text="Hello, World!")
        self.label.pack()
        self.button = tk.Button(self.root, text="Click Me!")
        self.button.pack()

    def create_ui(self, presenter: Presenter) -> None:
        self.button.config(command=presenter.on_button_click)
    
    def mainloop(self) -> None:
        self.root.mainloop()