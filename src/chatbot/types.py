from typing import Generator, Literal, TypedDict, Union


class ChatHistory(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class ChatHistoryItem(TypedDict):
    user_message: str
    assistant_message: str
    emotion: int


type StreamedResponse = Generator[str, None, None]


class SystemPromptFile(TypedDict):
    """
    Represents a system prompt provided as a file.

    Attributes:
        type (str): The type of the system prompt, always "file".
        path (str): The file path to the system prompt.
    """

    type: Literal["file"]  # "file"
    path: str


class SystemPromptText(TypedDict):
    """
    Represents a system prompt provided as a text string.

    Attributes:
        type (str): The type of the system prompt, always "text".
        content (str): The text content of the system prompt.
    """

    type: Literal["text"]  # "text"
    content: str


type SystemPrompt = Union[SystemPromptFile, SystemPromptText]


class AgentConfig(TypedDict, total=False):
    """
    Represents the configuration for an agent.

    Attributes:
        model (str): The model used by the agent.
        baseURL (str): The URL of the LLM server API.
        apiKey (str): The API key used by the LLM server.
        systemPrompt (SystemPrompt): The system prompt, either as a file or text.
        temperature (float, optional): The temperature used by the model. Default is 0.7.
        historyLimit (int, optional): The maximum number of history records to use as context. Default is 20.
        maxTokens (int, optional): The maximum number of tokens to use in the response. Default is 2048.
    """

    model: str
    baseURL: str
    apiKey: str
    systemPrompt: SystemPrompt
    temperature: float | None  # Optional, default is 0.7
    historyLimit: int | None  # Optional, default is 20
    maxTokens: int | None  # Optional, default is 2048
