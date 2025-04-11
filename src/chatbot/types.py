from typing import Generator, Literal, TypedDict


class ChatHistory(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class ChatHistoryItem(TypedDict):
    user_message: str
    assistant_message: str
    emotion: int


type StreamedResponse = Generator[str, None, None]

__all__ = ["ChatHistory", "StreamedResponse"]
