import requests
import base64
import os

# 🤫 Obfuscated API URL
_OBF_API_URL = "aHR0cHM6Ly9hbWVyaWNhbmV3cy52ZXJjZWwuYXBwL2FwaS9nZW5lcmF0ZT8="

def _get_api_url():
    return base64.b64decode(_OBF_API_URL).decode()

class DreamRender:
    def __init__(self, key=""):
        self.key = key
        self._prompt = None

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self, value):
        self._prompt = value
        if self.key and self._prompt:
            self._generate_image()
        # if key not set, do nothing

    def _generate_image(self):
        try:
            url = f"{_get_api_url()}apikey={self.key}&prompt={self._prompt.replace(' ', '%20')}"
            response = requests.get(url)

            if response.status_code != 200:
                return  # fail silently

            data = response.json()
            # take only the base64 image part
            img_base64 = data.get("image")
            if not img_base64:
                return  # nothing to save

            img_bytes = base64.b64decode(img_base64)
            # save to same directory as this script
            save_path = os.path.join(os.path.dirname(__file__), f"{self._prompt.replace(' ', '_')}.png")
            with open(save_path, "wb") as f:
                f.write(img_bytes)

        except:
            pass  # fail silently
