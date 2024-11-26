import tkinter as tk
from tkinter import Frame, Text, Entry, Button, DISABLED, WORD, Label
from PIL import Image, ImageTk
from typing import Protocol

from config.constants import colors, fonts
from utils.file_utils import get_abs_path_at_runtime

# Constants
BG_GRAY = colors.GRAY_CHATEAU
BG_BLACK = colors.BLACK
BG_COLOR = colors.MIDNIGHT
TEXT_COLOR = colors.PORCELAIN
FONT = fonts.HELVETICA_14
FONT_BOLD = fonts.HELVETICA_13_BOLD

class Presenter(Protocol):
    ...

class View:

    # Define the fields of this class
    root: tk.Tk
    label: tk.Label
    button: tk.Button

    # Initialize the view
    def __init__(self) -> None:

        # Root config
        self.root = tk.Tk()
        self.root.grid_rowconfigure(0, weight=1)  # Allocate extra space to row 0
        self.root.grid_columnconfigure(0, weight=1)  # Allocate extra space to column 0
        self.root.grid_columnconfigure(1, weight=1)  # Allocate extra space to column 1
        self.root.minsize(500, 500)
        self.root.config(bg=BG_BLACK)
        self.root.attributes('-fullscreen', True)

        # Create a Frame
        chat_frame = Frame(self.root)
        chat_frame.grid(row=0, column=0, sticky='NWSE', columnspan=1, rowspan=1)  # Add the Frame to the root window and make it stick to the left
        chat_frame.grid_rowconfigure(0, weight=1)  # Allocate extra space to row 0
        chat_frame.grid_columnconfigure(0, weight=1)  # Allocate extra space to column 0

        # Create image widget
        title_screen_path = get_abs_path_at_runtime("assets/title_screen.png")
        image_widget = create_image_widget(self.root, title_screen_path)
        image_widget.grid(row=0, column=1, sticky="W")

        # Create Main Chat Area
        txt = Text(chat_frame, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=60, wrap=WORD)
        txt.grid(row=0, column=0, columnspan=2, sticky='NSWE')

        # Set chat window settings
        txt.tag_config("You", foreground="green") # Set the user text color
        txt.tag_config("DungeonMaster", foreground="white") # Set the ChatGPT text color
        txt.config(state=DISABLED) # Disable the chat window for typing

        # Create the text input field
        e = Entry(chat_frame, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        e.grid(row=1, column=0, columnspan=1, sticky='WSE', padx=0)
        e.focus_set()
        e.config(state=DISABLED) # Will be enabled after the ChatGPT response

        # Create a send button
        send_button = Button(chat_frame, text="Send", font=FONT_BOLD, bg=BG_GRAY)
        send_button.grid(row=1, column=1, sticky='WS', padx=0)
        send_button.config(state=DISABLED) # Disabled until the user is allowed to type something

    # Set up the UI with the presenter bindings
    def create_ui(self, presenter: Presenter) -> None:
        ...
        # self.button.config(command=presenter.on_button_click)
    
    # Start the main event loop
    def mainloop(self) -> None:
        self.root.mainloop()

def create_image_widget(root, file_path):
    img = Image.open(file_path)
    photo = ImageTk.PhotoImage(img)
    image_widget = Label(root, image=photo)
    image_widget.image = photo
    image_widget.original = img

    return image_widget