from typing import Generator, Literal, TypedDict, Union


class ChatHistoryV0Item(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class ChatHistoryV1Item(TypedDict):
    user_message: str
    assistant_message: str
    emotion: int


class ChatHistoryV1(TypedDict):
    version: Literal["v1"]
    history: list[ChatHistoryV1Item]


type StreamedResponse = Generator[str, None, None]


class PromptFile(TypedDict):
    """
    Represents a system prompt provided as a file.

    Attributes:
        type (str): The type of the system prompt, always "file".
        path (str): The file path to the system prompt.
    """

    type: Literal["file"]  # "file"
    path: str


class PromptText(TypedDict):
    """
    Represents a system prompt provided as a text string.

    Attributes:
        type (str): The type of the system prompt, always "text".
        content (str): The text content of the system prompt.
    """

    type: Literal["text"]  # "text"
    content: str


type PromptSchema = Union[PromptFile, PromptText]


class AgentConfig(TypedDict, total=False):
    """
    Represents the configuration for an agent.

    Attributes:
        model (str): The model used by the agent.
        baseURL (str): The URL of the LLM server API.
        apiKey (str): The API key used by the LLM server.
        agentDescription (PromptSchema, optional): The prompt to be used by the agent. It can be either a file or a text string.
        userDescription (PromptSchema, optional): The prompt to be used by the user. It can be either a file or a text string.
        temperature (float, optional): The temperature used by the model. Default value is 0.7.
        historyLimit (int, optional): The maximum number of history records to be used as the context. Default is 20. Note that one pair of user-assistant chat history is counted as one record.
        maxTokens (int, optional): The maximum number of tokens to be used in the response. Default value is 2048.
    """

    model: str
    baseURL: str
    apiKey: str
    agentDescription: PromptSchema | None
    userDescription: PromptSchema | None
    temperature: float | None  # Optional, default is 0.7
    historyLimit: int | None  # Optional, default is 20
    maxTokens: int | None  # Optional, default is 2048
