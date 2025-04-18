import os
import json
import sys
import traceback

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk

from chatbot.types import ChatHistoryV0Item, StreamedResponse
from emotion.emotion import Emotion
from utils.utils import remove_think_tags
from .types import AgentConfig, ChatHistoryV1, SystemPrompt
from .validators.validator import validate
from .validators.agent_config import schema as agent_config_schema
from .validators.chat_history import schema_v0 as chat_history_schema_v0, schema_v1 as chat_history_schema_v1
from .prompts import system_prompt, agent_description_prompt, user_description_prompt


def chat_history_converter(historyV0: list[ChatHistoryV0Item]) -> ChatHistoryV1:
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
                "emotion": Agent.DEFAULT_EMOTION,
            })
    except StopIteration:
        pass

    return result


class Agent:
    __BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    __AGENT_FOLDER = os.path.join(__BASE_PATH, "agents")
    __CONFIG_FILE_NAME = "config.json"
    __HISTORY_FILE_NAME = "history.json"
    DEFAULT_EMOTION = 50

    def __init__(self, name: str):
        self.__name: str = name

        # Config file is located in `./agents/{agent_name}/config.json`.
        config_file_path = os.path.join(
            Agent.__AGENT_FOLDER, name, self.__CONFIG_FILE_NAME)
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(
                f"Agent '{self.name}' does not exist. Please create a config file at '{config_file_path}'."
            )

        with open(config_file_path, "r", encoding="utf-8") as file:
            config_file_content: AgentConfig = validate(
                json.load(file), agent_config_schema)

        # Load agent configuration from config file.
        self.__model: str = config_file_content.get("model")
        self.__temperature: float = config_file_content.get("temperature", 0.7)
        self.__history_limit: int = config_file_content.get("historyLimit", 20)
        self.__max_tokens: int = config_file_content.get("maxTokens", 2048)
        self.__history: ChatHistoryV1 = {"version": "v1", "history": []}

        # Load description from config file.
        self.__agent_description: str = self.__load_description(
            config_file_content.get("agentDescription"))
        self.__user_description: str = self.__load_description(
            config_file_content.get("userDescription"))

        # Create OpenAI client with the provided API key and base URL.
        self.__client: OpenAI = OpenAI(
            api_key=config_file_content.get("apiKey"),
            base_url=config_file_content.get("baseURL"),
        )

        # Load or create history file.
        history_file_path = os.path.join(os.path.dirname(
            config_file_path), Agent.__HISTORY_FILE_NAME)
        if not os.path.exists(history_file_path):
            self.save()
        else:
            try:
                self.__load_history(history_file_path)
            except Exception as e:
                print(f"Warning: {str(e)}")
                print("Cannot load history file. History will be empty.")

        # Create emotion instance.
        self.__emotion: Emotion = Emotion(
            self.__model, self.__client.base_url, config_file_content.get("apiKey"))

    @property
    def name(self) -> str:
        return self.__name

    @staticmethod
    def list_agents() -> list[str]:
        if not os.path.exists(Agent.__AGENT_FOLDER):
            return []

        if not os.path.isdir(Agent.__AGENT_FOLDER):
            raise NotADirectoryError(
                f"Agent folder '{Agent.__AGENT_FOLDER}' is not a directory.")

        return [f for f in os.listdir(Agent.__AGENT_FOLDER) if os.path.isdir(os.path.join(Agent.__AGENT_FOLDER, f))]

    def chat(self, user_input: str) -> StreamedResponse:
        """
        Sends a message to the chatbot and get a streamed response.

        :param str user_input: The user's input message.
        :return: The chatbot's response in stream.
        :rtype: StreamedResponse
        """

        for chunk in self.__chat(user_input):
            yield chunk
        self.save()

    def history(self) -> ChatHistoryV1:
        return self.__history

    def regenerate(self) -> StreamedResponse:
        """
        Regenerates the last response by re-sending the last user message.

        :return: A streamed response of the regenerated assistant's reply.
        :rtype: StreamedResponse
        """

        if len(self.__history["history"]) == 0:
            return (_ for _ in [])  # Empty generator

        last_user_message = self.__history["history"][-1]["user_message"]

        self.__history["history"] = self.__history["history"][:-1]

        for chunk in self.__chat(last_user_message):
            yield chunk
        self.save()

    def save(self):
        history_file_path = os.path.join(
            Agent.__AGENT_FOLDER, self.name, Agent.__HISTORY_FILE_NAME)
        with open(history_file_path, "w", encoding="utf-8") as file:
            json.dump(self.__history, file, indent=2, ensure_ascii=False)

    def __get_system_prompt(self) -> str:
        """
        Generates system prompt based on the user system prompt and the current emotion value.
        :return: The system prompt string.
        :rtype: str
        """

        if len(self.__history["history"]) > 0:
            # Get the last emotion value from the history.
            emotion = self.__history["history"][-1]["emotion"]
        else:
            # If no history, use the default emotion value.
            emotion = Agent.DEFAULT_EMOTION

        return system_prompt.format(
            agent_description=(agent_description_prompt.format(
                prompt=self.__agent_description) if self.__agent_description else ""),
            user_description=(user_description_prompt.format(
                prompt=self.__user_description) if self.__user_description else ""),
            emotion_value=emotion,
        )

    def __load_description(self, prompt: SystemPrompt | None) -> str:
        """
        Loads the system prompt from a file or uses the provided text.

        :param SystemPrompt prompt: The system prompt configuration.
        :return: The loaded system prompt.
        :rtype: str
        """
        if prompt is None:
            return ""

        if prompt["type"] == "file":
            with open(os.path.join(Agent.__AGENT_FOLDER, self.name, prompt["path"]), "r", encoding="utf-8") as file:
                return file.read().strip()
        elif prompt["type"] == "text":
            return prompt["content"].strip()
        else:
            return ""

    def __load_history(self, path: str):
        """
        Loads a given chat history into the chatbot.

        :param str path: The path to the chat history file.
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                file_content = json.load(file)
            try:
                self.__history = chat_history_converter(
                    validate(file_content, chat_history_schema_v0))
                self.save()
            except ValueError:
                self.__history = validate(
                    file_content, chat_history_schema_v1)
        except Exception as e:
            print(f"Warning: {str(e)}\n{traceback.format_exc()}")
            print("Cannot load history file. History will be empty.")

    def __chat(self, user_input: str) -> StreamedResponse:
        converted_history = []
        for item in self.__history["history"][-self.__history_limit:]:
            converted_history.append({
                "role": "user",
                "content": item["user_message"],
            })
            converted_history.append({
                "role": "assistant",
                "content": item["assistant_message"],
            })

        messages = [{"role": "system", "content": self.__get_system_prompt()}] + \
            converted_history + \
            [{"role": "user", "content": user_input}]

        response: Stream[ChatCompletionChunk] = self.__client.chat.completions.create(
            model=self.__model,
            messages=messages,
            stream=True,
            temperature=self.__temperature,
            max_completion_tokens=self.__max_tokens,
        )

        response_content = ""
        for chunk in response:
            if chunk.choices[0].finish_reason == "stop":
                break

            content = chunk.choices[0].delta.content or ""
            yield content
            response_content += content

        response_content = remove_think_tags(response_content)
        if response_content:
            self.__history["history"].append({
                "user_message": user_input,
                "assistant_message": response_content,
                "emotion": self.__get_new_emotion(user_input, response_content),
            })

    def __get_new_emotion(self, user: str, assistant: str) -> int:
        return self.__emotion.get(self.__history["history"], user, assistant)
