from typing import Protocol
import time
import traceback
from utils.file_utils import format_path_from_root
from config.constants import audio_files
from chat_session import ChatSession
from scene import Scene

import simpleaudio as sa
import concurrent.futures

class View(Protocol):
    def mainloop(self) -> None:
        ...

class Presenter:

    # Define the fields of this class
    view: View
    cancel_music_token = {"value": False}
    cancel_narration_token = {"value": False}
    executor = concurrent.futures.ThreadPoolExecutor()

    # Initialize the presenter with a reference to the view
    def __init__(self, view: View) -> None:
        self.view = view

    # Run the presenter which handles all logic before running the main event loop
    def run(self) -> None:
        self.view.create_ui(self)
        self.view.protocol("WM_DELETE_WINDOW", self.on_exit)  # Bind the cleanup function to the window close event
        self.initialize_chat_session()
        initial_scene = self.generate_initial_scene()
        self.play_scene(initial_scene)
        self.view.mainloop()

    # Generate the initial scene audio and image
    # Returns a Scene object containing the audio and image paths and the chatGPT response
    def generate_initial_scene(self) -> Scene:
        # Set the paths of the initial audio and image and call play_scene
        chatGPT_response = "Welcome to the epic adventure that awaits you in Chat RPG. From mystical forests to ancient, bustling cities, explore an infinitely unfolding world shaped by your actions and decisions. With deep and complex NPCs, beautifully generated art, and epic narration, an exciting journey awaits you, if you are ready. Your adventure begins in an unassuming tavern."
        music_path = format_path_from_root(audio_files.TITLE)
        narration_path = format_path_from_root(audio_files.INTRO_NARRATION)
        image_path = format_path_from_root("assets/title_screen.png")
        return Scene(chatGPT_response, music_path, narration_path, image_path)

    def generate_scene(self, user_input: str) -> None:
        # 1. Take the user prompt as a parameter
        # 2. Start generating vamping audio
        # 3. Start generating the DM response
        # 4. Await the DM response
        # 5. Start generating the image description from the DM response
        # 6. Start generating the DM response audio
        # 7. Play the vamping audio
        # 8. Await the image and DM response audio generation
        # 9. Play the image and DM response audio by calling play_scene
        ...

    def play_scene(self, scene: Scene) -> None:
        # At this point, last image and audio are generated and waiting to be played
        # From here, we will do the following:
        # 1. Play the input audio
        # 2. Display the input image
        # 3. Display the response text in the chat window
        # 4. Switch the send button to the skip button
        
        # Play the initial audio and display the initial image
        self.view.update_image_widget(scene.get_image_path())
        self.executor.submit(self.play_audio_file, scene.get_music_path(), self.cancel_music_token)
        self.executor.submit(self.play_audio_file, scene.get_narration_path(), self.cancel_narration_token, delay=2)

        # Display the response
        self.view.add_text_to_chat_window(scene.get_chatGPT_response(), "DungeonMaster")

        # Switch the send button to the skip button
        self.view.switch_send_button_to_skip(self.on_skip)

    def initialize_chat_session(self) -> None:
        print("Initializing chat session")
        dm_system_prompt = "You are a table top role playing game dungeon master. Please always limit your responses to a few sentences."
        self.chat_session = ChatSession(system_prompt=dm_system_prompt)

    def initial_screen(self) -> None:
        print("Initial screen setup")

        # Play the title screen music using simpleaudio and file assets/Title-14.wav
        self.executor.submit(
            self.play_audio_on_loop,
                format_path_from_root(audio_files.TITLE),
                cancel_token=self.cancel_music_token)
        
        intro = "Welcome to the epic adventure that awaits you in Chat RPG. From mystical forests to ancient, bustling cities, explore an infinitely unfolding world shaped by your actions and decisions. With deep and complex NPCs, beautifully generated art, and epic narration, an exciting journey awaits you, if you are ready. Your adventure begins in an unassuming tavern."

        # Play the initial narration
        self.executor.submit(
            self.play_audio_file,
                format_path_from_root(audio_files.INTRO_NARRATION),
                cancel_token=self.cancel_narration_token, delay=2)

        # Display the response
        self.view.add_text_to_chat_window(intro, "DungeonMaster")

        # Switch the send button to the skip button
        self.view.switch_send_button_to_skip(self.on_skip)

    def play_audio_file(self, file_path, cancel_token, delay=0):
        try:
            time.sleep(delay)

            # Load the audio file from the provided path
            print(f"Loading audio file from: {file_path}")
            wave_obj = sa.WaveObject.from_wave_file(file_path)

            print("Loaded audio file")
            
            # Play the audio
            file_name = file_path.split("/")[-1]
            print(f"Playing audio {file_name}")
            play_obj = wave_obj.play()
            
            # Wait for the audio to finish playing or stop if cancel_token is set
            while play_obj.is_playing(): # TODO make this not waste CPU cycles using threading.Event
                if (cancel_token["value"] == True):
                    print(f"Stopping audio {file_name}")
                    play_obj.stop()
                    cancel_token["value"] = False
                    break
        except Exception as e:
            print(f"An error occurred while playing the audio")
            traceback.print_exc()
            raise(e)

    def play_audio_on_loop(self, file_path, cancel_token):
        i = 1
        file_name = file_path.split("/")[-1]
        while cancel_token["value"] == False:
            self.play_audio_file(file_path, cancel_token)
            i += 1
            print(f"Starting loop {i} on audio {file_name}")
    
    def on_send(self) -> None:
        print("Send button clicked!")

    def on_skip(self) -> None:
        print("Skip button clicked!")
        self.cancel_narration_token["value"] = True

        # Set the send button back to the original state
        self.view.send_button.config(command=self.on_send)
        self.view.send_button.config(text="Send")

    def on_exit(self) -> None:
        print("Exiting the application")
        self.cancel_music_token["value"] = True # sa.stop_all() may also work, but is buggier
        self.cancel_narration_token["value"] = True
        self.executor.shutdown(wait=False)
        self.view.quit()