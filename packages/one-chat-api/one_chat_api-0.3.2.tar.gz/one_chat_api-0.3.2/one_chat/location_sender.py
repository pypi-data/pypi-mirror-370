import requests


class LocationSender:
    def __init__(self, authorization_token: str):
        if authorization_token.startswith("Bearer "):
            authorization_token = authorization_token.replace("Bearer ", "", 1)
        self.authorization_token = authorization_token
        self.url = "https://chat-api.one.th/message/api/v1/push_message"

    def send_location(
        self,
        to: str,
        bot_id: str,
        latitude: str,
        longitude: str,
        address: str,
        custom_notification: str = None,
    ) -> dict:
        headers = {
            "Authorization": f"Bearer {self.authorization_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "to": to,
            "bot_id": bot_id,
            "type": "location",
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "custom_notification": custom_notification,
        }

        response = requests.post(self.url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return response.json()
