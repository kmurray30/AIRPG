import os

import openai
from openai import OpenAI
from utils.file_utils import init_dotenv
from config.constants import flags, art_styles
from concurrent.futures import Future
from utils.file_utils import format_path_from_root
from concurrent.futures import ThreadPoolExecutor
import random
import urllib.request
import traceback

class ChatSession:
    # ChatGPT Model
    open_ai_client: OpenAI

    # Message history for the ChatGPT
    chat_messages: list

    # System prompt options
    dm_system_prompt = "You are a table top role playing game dungeon master. Please always limit your responses to a few sentences."
    
    # Image prompt
    image_prompt = f"Generate the following scene in the a {art_styles.STUDIO_GHIBLI} style, making sure to include a character that looks like aragorn from The Lord of the Rings, and don't include any text: "

    # Custom GPT error response
    custom_gpt_error_response = "Something went wrong while generating the response"

    # Executor
    executor: ThreadPoolExecutor

    def __init__(self, system_prompt: str, executor: ThreadPoolExecutor):
        # Load the OpenAI API key from the .env file and initialize the OpenAI client
        init_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.open_ai_client = OpenAI()
        self.chat_messages = []
        self.executor = executor

    # Function to call the OpenAI API
    def _call_openai_chat(self, messages):
        try:
            response = self.open_ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                # model="gpt-4-turbo-preview",
                # model="gpt-4-0125-preview",
                messages=messages
            )
            chat_response = response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred while calling the OpenAI chat API")
            traceback.print_exc()
            chat_response = self.custom_gpt_error_response
        return chat_response

    def _call_openai_image(self, prompt):
        try:
            response = self.open_ai_client.images.generate(
                    model="dall-e-3", # options: dall-e-3, dall-e-2
                    prompt=prompt,
                    size="1024x1024", # options: 1024x1024, 1024x1792 or 1792x1024
                    quality="standard", # options: standard, hd
                    n=1
                )
            print(f"Image file url returned: {response.data[0].url}")
            image_url = response.data[0].url
            image_path = format_path_from_root(f"generated/temp/temp{random.randint(0, 1000000)}.png")
            urllib.request.urlretrieve(image_url, image_path)
            return image_path
        except Exception as e:
            print(f"An error occurred while generating the image")
            traceback.print_exc()
            raise(e)
    
    def _call_openai_audio(self, prompt, file_path) -> str:
        with (
            self.open_ai_client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="echo",
                input=prompt,
                response_format="wav"
            )
        ) as response:
            if response.status_code != 200:
                print(f"Failed to convert the text to speech. Status code: {response.status_code}")
                raise Exception("Failed to convert the text to speech")
                return
            print(f"response for audio file {file_path}: {response}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            response.stream_to_file(file_path)
        return file_path
    
    def _call_openai_one_off(self, prompt, custom_system_context = "You are a helpful assistant."):
        chatGptMessages = [
            {"role": "system", "content": custom_system_context},
            {"role": "user", "content": prompt}
        ]
        return self._call_openai_chat(chatGptMessages)

    # TODO make these more thread safe (can set up a buffer or smth)
    def append_user_input_and_get_response(self, user_input: str) -> str:
        # Create a deep copy of the chat messages to avoid race conditions
        chat_messages = self.chat_messages.copy()
        chat_messages.append({"role": "user", "content": user_input})
        chat_messages.insert(0, {"role": "system", "content": self.dm_system_prompt})
        response = self._call_openai_chat(chat_messages)
        chat_messages.append({"role": "assistant", "content": response})
        chat_messages.pop(0) # Don't persist the system prompt
        self.chat_messages = chat_messages # Update the chat messages
        return response
    
    def generate_vamp_response(self, user_input: str, vamp_prompt: str) -> str:
        chat_messages = self.chat_messages.copy()
        input = f"{vamp_prompt}: {user_input}"
        chat_messages.append({"role": "user", "content": input})
        response = self._call_openai_chat(chat_messages)
        return response
    
    # Generate image
    def generate_image(self, gtp_scene_description) -> str:
        # Generate the image from the scene description (non-blocking)
        if flags.DEBUG or self.custom_gpt_error_response in gtp_scene_description: # TODO replace this
            image_path_future = Future()
            image_path_future.set_result(format_path_from_root("assets/sample_tavern_art.png"))
        else:
            prompt = self.image_prompt + gtp_scene_description
            image_path_future = self.executor.submit(self._call_openai_image, prompt)
            if image_path_future.exception():
                print(f"An error occurred while generating the image")
                print(f"Returning a placeholder image")
                image_path_future = Future()
                image_path_future.set_result(format_path_from_root("assets/sample_tavern_art.png"))
        return image_path_future
    
    def generate_narration(self, gtp_scene_description) -> Future[str]:
        # Generate the audio from the scene description (non-blocking)
        if flags.DEBUG:
            file_future = Future[str]()
            file_future.set_result(format_path_from_root("assets/sample_tavern_audio.mp3"))
        else:
            file_path = self._generate_audio_file_path(gtp_scene_description, summary_as_filename=False, delete=True)
            file_future = self.executor.submit(self._call_openai_audio, gtp_scene_description, file_path)
        return file_future
    
    def _generate_audio_file_path(self, prompt, summary_as_filename=False, delete=True):
        # Generate a file name based on the user input, or some generic name
        if delete:
            path = format_path_from_root("generated/temp/")
        else:
            path = format_path_from_root("generated/")
        if summary_as_filename:
            summary = self._call_openai_one_off("Summarize the following into 1-4 words (and no special characters): " + prompt).rstrip('.')
            speech_file_name = f"{summary}.wav"
            speech_file_path = path + speech_file_name
        else:
            speech_file_name = f"speech{str(hash(prompt))}.wav"
            speech_file_path = path + speech_file_name
        return speech_file_path