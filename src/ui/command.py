import sys
import traceback

from prompt_toolkit import HTML, PromptSession, print_formatted_text as print
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from chatbot.agent import Agent
from chatbot.types import StreamedResponse


class ConsoleCommand:
    __MULTILINE_TAGS = ["'''", '"""']
    __INPUT_PROMPT = ">>> "
    __INPUT_MULTILINE_PROMPT = "... "

    def __init__(self):
        self.__agent: Agent | None = None
        self.__session = PromptSession()

    def start(self):
        while True:
            input_content = self.input()
            if input_content.strip() == "":
                continue

            if input_content.startswith("/"):
                self.handle_commands(input_content)
                continue

            if not self.__agent:
                self.__log_agent_not_loaded()
                continue

            self.__receive_response(self.__agent.chat(input_content))

    def __receive_response(self, response: StreamedResponse):
        try:
            printer = StreamResponsePrinter()
            for chunk in response:
                printer.write(chunk)
            print()
        except Exception as e:
            print(f"Error: {e}\n{traceback.format_exc()}", file=sys.stderr)

    def __log_agent_not_loaded(self):
        print(HTML('<ansired>Please load an agent with <b>/load &lt;agent-name&gt;</b> first.</ansired>'))

    def handle_commands(self, command: str):
        commands = command.strip().lower().split(" ")
        match commands[0]:
            case "/list":
                current_agent = self.__agent.name if self.__agent else None
                print(HTML('<b>Available agents:</b>'))
                for agent in Agent.list_agents():
                    if agent == current_agent:
                        print(
                            HTML(f'- <ansigreen><b>{agent}</b></ansigreen> (current)'))
                    else:
                        print(f'- {agent}')
            case "/load":
                if len(commands) > 1:
                    self.load_agent(commands[1])
                else:
                    print("Please provide an agent name to load.")
                    self.help()
            case "/history":
                self.history()
            case "/regen" | "/regenerate":
                if not self.__agent:
                    self.__log_agent_not_loaded()
                    return
                self.__receive_response(self.__agent.regenerate())
            case "/exit" | "/bye":
                self.exit()
            case "/help" | "/?":
                self.help()
            case _:
                print(HTML(
                    '<ansired>Unknown command. Type <b>/help</b> for a list of commands.</ansired>'))
                self.help()

    def load_agent(self, agent_name: str):
        try:
            self.__agent = Agent(agent_name)
            self.history()
            print(HTML(f'<gray>(History restored)</gray>'))
        except Exception as e:
            print(f"Error: {e}\n{traceback.format_exc()}", file=sys.stderr)

    def input(self) -> str:
        """
        Accept user input with support for single-line and multi-line modes.

        Single-line mode is triggered by input other than triple single quotes or triple double quotes.

        Multi-line mode is triggered by triple single quotes or triple double quotes and ends when the same is entered again.
        """
        input_content = self.__session.prompt(self.__INPUT_PROMPT)
        if input_content in self.__MULTILINE_TAGS:
            tag = input_content
            lines = []
            while True:
                line = self.__session.prompt(self.__INPUT_MULTILINE_PROMPT)
                if line == tag:
                    break
                lines.append(line)
            return "\n".join(lines)
        return input_content

    def help(self):
        print("Type the message you want to send to the agent.")
        print("If you want to send a multi-line message, use triple single quotes (''') or triple double quotes (\"\"\") to start and end the message.")
        print("")
        print("Available commands:")
        print(HTML('<b>/list</b> - List available agents.'))
        print(HTML(
            '<b>/load &lt;agent-name&gt;</b> - Load an agent. The \'&lt;agent-name&gt;\' is the folder name under \'agents\' folder.'))
        print(
            HTML('<b>/history</b> - Show the history of the current agent.'))
        print(HTML(
            '<b>/regen</b> or <b>/regenerate</b> - Regenerate the last response.'))
        print(
            HTML('<b>/exit</b> or <b>/bye</b> - Exit the program.'))
        print(
            HTML('<b>/help</b> or <b>/?</b> - Show this help message.'))

    def history(self):
        if not self.__agent:
            self.__log_agent_not_loaded()
            return

        for item in self.__agent.history()["history"][-20:]:
            print(">>> " + item["user_message"].replace("\n", "\n... "))
            print(FormattedText(
                [('bold', item["assistant_message"])]))

    def exit(self):
        if self.__agent:
            self.__agent.save()
        sys.exit()


class StreamResponsePrinter:
    __THINK_TAG_START = "<think>"
    __THINK_TAG_END = "</think>"

    def __init__(self):
        self.__is_inside_think_tag: bool = False
        self.__response: str = ""

    def write(self, chunk: str):
        if chunk == self.__THINK_TAG_START:
            self.__is_inside_think_tag = True

        if self.__is_inside_think_tag:
            print(FormattedText(
                [('gray', chunk)]), end="", flush=True)
        else:
            print(chunk, end="", flush=True)
            self.__response += chunk

        if chunk == self.__THINK_TAG_END:
            self.__is_inside_think_tag = False

    @property
    def response(self) -> str:
        return self.__response
