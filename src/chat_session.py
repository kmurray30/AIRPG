
class ChatSession:
    messages = []
    
    def __init__(self, system_prompt):
        self.messages = [
        {
            "role": "system",
            "content": f"""
            {system_prompt}
            """}
        ]