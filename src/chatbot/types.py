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


class ModelParams(TypedDict, total=False):
    """
    The parameters passed to the model.

    Attributes:
        temperature (float, optional): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
        top_p (float, optional): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
    """

    temperature: float | None
    top_p: float | None


class AgentConfig(TypedDict, total=False):
    """
    Represents the configuration for an agent.

    Attributes:
        model (str): The model used by the agent.
        baseURL (str): The URL of the LLM server API.
        apiKey (str): The API key used by the LLM server.
        agentDescription (PromptSchema, optional): The prompt to be used by the agent. It can be either a file or a text string.
        userDescription (PromptSchema, optional): The prompt to be used by the user. It can be either a file or a text string.
        historyLimit (int, optional): The maximum number of history records to be used as the context. Default is 20. Note that one pair of user-assistant chat history is counted as one record.
        modelParams (optional): The parameters passed to the model.
    """

    model: str
    baseURL: str
    apiKey: str
    agentDescription: PromptSchema | None
    userDescription: PromptSchema | None
    historyLimit: int | None  # Optional, default is 20
    modelParams: ModelParams | None
