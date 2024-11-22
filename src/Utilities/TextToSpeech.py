import os
from pathlib import Path
from os import environ

import openai
# from dotenv import load_dotenv
from openai import OpenAI

filename = os.path.splitext(os.path.basename(__file__))[0]
if __name__ == "__main__" or __name__ == filename: # If the script is being run directly
    from ChatBot import call_openai_without_context  # Relative import for direct execution
    from Utilities import (get_path_from_project_root, init_dotenv)
else: # If the script is being imported
    from .ChatBot import call_openai_without_context  # Package-relative import for when imported by other modules
    from .Utilities import (get_path_from_project_root, init_dotenv)

# load_dotenv()
init_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

import simpleaudio as sa

def play_audio_file(file_path):
    try:
        # Load the audio file from the provided path
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        
        # Play the audio
        play_obj = wave_obj.play()
        
        # Wait for the audio to finish playing
        play_obj.wait_done()
    except Exception as e:
        print(f"An error occurred while playing the audio: {e}")

def cancel_audio():
    sa.stop_all()

def delete_audio_file(file_path):
    # only delete audio files in the generated directory
    if os.path.exists(file_path) and "/generated/" in file_path and Path(file_path).suffix == ".wav":
        os.remove(file_path)
    else:
        print("The file does not exist")

def convert_text_to_speech_file(prompt, file_path):
    with (client.audio.speech.with_streaming_response.create(
      model="tts-1",
      voice="echo",
      input=prompt,
      response_format="wav"
    )) as response:
        if response.status_code != 200:
            print(f"Failed to convert the text to speech. Status code: {response.status_code}")
            return
        print("response: ", response)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        response.stream_to_file(file_path)

def generate_audio_file(prompt, summary_as_filename=False, delete=True):
    # Generate a file name based on the user input, or some generic name
    if delete:
        path = get_path_from_project_root("generated/temp/")
    else:
        path = get_path_from_project_root("generated/")
    if summary_as_filename:
        summary = call_openai_without_context("Summarize the following into 1-4 words (and no special characters): " + prompt).rstrip('.')
        speech_file_name = f"{summary}.wav"
        speech_file_path = path + speech_file_name
    else:
        speech_file_name = f"speech{str(hash(prompt))}.wav"
        speech_file_path = path + speech_file_name
    return speech_file_path

def convert_play_delete_text_to_speech_file(prompt, summary_as_filename=False, delete=True):
    try:
        # Generate the speech file path
        speech_file_path = generate_audio_file(prompt, summary_as_filename, delete)

        # Generate the speech file
        convert_text_to_speech_file(prompt, speech_file_path)

        # Play the speech file
        play_audio_file(speech_file_path)

        # Delete the speech file
        if delete:
            delete_audio_file(speech_file_path)
    except Exception as e:
        print(f"An error occurred while converting the text to speech: {e}")

def main():
    print("Welcome to the Text to Speech Converter!")
    while True:
        user_input = input("\nEnter the text you would like to convert to speech (type 'exit' to quit):\n")
        if user_input.lower() == "exit":
            break
        if user_input:
            convert_play_delete_text_to_speech_file(user_input)      

if __name__ == "__main__":
    main()