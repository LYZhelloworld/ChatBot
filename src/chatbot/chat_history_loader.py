import json
from typing import Any

from jsonschema import ValidationError

from emotion.emotion import DEFAULT_EMOTION
from .types import ChatHistoryV0Item, ChatHistoryV1
from .validators.validator import validate
from .validators.chat_history import schema_v0, schema_v1


def chat_history_converter_v0(historyV0: list[ChatHistoryV0Item]) -> ChatHistoryV1:
    """
    Converts a list of ChatHistoryV0Item to ChatHistoryV1 format.

    :param historyV0: The chat history in V0 format.
    :return: The chat history in V1 format.
    :rtype: ChatHistoryV1
    """
    iterator = iter(historyV0)
    result: ChatHistoryV1 = {
        "version": "v1",
        "history": [],
    }

    try:
        while True:
            user = next(iterator)
            assistant = next(iterator)
            result["history"].append({
                "user_message": user["content"],
                "assistant_message": assistant["content"],
                "emotion": DEFAULT_EMOTION,
            })
    except StopIteration:
        pass

    return result


def is_schema(file_content: Any, schema: Any) -> bool:
    """
    Checks if the given file content is in V1 format.

    :param file_content: The content of the file to check.
    :return: True if the file content is in V1 format, False otherwise.
    :rtype: bool
    """
    try:
        validate(file_content, schema)
        return True
    except ValidationError:
        return False


def load_chat_history(path: str) -> ChatHistoryV1:
    """
    Loads a given chat history.

    :param str path: The path to the chat history file.
    :return: The loaded chat history.
    :rtype: ChatHistoryV1
    """
    with open(path, "r", encoding="utf-8") as file:
        file_content = json.load(file)

    if is_schema(file_content, schema_v1):
        return file_content

    if is_schema(file_content, schema_v0):
        return chat_history_converter_v0(file_content)

    raise ValueError('Invalid chat history format.')
