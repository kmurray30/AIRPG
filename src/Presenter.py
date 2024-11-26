from typing import Protocol

class View(Protocol):
    def mainloop(self) -> None:
        ...

class Presenter:

    # Define the fields of this class
    view: View

    # Initialize the presenter with a reference to the view
    def __init__(self, view: View) -> None:
        self.view = view

    # Run the presenter which handles all logic before running the main event loop
    def run(self) -> None:
        self.view.create_ui(self)
        self.view.mainloop()

    def on_button_click(self) -> None:
        print("Button clicked!")