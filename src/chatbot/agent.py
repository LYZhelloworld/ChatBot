import os
import json
import sys
import traceback
from typing import Iterator

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, trim_messages

from chatbot.types import StreamedResponse
from emotion.emotion import Emotion, DEFAULT_EMOTION
from utils.utils import remove_think_tags
from .types import AgentConfig, ChatHistoryV1, PromptSchema
from .prompts import system_prompt, agent_description_prompt, user_description_prompt


class Agent:
    """
    Represents a chatbot agent that interacts with the LLM.
    """
    __BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    __AGENT_FOLDER = os.path.join(__BASE_PATH, "agents")
    __CONFIG_FILE_NAME = "config.json"
    __HISTORY_FILE_NAME = "history.json"
    __SYSTEM_PROMPT_TEMPLATE = ChatPromptTemplate([('system', system_prompt)])

    def __init__(self, name: str):
        """
        Initializes the Agent instance with the given name.

        :param str name: The name of the agent.
        """
        self.__name: str = name

        # Config file is located in `./agents/{agent_name}/config.json`.
        config_file_path = os.path.join(
            Agent.__AGENT_FOLDER, name, self.__CONFIG_FILE_NAME)
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(f"Agent '{self.name}' does not exist. Please create a config file at '{config_file_path}'.")

        with open(config_file_path, "r", encoding="utf-8") as file:
            agent_config = AgentConfig(**json.load(file))

        # Load agent configuration from config file.
        self.__model = agent_config.model
        self.__model_params = agent_config.modelParams
        self.__history_limit = agent_config.historyLimit
        self.__history = ChatHistoryV1(version="v1", history=[])

        # Load description from config file.
        self.__agent_description = self.__load_description(agent_config.agentDescription)
        self.__user_description = self.__load_description(agent_config.userDescription)

        # Create Ollama client with the provided base URL.
        self.__client = OllamaLLM(
            base_url=agent_config.baseURL,
            model=agent_config.model,
            temperature=self.__model_params.temperature,
            top_p=self.__model_params.top_p,
        )

        # Load or create history file.
        history_file_path = os.path.join(os.path.dirname(config_file_path), Agent.__HISTORY_FILE_NAME)
        if not os.path.exists(history_file_path):
            self.save()
        else:
            try:
                self.__load_history(history_file_path)
            except Exception as e:
                print(f"Warning: {str(e)}")
                print("Cannot load history file. History will be empty.")

        # Create emotion instance.
        self.__emotion: Emotion = Emotion(self.__model, agent_config)

    @property
    def name(self) -> str:
        """
        Returns the name of the agent.

        :return: The name of the agent.
        :rtype: str
        """
        return self.__name

    @staticmethod
    def list_agents() -> list[str]:
        """
        Lists all available agents in the agent folder.

        :return: A list of agent names.
        :rtype: list[str]
        """
        if not os.path.exists(Agent.__AGENT_FOLDER):
            return []

        if not os.path.isdir(Agent.__AGENT_FOLDER):
            raise NotADirectoryError(f"Agent folder '{Agent.__AGENT_FOLDER}' is not a directory.")

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
        """
        Returns the chat history of the agent.

        :return: The chat history.
        :rtype: ChatHistoryV1
        """
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
        """
        Saves the current chat history to a file.
        """
        history_file_path = os.path.join(Agent.__AGENT_FOLDER, self.name, Agent.__HISTORY_FILE_NAME)
        with open(history_file_path, "w", encoding="utf-8") as file:
            json.dump(self.__history, file, indent=2, ensure_ascii=False)

    def __get_system_prompt(self) -> list[BaseMessage]:
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
            emotion = DEFAULT_EMOTION

        return Agent.__SYSTEM_PROMPT_TEMPLATE.format_messages(
            agent_description=(agent_description_prompt.format(prompt=self.__agent_description) if self.__agent_description else ""),
            user_description=(user_description_prompt.format(prompt=self.__user_description) if self.__user_description else ""),
            emotion_value=emotion,
        )

    def __load_description(self, prompt: PromptSchema) -> str:
        """
        Loads the description prompt from a file or uses the provided text.

        :param PromptSchema: The description prompt.
        :return: The loaded system prompt.
        :rtype: str
        """

        if prompt.type == "file":
            with open(os.path.join(Agent.__AGENT_FOLDER, self.name, prompt.path), "r", encoding="utf-8") as file:
                return file.read().strip()
        elif prompt.type == "text":
            return prompt.content.strip()
        else:
            return ""

    def __load_history(self, path: str):
        """
        Loads a given chat history into the chatbot.

        :param str path: The path to the chat history file.
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                self.__history = ChatHistoryV1(**json.load(file))
            self.save()
        except Exception as e:
            print(f"Warning: {str(e)}\n{traceback.format_exc()}")
            print("Cannot load history file. History will be empty.")

    def __chat(self, user_input: str) -> StreamedResponse:
        """
        Sends a message to the chatbot and get a streamed response.

        :param str user_input: The user's input message.
        :return: The response in stream.
        :rtype: StreamedResponse
        """

        messages = self.__get_system_prompt()
        for item in self.__history["history"]:
            messages.append(HumanMessage(content=item["user_message"]))
            messages.append(AIMessage(content=item["assistant_message"]))
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
            self.__history.history.append({
                "user_message": user_input,
                "assistant_message": response_content,
                "emotion": self.__get_new_emotion(user_input, response_content),
            })

    def __get_new_emotion(self, user: str, assistant: str) -> int:
        """
        Returns the new emotion value based on the user and assistant messages.

        :param str user: The user's message.
        :param str assistant: The assistant's message.
        :return: The new emotion value.
        :rtype: int
        """
        return self.__emotion.get(self.__history["history"], user, assistant)
