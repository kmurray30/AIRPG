from tkinter import Tk, Frame, Text, Entry, Button, DISABLED, WORD, END, NORMAL, DISABLED
from tkinter import Label
import os
import concurrent.futures
import sys

import urllib.request
import random

from PIL import Image, ImageTk

from Utilities import ChatBot
from Utilities import TextToSpeech
from Utilities import ImageGenerator
from concurrent.futures import Future

import simpleaudio as sa

from Utilities.Utilities import get_path_from_project_root

DEBUG = False

# GUI
root = Tk()

BG_GRAY = "#ABB2B9"
BG_BLACK = "#000000"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

# Art styles
medieval_tavern = "medieval tavern"
realistic_office = "realistic office"
animated_show = "animated tv show"
studio_ghibli = "studio ghibli"

image_prompt = f"Generate the following scene in the a {studio_ghibli} style, making sure to include a character that looks like aragorn from The Lord of the Rings, and don't include any text: "

chatGptMessages = [
        {
            "role": "system",
            "content": """
            You are a table top role playing game dungeon master. Please always limit your responses to a few sentences.
            """}
    ]

executor = concurrent.futures.ThreadPoolExecutor()

image_widget = None

title_audio_flag = True

def get_asset_from_root_path(relative_path):
    if getattr(sys, 'frozen', False):
        # The application is running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # The application is running in a normal Python environment
        return get_path_from_project_root(relative_path)

def play_audio_file(file_path, cancel_token=None):
    try:
        # Load the audio file from the provided path
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        
        # Play the audio
        play_obj = wave_obj.play()
        
        # Wait for the audio to finish playing
        if cancel_token:
            while not cancel_token["value"]:
                pass
            play_obj.stop()
        else:
            play_obj.wait_done()
    except Exception as e:
        print(f"An error occurred while playing the audio: {e}")

def play_audio_on_loop(file_path, cancel_token=None):
    if cancel_token:
        while True and not cancel_token["value"]:
            play_audio_file(file_path, cancel_token)
    else:
        while True:
            play_audio_file(file_path)

def play_music():
    # Create a pointer to a boolean so it can be passed into the thread and modified here
    cancel_token = {"value": False}
    executor.submit(play_audio_on_loop, get_asset_from_root_path("assets/Title-14.wav"), cancel_token=cancel_token)

    global title_audio_flag
    # Wait for the title screen flag to be turned off
    while title_audio_flag:
        pass

    # Kill the title music and play the tavern music and chatter
    cancel_token["value"] = True
    executor.submit(play_audio_on_loop, get_asset_from_root_path("assets/Tavern-20.wav"))
    executor.submit(play_audio_on_loop, get_asset_from_root_path("assets/Chatter-12.wav"))

# Function to summarize and speak the user input
def summarize_and_speak(prompt):
    summary = ChatBot.call_openai_without_context("Repeat back my proposed actions to me, and make a brief comment asking the character to hang tight while the scene is generated: " + prompt)
    executor.submit(TextToSpeech.convert_play_delete_text_to_speech_file, summary, summary_as_filename=True, delete=False)

# Function to generate a speech file from the scene description
def generate_speech_file(scene_description):
    speech_file_path = TextToSpeech.generate_audio_file(scene_description, summary_as_filename=True, delete=False)
    TextToSpeech.convert_text_to_speech_file(scene_description, speech_file_path)
    return speech_file_path

def create_image_widget(root, file_path):
    img = Image.open(file_path)
    photo = ImageTk.PhotoImage(img)
    image_widget = Label(root, image=photo)
    image_widget.image = photo
    image_widget.original = img

    return image_widget

def update_image_widget(image_widget, file_path):
    img = Image.open(file_path)
    photo = ImageTk.PhotoImage(img)
    image_widget.config(image=photo)
    image_widget.image = photo
    image_widget.original = img

def add_text_to_chat_window(text, role):
    txt.config(state=NORMAL)
    txt.insert(END, role + " -> " + text + "\n\n\n\n", role)
    txt.config(state=DISABLED)

def save_image_from_url(url, file_path):
    urllib.request.urlretrieve(url, file_path)

