import requests

class Client:
    def __init__(self, token, base_url="https://soundrush.live/api_dev"):
        self.token = token
        self.base_url = base_url
        
    def _handle_json_response(self, response, method_name=""):
        """Helper method to handle JSON responses and errors consistently"""
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Error: Could not decode JSON response from {method_name}. Status code: {response.status_code}")
            print(f"Response text: {response.text}")
            return {"error": "Invalid JSON response", "status_code": response.status_code}


    def get(self, endpoint):
        response = requests.get(self.base_url+endpoint, headers={"Authorization": self.token})
        return self._handle_json_response(response, "GET")
        
    def post(self, endpoint, data=None):
        response = requests.post(self.base_url+endpoint, headers={"Authorization": self.token}, json=data)
        return self._handle_json_response(response, "POST")
        
    def put(self, endpoint, data=None):
        response = requests.put(self.base_url+endpoint, headers={"Authorization": self.token}, json=data)
        return self._handle_json_response(response, "PUT")
        
    def delete(self, endpoint):
        response = requests.delete(self.base_url+endpoint, headers={"Authorization": self.token})
        return self._handle_json_response(response, "DELETE")
        
    def patch(self, endpoint, data=None):
        response = requests.patch(self.base_url+endpoint, headers={"Authorization": self.token}, json=data)
        return self._handle_json_response(response, "PATCH")


    # Методы для создания экземпляров модулей API
    def auth(self):
        from .auth import Auth
        return Auth(self)
        
    def user(self):
        from .user import User
        return User(self)
        
    def bots(self):
        from .bots import Bots
        return Bots(self)
        
    def templates(self):
        from .templates import Templates
        return Templates(self)
        
    def media(self):
        from .media import Media
        return Media(self)
        
    def visual_editor(self):
        from .visual_editor import VisualEditor
        return VisualEditor(self)
        
    def admin(self):
        from .admin import Admin
        return Admin(self)
        
    def system(self):
        from .system import System
        return System(self)


if __name__ == "__main__":
    client = Client("123")
    # Get user data
    get_result = client.get("/api/user/info")
    print("GET result:", get_result)
    
    # Post user data using user module
    user = client.user()
    user_info = user.get_info()
    print("User info:", user_info)
