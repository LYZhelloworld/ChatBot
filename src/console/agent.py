import os
import json
import sys

from chatbot.types import ChatHistory, StreamedResponse
from .types import AgentConfig, SystemPrompt
from chatbot.chatbot import ChatBot
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

        self.__bot: ChatBot = ChatBot(
            model=config_file_content.get("model"),
            base_url=config_file_content.get("baseURL"),
            api_key=config_file_content.get("apiKey"),
            system_prompt=self.get_system_prompt(
                config_file_content.get("systemPrompt")),
            temperature=config_file_content.get("temperature"),
            history_limit=config_file_content.get("historyLimit"),
            max_tokens=config_file_content.get("maxTokens"),
        )

        history_file_path = os.path.join(os.path.dirname(
            config_file_path), Agent.__HISTORY_FILE_NAME)
        if not os.path.exists(history_file_path):
            self.save_history([])
        else:
            try:
                with open(history_file_path, "r", encoding="utf-8") as file:
                    history_content: list[ChatHistory] = validate(
                        json.load(file), chat_history_schema)
                self.__bot.load_chat_history(history_content)
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
        for chunk in self.__bot.chat(user_input):
            yield chunk
        self.save()

    def history(self) -> ChatHistory:
        return self.__bot.dump_chat_history()

    def regenerate(self) -> StreamedResponse:
        for chunk in self.__bot.regenerate():
            yield chunk
        self.save()

    def save(self):
        self.save_history(self.__bot.dump_chat_history())

    def get_system_prompt(self, system_prompt: SystemPrompt) -> str:
        if system_prompt is None:
            return ""

        if system_prompt["type"] == "text":
            return system_prompt["content"]

        if system_prompt["type"] == "file":
            with open(os.path.join(Agent.__AGENT_FOLDER, self.name, system_prompt["path"]), "r", encoding="utf-8") as file:
                return file.read()

        return ""

    def save_history(self, history: ChatHistory):
        history_file_path = os.path.join(
            Agent.__AGENT_FOLDER, self.name, Agent.__HISTORY_FILE_NAME)
        with open(history_file_path, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=2, ensure_ascii=False)
