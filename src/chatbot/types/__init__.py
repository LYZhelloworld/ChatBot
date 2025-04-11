from typing import Generator, Literal, TypedDict


class ChatHistory(TypedDict):
    role: Literal["user", "assistant"]
    content: str


type StreamedResponse = Generator[str, None, None]

__all__ = ["ChatHistory", "StreamedResponse"]
