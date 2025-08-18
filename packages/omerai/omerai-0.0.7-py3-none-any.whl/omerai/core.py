import requests
import base64

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
            self._print_imgbb_url()

    def _print_imgbb_url(self):
        try:
            url = f"{_get_api_url()}apikey={self.key}&prompt={self._prompt.replace(' ', '%20')}"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Request failed: {response.status_code}")
                return

            data = response.json()
            imgbb_url = data.get("imgbb_url")
            if imgbb_url:
                print(imgbb_url)
            else:
                print("No imgbb_url found in response.")

        except Exception as e:
            print("Error:", e)