import tkinter as tk
from tkinter import Frame, Text, Entry, Button, DISABLED, WORD, Label, NORMAL, END
from PIL import Image, ImageTk
from typing import Protocol, Callable

from config.constants import colors, fonts
from utils.file_utils import format_path_from_root

# Constants
BG_GRAY = colors.GRAY_CHATEAU
BG_BLACK = colors.BLACK
BG_COLOR = colors.MIDNIGHT
TEXT_COLOR = colors.PORCELAIN
FONT = fonts.HELVETICA_14
FONT_BOLD = fonts.HELVETICA_13_BOLD

class Presenter(Protocol):
    ...

# Make View a subclass of Tkinter's Tk class
class View(tk.Tk):

    # Define the fields of this class
    root: tk.Tk

    # Define the widgets
    label: tk.Label
    send_button: tk.Button
    chat_window: Text
    image_widget: Label
    txt_input_field: Entry

    # Presenter functions needed for toggling the send button
    send_function: Callable[[], None]
    skip_function: Callable[[], None]

    # Initialize the view
    def __init__(self) -> None:

        # Initialize the parent class
        super().__init__()

        # Root config
        self.grid_rowconfigure(0, weight=1)  # Allocate extra space to row 0
        self.grid_columnconfigure(0, weight=1)  # Allocate extra space to column 0
        self.grid_columnconfigure(1, weight=1)  # Allocate extra space to column 1
        self.minsize(500, 500)
        self.config(bg=BG_BLACK)
        self.attributes('-fullscreen', True)

        # Create a Frame
        chat_frame = Frame(self)
        chat_frame.grid(row=0, column=0, sticky='NWSE', columnspan=1, rowspan=1)  # Add the Frame to the root window and make it stick to the left
        chat_frame.grid_rowconfigure(0, weight=1)  # Allocate extra space to row 0
        chat_frame.grid_columnconfigure(0, weight=1)  # Allocate extra space to column 0

        # Create image widget
        title_screen_path = format_path_from_root("assets/title_screen.png")
        self.image_widget = self.create_image_widget(self, title_screen_path)
        self.image_widget.grid(row=0, column=1, sticky="W")

        # Create Main Chat Area
        self.chat_window = Text(chat_frame, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=60, wrap=WORD)
        self.chat_window.grid(row=0, column=0, columnspan=2, sticky='NSWE')

        # Set chat window settings
        self.chat_window.tag_config("You", foreground="green") # Set the user text color
        self.chat_window.tag_config("DungeonMaster", foreground="white") # Set the ChatGPT text color
        self.chat_window.config(state=DISABLED) # Disable the chat window for typing

        # Create the text input field
        self.txt_input_field = Entry(chat_frame, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.txt_input_field.grid(row=1, column=0, columnspan=1, sticky='WSE', padx=0)
        self.txt_input_field.focus_set()
        self.txt_input_field.config(state=DISABLED) # Will be enabled after the ChatGPT response
        # TODO this line above is causing the txt field to be disabled
        # I'm conflating the txt field with the e field

        # Create a send button
        self.send_button = Button(chat_frame, text="Skip", font=FONT_BOLD, bg=BG_GRAY)
        self.send_button.grid(row=1, column=1, sticky='WS', padx=0)

    # Set up the UI with the presenter bindings
    def create_ui(self, presenter: Presenter) -> None:
        self.send_function = presenter.on_send
        self.skip_function = presenter.on_skip
        self.send_button.config(command=presenter.on_initial_skip)
        self.txt_input_field.bind("<Return>", self.send_function)
    
    # Start the main event loop
    def mainloop(self) -> None:
        # Call mainloop of the parent class TK
        super().mainloop()

    def create_image_widget(self, root, file_path) -> Label:
        img = Image.open(file_path)
        photo = ImageTk.PhotoImage(img)
        image_widget = Label(root, image=photo)
        image_widget.image = photo
        image_widget.original = img
        return image_widget
    
    def update_image_widget(self, file_path) -> None:
        img = Image.open(file_path)
        photo = ImageTk.PhotoImage(img)
        self.image_widget.config(image=photo)
        self.image_widget.image = photo
        self.image_widget.original = img
    
    def enable_skip_button(self) -> None:
        print("DEBUG: setting send button to Skip")
        self.send_button.config(state=NORMAL)
        self.send_button.config(text="Skip")
        self.send_button.config(command=self.skip_function)

    def enable_text_and_send_button(self) -> None:
        print("DEBUG: enabling text field and send button")
        self.txt_input_field.config(state=NORMAL)
        self.send_button.config(state=NORMAL)
        self.send_button.config(text="Send")
        self.send_button.config(command=self.send_function)
    
    def drain_text(self) -> str:
        user_prompt = "" + self.txt_input_field.get()
        if user_prompt == "":
            return
        self.txt_input_field.delete(0, END) # Clear the input field
        return user_prompt
    
    def disable_send(self) -> str:
        print("DEBUG: disabling send button")
        self.txt_input_field.config(state=DISABLED)
        self.send_button.config(text="Wait...")
        self.send_button.config(state=DISABLED)

    def display_chat_message(self, role, text) -> None:
        self.chat_window.config(state=NORMAL)
        self.chat_window.insert(END, role + " -> " + text + "\n\n\n\n", role)
        self.chat_window.config(state=DISABLED)
        print("DEBUG: chat window disabled")