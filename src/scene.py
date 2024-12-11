
class Scene:
    chatGPT_response: str
    music_path: str
    narration_path: str
    image_path: str

    def __init__(self, chatGPT_response: str, music_path: str, narration_path: str, image_path: str):
        self.chatGPT_response = chatGPT_response
        self.music_path = music_path
        self.narration_path = narration_path
        self.image_path = image_path
    
    # Getters
    def get_chatGPT_response(self) -> str:
        return self.chatGPT_response
    
    def get_music_path(self) -> str:
        return self.music_path
    
    def get_narration_path(self) -> str:
        return self.narration_path
    
    def get_image_path(self) -> str:
        return self.image_path
    
    # Truncate the message if it exceeds the max length, rounding down to the nearest word
    def truncate_message(self, message: str, max_length: int) -> str:
        if len(message) > max_length:
            trunacted = message[:max_length]
            index_of_last_space = trunacted.rfind(" ")
            return trunacted[:index_of_last_space] + "..."
    
    def __str__(self) -> str:
        return f"""
        ChatGPT Response: {self.truncate_message(self.chatGPT_response, 32)}
        Music Path: {self.music_path}
        Narration Path: {self.narration_path}
        Image Path: {self.image_path}
        """