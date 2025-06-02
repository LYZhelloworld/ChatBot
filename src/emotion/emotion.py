from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, trim_messages

from chatbot.types import AgentConfig, ChatHistoryV1Item
from utils.utils import remove_think_tags
from .prompts import system_prompt, chat_history_item

DEFAULT_EMOTION = 50


class Emotion:
    """
    A class to handle emotion value of an agent.
    Emotion is a value between -100 and 100.
    The emotion value is used to determine the emotional state of the agent.
    The default emotion value is 50.
    """

    __TEMPERATURE = 0.0
    __HISTORY_LIMIT = 10
    __EMOTION_MIN = -100
    __EMOTION_MAX = 100
    __CHAT_HISTORY_ITEM_TEMPLATE = ChatPromptTemplate.from_template(
        chat_history_item)

    def __init__(self, model: str, config: AgentConfig):
        """
        Initializes the Emotion instance.

        :param str model: The model to use for the emotion.
        :param str base_url: The base URL for the OpenAI API.
        :param str api_key: The API key for authentication.
        """

        self.__client = OllamaLLM(
            base_url=config.get("baseURL", "http://ollama:11434/"),
            model=model,
            temperature=Emotion.__TEMPERATURE,
        )

    def get(self, history: list[ChatHistoryV1Item], user: str, assistant: str) -> int:
        """
        Returns the current emotion value based on the history.

        :param list[ChatHistory] history: The chat history.
        :param str user: The user message.
        :param str assistant: The assistant message.
        :return: The current emotion value.
        :rtype: int
        """

        if len(history) == 0:
            return DEFAULT_EMOTION

        messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
        for item in history:
            messages.append(Emotion.__CHAT_HISTORY_ITEM_TEMPLATE.format_messages(
                user_message=item["user_message"], assistant_message=item["assistant_message"]))
            messages.append(AIMessage(content=str(item["emotion"])))

        messages.append(Emotion.__CHAT_HISTORY_ITEM_TEMPLATE.format_messages(
            user_message=user,
            assistant_message=assistant,
        ))

        trim_messages(
            messages,
            strategy="last",
            token_counter=len,
            max_tokens=Emotion.__HISTORY_LIMIT,
            start_on="human",
            end_on="human",
            include_system=True,
            allow_partial=False
        )

        response = self.__client.invoke(messages)

        try:
            emotion = int(remove_think_tags(response))
        except ValueError:
            emotion = history[-1]["emotion"] if len(
                history) > 0 else DEFAULT_EMOTION

        return max(Emotion.__EMOTION_MIN, min(Emotion.__EMOTION_MAX, emotion))
