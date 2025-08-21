# one_chat/friend_and_group_manager.py

import requests


class FriendAndGroupManager:
    def __init__(self, authorization_token: str):
        if authorization_token.startswith("Bearer "):
            authorization_token = authorization_token.replace("Bearer ", "", 1)
        self.authorization_token = authorization_token
        self.base_url = "https://chat-api.one.th/manage/api/v1/getlistroom"
        self.headers = {
            "Authorization": f"Bearer {self.authorization_token}",
            "Content-Type": "application/json",
        }

    def fetch_friends_and_groups(self, bot_id: str) -> dict:
        payload = {"bot_id": bot_id}
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)

            if response.status_code == 200:
                return response.json()
            else:
                return self._handle_error(response)
        except requests.exceptions.RequestException as e:
            return {"status": "fail", "message": f"Request failed: {str(e)}"}

    def list_all_friends(self, bot_id: str) -> dict:
        try:
            response = self.fetch_friends_and_groups(bot_id)
            if response.get("status") == "success":
                return response.get("list_friend", [])
            return []
        except requests.exceptions.RequestException as e:
            return {"status": "fail", "message": f"Request failed: {str(e)}"}

    def list_friend_ids(self, bot_id: str) -> dict:
        try:
            response = self.fetch_friends_and_groups(bot_id)
            if response.get("status") == "success":
                return [friend["one_id"] for friend in response.get("list_friend", [])]
            return []
        except requests.exceptions.RequestException as e:
            return {"status": "fail", "message": f"Request failed: {str(e)}"}

    def list_all_groups(self, bot_id) -> dict:
        try:
            response = self.fetch_friends_and_groups(bot_id)
            if response.get("status") == "success":
                return response.get("list_group", [])
            return []
        except requests.exceptions.RequestException as e:
            return {"status": "fail", "message": f"Request failed: {str(e)}"}

    def list_group_ids(self, bot_id) -> dict:
        try:
            response = self.fetch_friends_and_groups(bot_id)
            if response.get("status") == "success":
                return [group["group_id"] for group in response.get("list_group", [])]
            return []
        except requests.exceptions.RequestException as e:
            return {"status": "fail", "message": f"Request failed: {str(e)}"}

    def _handle_error(self, response: requests.Response) -> dict:
        try:
            error_response = response.json()
            return {
                "status": error_response.get("status", "fail"),
                "message": error_response.get("message", "Unknown error occurred."),
            }
        except ValueError:
            return {"status": "fail", "message": "Invalid response from the server."}