def submit_prompt_and_narrate_task(user_prompt, summary_future):
    # Call ChatGPT
    gtp_scene_description = ChatBot.call_openai_and_update_chat_messages(user_prompt, chatGptMessages)
     
    # Generate the image from the scene description (non-blocking)
    if DEBUG:
        image_url_future = Future()
        image_url_future.set_result(get_asset_from_root_path("assets/sample_tavern_art.png"))
    else:
        prompt = image_prompt + gtp_scene_description
        image_url_future = executor.submit(ImageGenerator.generate_image_url, prompt)

    # Generate the speech file from the scene description (non-blocking)
    speech_file_future = executor.submit(generate_speech_file, gtp_scene_description)

    # Wait for the summary speech, image gen, and speech gen (and music gen) to all finish
    concurrent.futures.wait([summary_future, speech_file_future, image_url_future])

    # Turn off the title audio flag if it is still on
    global title_audio_flag
    title_audio_flag = False

    # Display the response
    add_text_to_chat_window(gtp_scene_description, "DungeonMaster")

    # Save the image to a file
    if DEBUG:
        image_path = image_url_future.result()
    else:
        image_path = get_path_from_project_root(f"generated/temp/temp{random.randint(0, 1000000)}.png")
        save_image_from_url(image_url_future.result(), image_path)

    # Display the image
    update_image_widget(image_widget, image_path)

    # Change the "Send" button to "Skip"
    print("DEBUG: setting send button to Skip")
    send_button.config(state=NORMAL)
    send_button.config(text="Skip")
    send_button.config(command=TextToSpeech.cancel_audio)

    # Play the speech audio
    TextToSpeech.play_audio_file(speech_file_future.result())

    send_button.config(text="Send")
    
    e.config(state=NORMAL)
    # send_button.config(state=NORMAL) TODO REMOVE
    e.delete(0, END)
	
# Send function
def send_prompt_task():
    user_prompt = "" + e.get()
    if user_prompt == "":
        return
    e.delete(0, END) # Clear the input field
    e.config(state=DISABLED)
    send_button.config(state=DISABLED)

    # Display the user input
    add_text_to_chat_window(user_prompt, "You")
     
    # Summarize and speak the user input (non-blocking)
    summary_future = executor.submit(summarize_and_speak, user_prompt)
	
    # Call ChatGPT in a separate thread. The only blocker should be the disabling of the text field
    executor.submit(submit_prompt_and_narrate_task, user_prompt, summary_future)

def enforce_aspect_ratio(event):
    new_height = root.winfo_height() - 10
    new_width = new_height

    # Resize the original image while maintaining its aspect ratio
    img = image_widget.original.copy()
    img.thumbnail((new_width, new_height))

    # Create a PhotoImage object from the resized image
    photo = ImageTk.PhotoImage(img)

    # Update the image displayed by the Label widget
    image_widget.config(image=photo)
    image_widget.image = photo  # Keep a reference to the image object to prevent it from being garbage collected

# Root config
root.grid_rowconfigure(0, weight=1)  # Allocate extra space to row 0
root.grid_columnconfigure(0, weight=1)  # Allocate extra space to column 0
root.grid_columnconfigure(1, weight=1)  # Allocate extra space to column 1
root.minsize(500, 500)
root.config(bg=BG_BLACK)
root.attributes('-fullscreen', True)

# Create a Frame
chat_frame = Frame(root)
chat_frame.grid(row=0, column=0, sticky='NWSE', columnspan=1, rowspan=1)  # Add the Frame to the root window and make it stick to the left
chat_frame.grid_rowconfigure(0, weight=1)  # Allocate extra space to row 0
chat_frame.grid_columnconfigure(0, weight=1)  # Allocate extra space to column 0

# Create image widget
title_screen_path = get_asset_from_root_path("assets/title_screen.png")
image_widget = create_image_widget(root, title_screen_path)
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
send_button = Button(chat_frame, text="Send", font=FONT_BOLD, bg=BG_GRAY,
			command=send_prompt_task)
send_button.grid(row=1, column=1, sticky='WS', padx=0)
send_button.config(state=DISABLED) # Disabled until the user is allowed to type something

# Bind the Enter key to the send function
root.bind('<Return>', lambda event: send_prompt_task())
# Bind the function to the <Configure> event
root.bind('<Configure>', enforce_aspect_ratio)

### Initial scene
if DEBUG:
    intro = "Hi, welcome to the game. Loading initial scene."
else:
    intro = "Welcome to the epic adventure that awaits you in Chat RPG. From mystical forests to ancient, bustling cities, explore an infinitely unfolding world shaped by your actions and decisions. With deep and complex NPCs, beautifully generated art, and epic narration, an exciting journey awaits you, if you are ready. Your adventure begins in an unassuming tavern."
initial_prompt = "Set up an initial scene in a medieval tavern."

# Display the response
add_text_to_chat_window(intro, "DungeonMaster")

# Intro music
executor.submit(play_music)

# Change the "Send" button to "Skip"
print("DEBUG: setting send button to Skip")
send_button.config(state=NORMAL)
send_button.config(text="Skip")
send_button.config(command=TextToSpeech.cancel_audio)

# Intro speech
intro_future = executor.submit(TextToSpeech.convert_play_delete_text_to_speech_file, intro, summary_as_filename=False, delete=True)

# Call ChatGPT in a future thread
print("DEBUG 1")
executor.submit(submit_prompt_and_narrate_task, initial_prompt, intro_future)

# Start the GUI
root.mainloop()

