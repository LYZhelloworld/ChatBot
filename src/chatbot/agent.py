import os
import json
import sys

from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk

from chatbot.types import ChatHistory, StreamedResponse
from utils.utils import remove_think_tags
from .types import AgentConfig, SystemPrompt
from .validators.validator import validate
from .validators.agent_config import schema as agent_config_schema
from .validators.chat_history import schema as chat_history_schema


class Agent:
    __BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    __AGENT_FOLDER = os.path.join(__BASE_PATH, "agents")
    __CONFIG_FILE_NAME = "config.json"
    __HISTORY_FILE_NAME = "history.json"

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

        self.__model: str = config_file_content.get("model")
        self.__system_prompt: str = self.__get_system_prompt(
            config_file_content.get("systemPrompt")).strip()
        self.__temperature: float = config_file_content.get("temperature", 0.7)
        self.__history_limit: int = config_file_content.get("historyLimit", 20)
        self.__max_tokens: int = config_file_content.get("maxTokens", 2048)
        self.__history: list[ChatHistory] = []

        self.__client: OpenAI = OpenAI(
            api_key=config_file_content.get("apiKey"),
            base_url=config_file_content.get("baseURL"),
        )

        history_file_path = os.path.join(os.path.dirname(
            config_file_path), Agent.__HISTORY_FILE_NAME)
        if not os.path.exists(history_file_path):
            self.save()
        else:
            try:
                with open(history_file_path, "r", encoding="utf-8") as file:
                    history_content: list[ChatHistory] = validate(
                        json.load(file), chat_history_schema)
                self.__load_history(history_content)
            except Exception as e:
                print(f"Warning: {str(e)}")
                print("Cannot load history file. History will be empty.")

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

    def history(self) -> list[ChatHistory]:
        return self.__history

    def regenerate(self) -> StreamedResponse:
        """
        Regenerates the last response by re-sending the last user message.

        :return: A streamed response of the regenerated assistant's reply.
        :rtype: StreamedResponse
        """

        if len(self.__history) < 2:
            return (_ for _ in [])  # Empty generator

        last_user_message = self.__history[-2]["content"]

        self.__history = self.__history[:-2]

        for chunk in self.__chat(last_user_message):
            yield chunk
        self.save()

    def save(self):
        history_file_path = os.path.join(
            Agent.__AGENT_FOLDER, self.name, Agent.__HISTORY_FILE_NAME)
        with open(history_file_path, "w", encoding="utf-8") as file:
            json.dump(self.__history, file, indent=2, ensure_ascii=False)

    def __get_system_prompt(self, system_prompt: SystemPrompt) -> str:
        if system_prompt is None:
            return ""

        if system_prompt["type"] == "text":
            return system_prompt["content"]

        if system_prompt["type"] == "file":
            with open(os.path.join(Agent.__AGENT_FOLDER, self.name, system_prompt["path"]), "r", encoding="utf-8") as file:
                return file.read()

        return ""

    def __load_history(self, history: list[ChatHistory]):
        """
        Loads a given chat history into the chatbot.

        :param list[ChatHistory] history: The chat history to load, as a list of messages with a role ("user" or "assistant") and content.
        """
        self.__history = history

    def __chat(self, user_input: str) -> StreamedResponse:
        messages = [{"role": "system", "content": self.__system_prompt}] + \
            self.__history[-self.__history_limit:] + \
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
            self.__history.append({"role": "user", "content": user_input})
            self.__history.append(
                {"role": "assistant", "content": response_content})
