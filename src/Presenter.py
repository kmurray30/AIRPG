from typing import Protocol
from utils.file_utils import format_path_from_root

import simpleaudio as sa

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
        self.initial_screen()
        self.view.mainloop()

    def initial_screen(self) -> None:
        print("Initial screen setup")

        # Play the title screen music using simpleaudio and file assets/Title-14.wav
        self.play_audio_file(format_path_from_root("assets/Title-14.wav"))

    def on_button_click(self) -> None:
        print("Button clicked!")

    def play_audio_file(self, file_path, cancel_token=None):
        try:
            # Load the audio file from the provided path
            print(f"Loading audio file from: {file_path}")
            wave_obj = sa.WaveObject.from_wave_file(file_path)

            print("Loaded audio file")
            
            # Play the audio
            file_name = file_path.split("/")[-1]
            print(f"Playing audio {file_name}")
            play_obj = wave_obj.play()
            
            # Wait for the audio to finish playing
            # if cancel_token:
            #     while not cancel_token["value"]:
            #         pass
            #     play_obj.stop()
            # else:
            #     play_obj.wait_done()
        except Exception as e:
            # Throw exception e
            raise(e)
            print(f"An error occurred while playing the audio: {e}")