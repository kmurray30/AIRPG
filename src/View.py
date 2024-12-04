import tkinter as tk
from tkinter import Frame, Text, Entry, Button, DISABLED, WORD, Label, NORMAL, END
from PIL import Image, ImageTk
from typing import Protocol

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
    label: tk.Label
    send_button: tk.Button

    # Define the widgets
    txt: Text

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
        image_widget = self.create_image_widget(self, title_screen_path)
        image_widget.grid(row=0, column=1, sticky="W")

        # Create Main Chat Area
        self.txt = Text(chat_frame, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=60, wrap=WORD)
        self.txt.grid(row=0, column=0, columnspan=2, sticky='NSWE')

        # Set chat window settings
        self.txt.tag_config("You", foreground="green") # Set the user text color
        self.txt.tag_config("DungeonMaster", foreground="white") # Set the ChatGPT text color
        self.txt.config(state=DISABLED) # Disable the chat window for typing

        # Create the text input field
        e = Entry(chat_frame, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        e.grid(row=1, column=0, columnspan=1, sticky='WSE', padx=0)
        e.focus_set()
        e.config(state=DISABLED) # Will be enabled after the ChatGPT response

        # Create a send button
        self.send_button = Button(chat_frame, text="Send", font=FONT_BOLD, bg=BG_GRAY)
        self.send_button.grid(row=1, column=1, sticky='WS', padx=0)

    # Set up the UI with the presenter bindings
    def create_ui(self, presenter: Presenter) -> None:
        self.send_button.config(command=presenter.on_send)
    
    # Start the main event loop
    def mainloop(self) -> None:
        # Call mainloop of the parent class TK
        super().mainloop()
    
    def add_text_to_chat_window(self, text, role):
        self.txt.config(state=NORMAL)
        self.txt.insert(END, role + " -> " + text + "\n\n\n\n", role)
        self.txt.config(state=DISABLED)

    def create_image_widget(self, root, file_path):
        img = Image.open(file_path)
        photo = ImageTk.PhotoImage(img)
        image_widget = Label(root, image=photo)
        image_widget.image = photo
        image_widget.original = img
        return image_widget