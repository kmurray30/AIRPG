from typing import Protocol
import time
import traceback
from utils.file_utils import format_path_from_root
from config.constants import audio_files, image_files
from chat_session import ChatSession
from scene import Scene
from threading import Event

import simpleaudio as sa
from concurrent import futures

# Prompts and messages
dm_system_prompt = "You are a table top role playing game dungeon master. Please always limit your responses to a few sentences. Do not include text in the image."
title_narration = "Welcome to the epic adventure that awaits you in Chat RPG. From mystical forests to ancient, bustling cities, explore an infinitely unfolding world shaped by your actions and decisions. With deep and complex NPCs, beautifully generated art, and epic narration, an exciting journey awaits you, if you are ready. Your adventure begins in an unassuming tavern."
initial_scene_prompt = "Set up an initial scene in a medieval tavern."
vamp_prompt = "Repeat back my following proposed actions to me in a sassy way and in a few short words, and then ask me to hang tight while the scene is generated"

# from view import View TODO use this instead

class View(Protocol):
    def mainloop(self) -> None:
        ...

class Presenter:
    # Define the fields of this class
    view: View
    cancel_music_token = {"value": False}
    cancel_narration_token = {"value": False}
    cancel_sfx_token = {"value": False}
    narration_finished_event = Event()
    vamping_finished_event = Event()
    executor = futures.ThreadPoolExecutor()
    chat_session: ChatSession
    event_toggle = False
    title_scene = True

    # Initialize the presenter with a reference to the view
    def __init__(self, view: View) -> None:
        self.view = view
        self.chat_session = ChatSession(
            system_prompt=dm_system_prompt,
            executor=self.executor)

    # Run the presenter which handles all logic before running the main event loop
    def run(self) -> None:
        # Create the UI bindings
        self.view.create_ui(self)

        # Bind the cleanup function to the window close event
        self.view.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Generate and play the title screen
        title_scene = self.generate_title_scene()
        self.play_scene(title_scene, title_scene=True)

        # Generate and play the initial scene in a separate thread
        self.executor.submit(self.generate_and_play_initial_scene)
        
        # Start the main event loop
        self.view.mainloop()

    # Generate the initial scene audio and image
    # Returns a Scene object containing the audio and image paths and the chatGPT response
    def generate_title_scene(self) -> Scene:
        # Set the paths of the initial audio and image and call play_scene
        chatGPT_response = title_narration
        music_path = format_path_from_root(audio_files.TITLE)
        narration_path = format_path_from_root(audio_files.INTRO_NARRATION)
        image_path = format_path_from_root(image_files.TITLE_SCREEN)
        return Scene(chatGPT_response, music_path, narration_path, image_path)
    
    def generate_and_play_initial_scene(self) -> Scene:
        intial_scene = self.generate_scene(initial_scene_prompt, vamp=False)
        self.narration_finished_event.wait() # Wait for title scene to finish before playing the initial scene
        if (self.event_toggle is False):
            self.event_toggle = True
        else:
            self.narration_finished_event.clear()
        self.cancel_music_token["value"] = True # Stop the title music
        self.play_scene(intial_scene, initial_scene=True)

    def generate_scene(self, user_input, vamp=True) -> Scene:
        try:
            # Generate the vamping audio and play it if vamp is set
            if (vamp):
                self.vamping_finished_event.clear()
                self.executor.submit(self.vamp_thread, user_input)
            
            # Await the DM response
            chatGPT_response = self.chat_session.append_user_input_and_get_response(user_input)
            
            # Start generating the image
            image_future = self.chat_session.generate_image(chatGPT_response)
            
            # Start generating the DM response audio
            narration_future = self.chat_session.generate_narration(chatGPT_response)

            # Await the image and DM response audio generation
            futures.wait([image_future, narration_future])

            # Wait for the vamping audio to finish playing
            if(vamp):
                self.vamping_finished_event.wait()

            # Return the scene object
            return Scene(chatGPT_response,
                        audio_files.TAVERN_MUSIC,
                        narration_future.result(),
                        image_future.result(),
                        sfx = audio_files.CHATTER)
        except Exception as e:
            print(f"An error occurred while generating the scene")
            traceback.print_exc()
            raise(e)
    
    def vamp_thread(self, user_input):
        # Generate the vamping response and audio
        vamp_response = self.chat_session.generate_vamp_response(user_input, vamp_prompt)
        vamp_audio_future = self.chat_session.generate_narration(vamp_response)
    
        # Wait for and play the vamping audio
        futures.wait([vamp_audio_future])
        vamp_audio_path = vamp_audio_future.result()
        self.play_audio_file(vamp_audio_path, self.cancel_narration_token, self.vamping_finished_event)

    # Play the scene by displaying the image, playing the music, and playing the narration
    def play_scene(self, scene: Scene, initial_scene = False, title_scene = False) -> None:        
        # Play the initial audios and display the initial image (and text)
        self.view.update_image_widget(scene.get_image_path())
        self.executor.submit(self.play_audio_file, scene.get_narration_path(), self.cancel_narration_token, self.narration_finished_event, delay=2)
        if (title_scene): # TODO replace this with a state machine / more elegant solution
            self.executor.submit(self.play_audio_file, scene.get_music_path(), self.cancel_music_token)
        elif (initial_scene):
            self.executor.submit(self.play_audio_on_loop, scene.get_music_path(), self.cancel_music_token)
            if (scene.has_sfx()):
                self.executor.submit(self.play_audio_on_loop, scene.get_sfx_path(), self.cancel_sfx_token)
        self.view.display_chat_message("DungeonMaster", scene.get_chatGPT_response())

        # Switch the send button to the skip button TODO pass in the cancel narration token so it doesn't have to be a class field
        self.view.enable_skip_button()

        # Set up the thread to wait for the narration to finish before enabling the text input TODO make the event a local var as well
        self.executor.submit(self.wait_on_narration_finish_thread)

    def wait_on_narration_finish_thread(self):
        self.narration_finished_event.wait()
        if (self.event_toggle is False): # TODO implement a more elegant solution for this race condition
            self.event_toggle = True
        else:
            self.narration_finished_event.clear()
        if (self.title_scene is True): # TODO replace this with a more elegant solution
            self.view.disable_send()
            self.title_scene = False
        else:
            self.view.enable_text_and_send_button()


    def play_audio_file(self, file_path, cancel_token = None, audio_finished_event = None, delay=0):
        try:
            if (file_path == None):
                raise ValueError("The file path provided is None")

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
            if (cancel_token != None):
                while play_obj.is_playing(): # TODO make this not waste CPU cycles using threading.Event
                    if (cancel_token["value"] == True):
                        print(f"Audio skipped: {file_name}")
                        play_obj.stop()
                        cancel_token["value"] = False
                        break # TODO test if this is necessary.
            else:
                play_obj.wait_done()

            # Signal the audio has finished playing
            print(f"Finished playing audio {file_name}")
            if (audio_finished_event != None):
                audio_finished_event.set()
        except Exception as e:
            print(f"An error occurred while playing the audio file: {file_path}")
            traceback.print_exc()
            raise(e)

    def play_audio_on_loop(self, file_path, cancel_token, audio_finished_event = None):
        i = 1
        file_name = file_path.split("/")[-1]
        while cancel_token["value"] == False:
            print(f"Starting loop {i} on audio {file_name}")
            self.play_audio_file(file_path, cancel_token, audio_finished_event)
            i += 1
    
    def on_send(self, event=None) -> None:
        print("Send button clicked!")
        # Fetch the user prompt as a parameter
        user_input = self.view.drain_text()
        self.view.display_chat_message("User", user_input)
        self.view.disable_send()
        self.executor.submit(self.send_thread, user_input)

    def send_thread(self, user_input):
        # Generate the scene (and play the vamping audio)
        scene = self.generate_scene(user_input)
        
        # Play the scene
        self.play_scene(scene)

    def on_skip(self) -> None:
        print("Skip button clicked!")
        self.cancel_narration_token["value"] = True
        # self.view.enable_text_and_send_button()

    def on_initial_skip(self) -> None:
        self.on_skip()
        self.view.disable_send()

    def on_initial_skip(self) -> None:
        print("Skip button clicked!")
        self.cancel_narration_token["value"] = True
        self.view.enable_text_and_send_button()

    def on_exit(self) -> None:
        print("Exiting the application")
        self.cancel_music_token["value"] = True # sa.stop_all() may also work, but is buggier
        self.cancel_sfx_token["value"] = True
        self.cancel_narration_token["value"] = True
        sa.stop_all()
        self.executor.shutdown(wait=False)
        self.view.quit()