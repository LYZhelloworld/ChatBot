from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_community.chat_message_histories import FileChatMessageHistory

from chatbot.types import AgentConfig
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
    __CHAT_HISTORY_ITEM_TEMPLATE = ChatPromptTemplate.from_template(chat_history_item)

    def __init__(self, model: str, config: AgentConfig):
        """
        Initializes the Emotion instance.

        :param str model: The model to use for the emotion.
        :param str base_url: The base URL for the OpenAI API.
        :param str api_key: The API key for authentication.
        """

        self.__client = OllamaLLM(
            base_url=config.baseURL,
            model=model,
            temperature=Emotion.__TEMPERATURE,
        )

    def get(self, history: FileChatMessageHistory, user: str, assistant: str) -> int:
        """
        Returns the current emotion value based on the history.

        :param list[ChatHistory] history: The chat history.
        :param str user: The user message.
        :param str assistant: The assistant message.
        :return: The current emotion value.
        :rtype: int
        """

        if len(history.messages) == 0:
            return DEFAULT_EMOTION

        messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
        user_message: HumanMessage
        for message in history.messages:
            if isinstance(message, HumanMessage):
                user_message = message
            elif isinstance(message, AIMessage):
                messages.append(Emotion.__CHAT_HISTORY_ITEM_TEMPLATE.format_messages(
                    user_message=user_message.content,
                    assistant_message=message.content,
                ))
                emotion = message.additional_kwargs["emotion"]
                emotion = emotion if emotion is not None else DEFAULT_EMOTION
                messages.append(AIMessage(content=str(emotion)))

        trim_messages(
            messages,
            strategy="last",
            token_counter=len,
            max_tokens=Emotion.__HISTORY_LIMIT,
            start_on="human",
            include_system=True,
            allow_partial=False
        )

        messages.append(Emotion.__CHAT_HISTORY_ITEM_TEMPLATE.format_messages(user_message=user, assistant_message=assistant))

        response = self.__client.invoke(messages)

        try:
            emotion = int(remove_think_tags(response))
        except ValueError:
            if len(history.messages) == 0:
                emotion = DEFAULT_EMOTION
            else:
                emotion = history.messages[-1].additional_kwargs["emotion"]
                emotion = DEFAULT_EMOTION if emotion is None else emotion

        return max(Emotion.__EMOTION_MIN, min(Emotion.__EMOTION_MAX, emotion))
