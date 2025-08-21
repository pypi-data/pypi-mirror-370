# one_chat/quickreply_sender.py

import requests


class QuickReplySender:
    def __init__(self, authorization_token: str):
        if authorization_token.startswith("Bearer "):
            authorization_token = authorization_token.replace("Bearer ", "", 1)
        self.authorization_token = authorization_token
        self.base_url = "https://chat-api.one.th/message/api/v1/push_quickreply"
        self.headers = {
            "Authorization": f"Bearer {authorization_token}",
            "Content-Type": "application/json",
        }

    def send_quickreply(
        self,
        to: str,
        bot_id: str,
        message: str,
        quick_reply: list,
        custom_notification: str = None,
    ) -> dict:
        payload = {
            "to": to,
            "bot_id": bot_id,
            "message": message,
            "quick_reply": quick_reply,
        }
        if custom_notification:
            payload["custom_notification"] = custom_notification

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)

            if response.status_code == 200:
                return response.json()
            else:
                return self._handle_error(response)
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