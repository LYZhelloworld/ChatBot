import re
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk

from chatbot.types import ChatHistory, StreamedResponse


class ChatBot:
    """
    A simple chatbot class. It maintains a conversation history and allows for a system prompt.
    """

    def __init__(self,
                 model: str,
                 base_url: str,
                 api_key: str,
                 system_prompt: str | None = None,
                 temperature: float | None = None,
                 history_limit: int | None = None,
                 max_tokens: int | None = None):
        """
        Initializes the ChatBot instance.

        :param str model: The model to use for the chatbot.
        :param str base_url: The base URL for the OpenAI API.
        :param str api_key: The API key for authentication.
        :param str system_prompt: The system prompt for the chatbot.
        :param float temperature: The temperature for the model's responses.
        :param int history_limit: The maximum number of messages to keep in history.
        :param int max_tokens: The maximum number of tokens for the response.
        """

        system_prompt = "" if system_prompt is None else system_prompt
        temperature = 0.7 if temperature is None else temperature
        history_limit = 20 if history_limit is None else history_limit
        max_tokens = 2048 if max_tokens is None else max_tokens

        self.__model: str = model
        self.__client: OpenAI = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.__system_prompt: str = system_prompt.strip()
        self.__temperature: float = temperature
        self.__history_limit: int = history_limit
        self.__max_tokens: int = max_tokens
        self.__history: list[ChatHistory] = []

    def chat(self, user_input: str) -> StreamedResponse:
        """
        Sends a message to the chatbot and get a streamed response.

        :param str user_input: The user's input message.
        :return: The chatbot's response in stream.
        :rtype: StreamedResponse
        """

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

        response_content = self.__remove_think_tags(response_content)
        if response_content:
            self.__history.append({"role": "user", "content": user_input})
            self.__history.append(
                {"role": "assistant", "content": response_content})

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
        return self.chat(last_user_message)

    def dump_chat_history(self) -> list[ChatHistory]:
        """
        Returns the current chat history.

        :return: The chat history as a list of messages, where each message contains a role ("user" or "assistant") and content.
        :rtype: list[ChatHistory]
        """
        return self.__history

    def load_chat_history(self, history: list[ChatHistory]):
        """
        Loads a given chat history into the chatbot.

        :param list[ChatHistory] history: The chat history to load, as a list of messages with a role ("user" or "assistant") and content.
        """
        self.__history = history

    def __remove_think_tags(self, text: str) -> str:
        """
        Removes content enclosed within `<think>` and `</think>` tags from the given text.

        - If both opening and closing `<think>` tags are present, the content within the tags is removed.
        - If only the opening `<think>` tag is present without a closing tag, an empty string is returned.
        - If no `<think>` tags are present, the text is returned as-is after trimming whitespace.

        :param str text: The input text to process.
        :return: The processed text with `<think>` tags handled appropriately.
        :rtype: str
        """

        if "<think>" in text and "</think>" in text:
            return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
        elif "<think>" in text:
            # The tag is not closed.
            return ""
        else:
            return text.strip()
