import os
import json
import sys
from typing import Iterator

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, trim_messages
from langchain_community.chat_message_histories import FileChatMessageHistory
from ollama import Client

from chatbot.types import StreamedResponse
from utils.utils import remove_think_tags
from .types import AgentConfig, PromptSchema
from .prompts import system_prompt


BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
AGENT_FOLDER = os.path.join(BASE_PATH, "agents")
CONFIG_FILE_NAME = "config.json"
HISTORY_FILE_NAME = "history.json"


class Agent:
    """
    Represents a chatbot agent that interacts with the LLM.
    """

    def __init__(self, name: str):
        """
        Initializes the Agent instance with the given name.

        :param str name: The name of the agent.
        """
        self.__name: str = name

        # Config file is located in `./agents/{agent_name}/config.json`.
        config_file_path = os.path.join(AGENT_FOLDER, name, CONFIG_FILE_NAME)
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(f"Agent '{self.name}' does not exist. Please create a config file at '{config_file_path}'.")

        with open(config_file_path, "r", encoding="utf-8") as file:
            agent_config = AgentConfig(**json.load(file))

        # Check if the model is available.
        self.__check_model_existence(agent_config)

        # Load agent configuration from config file.
        self.__history_limit = agent_config.historyLimit

        # Load or create history file.
        history_file_path = os.path.join(os.path.dirname(config_file_path), HISTORY_FILE_NAME)
        self.__history = FileChatMessageHistory(history_file_path, encoding='utf-8', ensure_ascii=False)

        # Load instructions from config file.
        self.__system_prompt = ChatPromptTemplate([('system', system_prompt)]).format_messages(
            instructions=self.__load_instructions(agent_config.instructions))

        # Create Ollama client with the provided base URL.
        self.__client = OllamaLLM(
            base_url=agent_config.baseURL,
            model=agent_config.model,
            temperature=agent_config.modelParams.temperature,
            top_p=agent_config.modelParams.top_p,
        )

    @property
    def name(self) -> str:
        """
        Returns the name of the agent.

        :return: The name of the agent.
        :rtype: str
        """
        return self.__name

    @property
    def history(self) -> list[BaseMessage]:
        """
        Returns the chat history of the agent.

        :return: The chat history.
        :rtype: list[BaseMessage]
        """
        return self.__history.messages

    @staticmethod
    def list_agents() -> list[str]:
        """
        Lists all available agents in the agent folder.

        :return: A list of agent names.
        :rtype: list[str]
        """
        if not os.path.exists(AGENT_FOLDER):
            return []

        if not os.path.isdir(AGENT_FOLDER):
            raise NotADirectoryError(f"Agent folder '{AGENT_FOLDER}' is not a directory.")

        return [f for f in os.listdir(AGENT_FOLDER) if os.path.isdir(os.path.join(AGENT_FOLDER, f))]

    def chat(self, user_input: str) -> StreamedResponse:
        """
        Sends a message to the chatbot and get a streamed response.

        :param str user_input: The user's input message.
        :return: The response in stream.
        :rtype: StreamedResponse
        """

        messages = self.__system_prompt + self.__history.messages
        messages.append(HumanMessage(content=user_input))

        trim_messages(
            messages,
            strategy="last",
            token_counter=len,
            max_tokens=self.__history_limit,
            start_on="human",
            end_on="human",
            include_system=True,
            allow_partial=False
        )

        response: Iterator[str] = self.__client.stream(messages)

        response_content = ""
        for chunk in response:
            yield chunk
            response_content += chunk

        response_content = remove_think_tags(response_content)
        if response_content:
            self.__history.add_user_message(HumanMessage(content=user_input))
            self.__history.add_ai_message(AIMessage(content=response_content))

    def __load_instructions(self, prompt: PromptSchema) -> str:
        """
        Loads the instruction prompt from a file or uses the provided text.

        :param PromptSchema: The instruction prompt.
        :return: The loaded system prompt.
        :rtype: str
        """

        if prompt.type == "file":
            with open(os.path.join(AGENT_FOLDER, self.name, prompt.path), "r", encoding="utf-8") as file:
                return file.read().strip()
        elif prompt.type == "text":
            return prompt.content.strip()
        else:
            return ""

    def __check_model_existence(self, agent_config: AgentConfig):
        """Check if the specified model exists in Ollama service, trigger download if not.

        :param AgentConfig agent_config: Configuration object containing Ollama server URL and model name
        """
        # Create Ollama client instance
        client = Client(host=agent_config.baseURL)
        # Get list of models currently loaded in the server
        models = client.list()
        required_model = agent_config.model

        # Check if required model exists in server's model list
        if any(model.model == required_model for model in models.models):
            return

        # Trigger model download process
        client.pull(model=required_model)
