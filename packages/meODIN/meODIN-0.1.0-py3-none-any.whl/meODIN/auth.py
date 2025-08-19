import requests

class Authenticator:
    def __init__(self, token, auth_url="https://www.meodin.eu/api/validate_token"):
        self.token = token
        self.auth_url = auth_url

    def is_token_valid(self):
        try:
            response = requests.post(self.auth_url, json={"token": self.token}, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print("Authentication failed:", e)
            return False
