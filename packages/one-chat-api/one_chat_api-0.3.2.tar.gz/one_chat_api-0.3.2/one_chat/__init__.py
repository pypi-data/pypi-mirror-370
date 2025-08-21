# one_chat/__init__.py

from .one_chat import OneChat

ONE_CHAT_INSTANCE = None
DEFAULT_TO = None
DEFAULT_BOT_ID = None


def init(authorization_token: str, to: str = None, bot_id: str = None):
    global ONE_CHAT_INSTANCE, DEFAULT_TO, DEFAULT_BOT_ID
    ONE_CHAT_INSTANCE = OneChat(authorization_token)
    DEFAULT_TO = to
    DEFAULT_BOT_ID = bot_id


def send_message(
    to: str = None,
    bot_id: str = None,
    message: str = None,
    custom_notification: str = None,
):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.send_message(to, bot_id, message, custom_notification)


def send_template(
    to: str = None,
    bot_id: str = None,
    template: list = None,
    custom_notification: str = None,
):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.send_template(to, bot_id, template, custom_notification)


def send_file(
    to: str = None,
    bot_id: str = None,
    file_path: str = None,
    custom_notification: str = None,
):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.send_file(to, bot_id, file_path, custom_notification)


def send_webview(
    to: str = None, bot_id: str = None, url: str = None, custom_notification: str = None
):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.send_webview(to, bot_id, url, custom_notification)


def broadcast_message(bot_id: str = None, to: str = None, message: str = None):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.broadcast_message(bot_id, [to], message)


def send_location(
    to: str = None,
    bot_id: str = None,
    latitude: str = None,
    longitude: str = None,
    address: str = None,
    custom_notification: str = None,
):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.send_location(
        to, bot_id, latitude, longitude, address, custom_notification
    )


def send_sticker(
    to: str = None,
    bot_id: str = None,
    sticker_id: str = None,
    custom_notification: str = None,
):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.send_sticker(to, bot_id, sticker_id, custom_notification)


def send_quickreply(
    to: str = None,
    bot_id: str = None,
    message: str = None,
    quick_reply: list = None,
    custom_notification: str = None,
):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.send_quickreply(
        to, bot_id, message, quick_reply, custom_notification
    )


def send_image_carousel(
    to: str = None,
    bot_id: str = None,
    elements: list = None,
    custom_notification: str = None,
):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    to = to or DEFAULT_TO
    bot_id = bot_id or DEFAULT_BOT_ID

    if not to or not bot_id:
        raise ValueError(
            "Both 'to' and 'bot_id' must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.send_image_carousel(
        to, bot_id, elements, custom_notification
    )


def fetch_friends_and_groups(bot_id: str = None):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    bot_id = bot_id or DEFAULT_BOT_ID

    if not bot_id:
        raise ValueError(
            "Bot ID must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.fetch_friends_and_groups(bot_id)


def list_all_friends(bot_id: str = None):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    bot_id = bot_id or DEFAULT_BOT_ID

    if not bot_id:
        raise ValueError(
            "Bot ID must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.list_all_friends(bot_id)


def list_friend_ids(bot_id: str = None):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    bot_id = bot_id or DEFAULT_BOT_ID

    if not bot_id:
        raise ValueError(
            "Bot ID must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.list_friend_ids(bot_id)


def list_all_groups(bot_id: str = None):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    bot_id = bot_id or DEFAULT_BOT_ID

    if not bot_id:
        raise ValueError(
            "Bot ID must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.list_all_groups(bot_id)


def list_group_ids(bot_id: str = None):
    if ONE_CHAT_INSTANCE is None:
        raise Exception(
            "OneChat is not initialized. Call init(authorization_token, to, bot_id) first."
        )

    bot_id = bot_id or DEFAULT_BOT_ID

    if not bot_id:
        raise ValueError(
            "Bot ID must be provided either during initialization or when calling this method."
        )

    return ONE_CHAT_INSTANCE.list_group_ids(bot_id)
