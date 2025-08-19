from rubigram.types import Update, InlineMessage
from typing import Union, Callable, Awaitable
import re


class Filter:
    def __init__(self, func: Callable[[Union[Update, InlineMessage]], bool | Awaitable[bool]]):
        self.func = func

    async def __call__(self, update: Union[Update, InlineMessage]) -> bool:
        result = self.func(update)
        if isinstance(result, Awaitable):
            return await result
        return result

    def __and__(self, other: "Filter"):
        async def combined(update):
            return await self(update) and await other(update)
        return Filter(combined)

    def __or__(self, other: "Filter"):
        async def combined(update):
            return await self(update) or await other(update)
        return Filter(combined)


class command(Filter):
    def __init__(self, cmd: Union[str, list[str]], prefix: str = "/"):
        self.cmd = cmd
        self.prefix = prefix
        super().__init__(self.filter)

    def filter(self, update: Update):
        commands = [self.cmd] if isinstance(self.cmd, str) else self.cmd
        text = ""
        if isinstance(update, Update):
            if update.type == "NewMessage":
                text = update.new_message.text
            elif update.type == "UpdatedMessage":
                text = update.updated_message.text
            if text:
                for cmd in commands:
                    if text.lower().startswith(self.prefix + cmd.lower()):
                        return True
                return False


class regex(Filter):
    def __init__(self, pattern: str):
        self.pattern = pattern
        super().__init__(self.filter)

    def filter(self, update: Union[Update, InlineMessage]):
        text = ""
        if isinstance(update, Update):
            if update.type == "NewMessage":
                text = getattr(update.new_message, "text", "")
            elif update.type == "UpdatedMessage":
                text = getattr(update.updated_message, "text", "")
        elif isinstance(update, InlineMessage):
            text = getattr(update, "text", "")

        if text:
            return bool(re.search(self.pattern, text))
        return False


class chat(Filter):
    def __init__(self, chat_id: Union[str, list[str]]):
        self.chat_id = chat_id
        super().__init__(self.filter)

    def filter(self, update: Union[Update, InlineMessage]):
        chat_ids = [self.chat_id] if isinstance(
            self.chat_id, str) else self.chat_id
        return update.chat_id in chat_ids


class button(Filter):
    def __init__(self, button_id: Union[str, list[str]]):
        self.button_id = button_id
        super().__init__(self.filter)

    def filter(self, update: InlineMessage):
        if isinstance(update, InlineMessage):
            button_ids = [self.button_id] if isinstance(
                self.button_id, str) else self.button_id
            return update.aux_data.button_id in button_ids



def TEXT(update: Update):
    return bool(update.new_message and getattr(update.new_message, "text", None))


def FILE(update: Update):
    return bool(update.new_message and getattr(update.new_message, "file", None))


def LIVE(update: Update):
    return bool(update.new_message and getattr(update.new_message, "live_location", None))


def POLL(update: Update):
    return bool(update.new_message and getattr(update.new_message, "poll", None))


def CONTACT(update: Update):
    return bool(update.new_message and getattr(update.new_message, "contact_message", None))


def STICKER(update: Update):
    return bool(update.new_message and getattr(update.new_message, "sticker", None))


def LOCATION(update: Update):
    return bool(update.new_message and getattr(update.new_message, "location", None))


def FORWARD(update: Update):
    return bool(update.new_message and getattr(update.new_message, "forwarded_from", None))


def EDITED(update: Update):
    if isinstance(update, Update) and update.type == "UpdatedMessage":
        return update.updated_message.is_edited


def PRIVATE(update: Update):
    if isinstance(update, Update) and update.type == "NewMessage":
        return update.new_message.sender_type in ["User", "Bot"]
    return False


def FORWARD_BOT(update: Update):
    if isinstance(update, Update) and update.type == "NewMessage" and update.new_message.forwarded_from:
        return update.new_message.forwarded_from.type_from == "Bot"
    return False


def FORWARD_USER(update: Update):
    if isinstance(update, Update) and update.type == "NewMessage" and update.new_message.forwarded_from:
        return update.new_message.forwarded_from.type_from == "User"
    return False


def FORWARD_CHANNEL(update: Update):
    if isinstance(update, Update) and update.type == "NewMessage" and update.new_message.forwarded_from:
        return update.new_message.forwarded_from.type_from == "Channel"
    return False


text = Filter(TEXT)
file = Filter(FILE)
live = Filter(LIVE)
poll = Filter(POLL)
edited = Filter(EDITED)
contact = Filter(CONTACT)
sticker = Filter(STICKER)
location = Filter(LOCATION)
forward = Filter(FORWARD)
private = Filter(PRIVATE)
forward_bot = Filter(FORWARD_BOT)
forward_user = Filter(FORWARD_USER)
forward_channel = Filter(FORWARD_CHANNEL)