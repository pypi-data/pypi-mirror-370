import requests
import base64

# 🤫 Obfuscated API URL
_OBF_API_URL = "aHR0cHM6Ly9hbWVyaWNhbmV3cy52ZXJjZWwuYXBwL2FwaS9nZW5lcmF0ZT8="

def _get_api_url():
    return base64.b64decode(_OBF_API_URL).decode()

class DreamRender:
    def __init__(self, key=""):
        self.key = key
        self._prompt = None
        self.last_image_path = None  # store last generated image path

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self, value):
        self._prompt = value
        if self.key and self._prompt:
            self.last_image_path = self._generate_image()
        elif not self.key:
            print("No API key set. Image generation skipped.")
            self.last_image_path = None

    def _generate_image(self):
        try:
            url = f"{_get_api_url()}apikey={self.key}&prompt={self._prompt.replace(' ', '%20')}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"API request failed {response.status_code}")
                return None

            data = response.json()
            if "image" not in data:
                print(f"No image returned by API: {data}")
                return None

            img_bytes = base64.b64decode(data["image"])
            save_path = f"{self._prompt.replace(' ', '_')}.png"
            with open(save_path, "wb") as f:
                f.write(img_bytes)

            print(f"Image saved as: {save_path}")
            return save_path

        except Exception as e:
            print(f"Image generation failed: {e}")
            return None
