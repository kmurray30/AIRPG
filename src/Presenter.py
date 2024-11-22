from typing import Protocol

class View(Protocol):
    def mainloop(self) -> None:
        ...

class Presenter:
    
    # Define the fields of this class
    view: View

    def __init__(self, view: View) -> None:
        self.view = view

    def run(self) -> None:
        self.view.create_ui(self)
        self.view.mainloop()

    def on_button_click(self) -> None:
        print("Button clicked!")