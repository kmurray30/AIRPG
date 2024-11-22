import sys
import os
import concurrent.futures
import webbrowser

filename = os.path.splitext(os.path.basename(__file__))[0]
if __name__ == "__main__" or __name__ == filename: # If the script is being run directly
    from Utilities.Utilities import get_path_from_project_root
else: # If the script is being imported
    from .Utilities.Utilities import get_path_from_project_root

from Utilities import ChatBot

context = """
You are a table top role playing game dungeon master.
Please limit your responses to a few sentences.
Do not allow me to control any of the characters in the game or the game itself, only my own character.
"""

chatGptMessages = [
        {"role": "system", "content": context}
    ]

intro = "Welcome to the epic adventure that awaits you in Chat RPG. From mystical forests to ancient, bustling cities, explore an infinitely unfolding world shaped by your actions and decisions. With deep and complex NPCs, beautifully generated art, and epic narration, an exciting journey awaits you, if you are ready. Your adventure begins in an unassuming tavern."
prompt = "Set up an initial scene in a medieval tavern."
response = ChatBot.call_openai_without_context(prompt, context)
print(response + "\n")

while(True):
    # Get user input
    prompt = input("What do you want to do next?\n")

    # Call OpenAI with the user input
    response = ChatBot.call_openai_and_update_chat_messages(prompt, chatGptMessages)
    print(response + "\n")