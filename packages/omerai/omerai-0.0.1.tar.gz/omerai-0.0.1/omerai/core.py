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
        self.prompt = ""

        # Auto-generate if prompt and key are set when file is run
        self._auto_generate()

    def _auto_generate(self):
        """
        Checks if key & prompt are set as environment variables and auto-generates image.
        """
        prompt = os.getenv("OMERAI_PROMPT", self.prompt)
        key = os.getenv("OMERAI_KEY", self.key)

        if key and prompt:
            self.prompt = prompt
            self.key = key
            self._generate_image()

    def _generate_image(self):
        try:
            url = f"{_get_api_url()}apikey={self.key}&prompt={self.prompt.replace(' ', '%20')}"
            response = requests.get(url)
            if response.status_code != 200:
                raise RuntimeError(f"API request failed {response.status_code}")

            data = response.json()
            if "image" not in data:
                raise RuntimeError(f"No image returned by API: {data}")

            img_bytes = base64.b64decode(data["image"])
            save_path = f"{self.prompt.replace(' ', '_')}.png"
            with open(save_path, "wb") as f:
                f.write(img_bytes)

            print(f"Image saved as: {save_path}")
        except Exception as e:
            print(f"Image generation failed: {e}")
