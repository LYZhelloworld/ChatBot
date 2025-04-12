from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from chatbot.types import ChatHistoryV1Item
from utils.utils import remove_think_tags
from .prompts import system_prompt, chat_history_item


class Emotion:
    """
    A class to handle emotion value of an agent.
    """

    __TEMPERATURE = 0.0
    __MAX_TOKENS = 2048
    __HISTORY_LIMIT = 10
    __EMOTION_MIN = -100
    __EMOTION_MAX = 100
    __EMOTION_DEFAULT = 50

    def __init__(self,
                 model: str,
                 base_url: str,
                 api_key: str):
        """
        Initializes the Emotion instance.

        :param str model: The model to use for the emotion.
        :param str base_url: The base URL for the OpenAI API.
        :param str api_key: The API key for authentication.
        """

        self.__model: str = model
        self.__client: OpenAI = OpenAI(
            api_key=api_key,
            base_url=base_url
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

        if len(history) > Emotion.__HISTORY_LIMIT:
            history = history[-Emotion.__HISTORY_LIMIT:]

        if len(history) == 0:
            return Emotion.__EMOTION_DEFAULT

        messages: list[ChatCompletionMessageParam] = []
        messages.append({"role": "system", "content": system_prompt})
        for item in history:
            messages.append({"role": "user", "content": chat_history_item.format(
                user_message=item["user_message"],
                assistant_message=item["assistant_message"],
            )})
            messages.append(
                {"role": "assistant", "content": str(item["emotion"])})

        messages.append({"role": "user", "content": chat_history_item.format(
            user_message=user,
            assistant_message=assistant,
        )})

        response = self.__client.chat.completions.create(
            model=self.__model,
            messages=messages,
            temperature=Emotion.__TEMPERATURE,
            max_completion_tokens=Emotion.__MAX_TOKENS,
            stream=False,
        )

        try:
            emotion = int(remove_think_tags(
                response.choices[0].message.content.strip()))
        except ValueError:
            emotion = history[-1]["emotion"] if len(
                history) > 0 else Emotion.__EMOTION_DEFAULT

        return max(Emotion.__EMOTION_MIN, min(Emotion.__EMOTION_MAX, emotion))
