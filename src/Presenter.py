from typing import Protocol
import time
import traceback
from utils.file_utils import format_path_from_root

import simpleaudio as sa
import concurrent.futures

class View(Protocol):
    def mainloop(self) -> None:
        ...

class Presenter:

    # Define the fields of this class
    view: View
    cancel_audio_token = {"value": False}
    executor = concurrent.futures.ThreadPoolExecutor()

    # Initialize the presenter with a reference to the view
    def __init__(self, view: View) -> None:
        self.view = view

    # Run the presenter which handles all logic before running the main event loop
    def run(self) -> None:
        self.view.create_ui(self)
        self.initial_screen()
        self.view.mainloop()

    def initial_screen(self) -> None:
        print("Initial screen setup")

        # Play the title screen music using simpleaudio and file assets/Title-14.wav
        self.executor.submit(
            self.play_audio_on_loop,
                format_path_from_root("assets/Title-14.wav"),
                cancel_token=self.cancel_audio_token)

    def play_audio_file(self, file_path, cancel_token):
        try:
            # Load the audio file from the provided path
            print(f"Loading audio file from: {file_path}")
            wave_obj = sa.WaveObject.from_wave_file(file_path)

            print("Loaded audio file")
            
            # Play the audio
            file_name = file_path.split("/")[-1]
            print(f"Playing audio {file_name}")
            play_obj = wave_obj.play()
            
            # Wait for the audio to finish playing or stop if cancel_token is set
            while play_obj.is_playing():
                if (cancel_token["value"] == True):
                    print(f"Stopping audio {file_name}")
                    play_obj.stop()
                    break
                time.sleep(1)
        except Exception as e:
            print(f"An error occurred while playing the audio")
            traceback.print_exc()
            raise(e)

    def play_audio_on_loop(self, file_path, cancel_token):
        i = 0
        while cancel_token["value"] == False:
            print(f"Looping audio {i}")
            self.play_audio_file(file_path, cancel_token)
    
    def on_button_click(self) -> None:
        print("Button clicked!")
        self.cancel_audio_token["value"] = True
        print(f"Cancel audio token set to: {self.cancel_audio_token}")

    def on_exit(self) -> None:
        print("Exiting the application")
        self.cancel_audio_token["value"] = True
        # self.executor.shutdown(wait=False)