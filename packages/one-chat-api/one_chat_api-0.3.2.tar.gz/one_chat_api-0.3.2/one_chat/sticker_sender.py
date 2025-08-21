# one_chat/sticker_sender.py

import requests


class StickerSender:
    def __init__(self, authorization_token: str):
        if authorization_token.startswith("Bearer "):
            authorization_token = authorization_token.replace("Bearer ", "", 1)
        self.authorization_token = authorization_token
        self.api_url = "https://chat-api.one.th/message/api/v1/push_message"

    def send_sticker(
        self, to: str, bot_id: str, sticker_id: str, custom_notification: str = None
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {self.authorization_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "to": to,
            "bot_id": bot_id,
            "type": "sticker",
            "sticker_id": sticker_id,
            "custom_notification": custom_notification,
        }

        response = requests.post(self.api_url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "fail",
                "message": response.json().get("message", "Error sending sticker."),
            }
