
class ChatSession:
    messages = []
    
    def __init__(self, system_prompt):
        self.messages = [
        {
            "role": "system",
            "content": """
            You are a table top role playing game dungeon master. Please always limit your responses to a few sentences.
            """}
    ]