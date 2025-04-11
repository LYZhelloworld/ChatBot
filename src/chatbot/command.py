import sys
import traceback

import colorama
from .agent import Agent
from chatbot.types import StreamedResponse


class ConsoleCommand:
    __MULTILINE_TAGS = ["'''", '"""']
    __INPUT_PROMPT = ">>> "
    __INPUT_MULTILINE_PROMPT = "... "

    def __init__(self):
        self.__agent: Agent | None = None

    def start(self):
        colorama.init()
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
            print(colorama.Style.RESET_ALL)
        except Exception as e:
            print(f"Error: {e}\n{traceback.format_exc()}", file=sys.stderr)

    def __log_agent_not_loaded(self):
        print(f"{colorama.Fore.RED}Please load an agent with " +
              f"{colorama.Style.BRIGHT}/load <agent-name>{colorama.Style.NORMAL}" +
              f" first.{colorama.Style.RESET_ALL}")

    def handle_commands(self, command: str):
        commands = command.strip().lower().split(" ")
        match commands[0]:
            case "/list":
                current_agent = self.__agent.name if self.__agent else None
                print(colorama.Style.BRIGHT +
                      "Available agents:" + colorama.Style.RESET_ALL)
                print(
                    "\n".join(
                        [
                            f"- {colorama.Fore.GREEN + colorama.Style.BRIGHT}{agent}{colorama.Fore.WHITE + colorama.Style.DIM} (current){colorama.Style.RESET_ALL}" if agent == current_agent else agent
                            for agent in Agent.list_agents()
                        ]
                    )
                )
            case "/load":
                if len(commands) > 1:
                    try:
                        self.__agent = Agent(commands[1])
                    except Exception as e:
                        print(
                            f"Error: {e}\n{traceback.format_exc()}", file=sys.stderr)
                    else:
                        self.history()
                        print(colorama.Style.DIM +
                              "(History restored)" + colorama.Style.RESET_ALL)
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
                print(colorama.Style.RESET_ALL)
            case "/exit" | "/bye":
                self.exit()
            case "/help" | "/?":
                self.help()
            case _:
                print(colorama.Fore.RED + "Unknown command. Type " + colorama.Style.BRIGHT +
                      "/help" + colorama.Style.NORMAL + " for a list of commands." + colorama.Style.RESET_ALL)
                self.help()

    def input(self) -> str:
        """
        Accept user input with support for single-line and multi-line modes.

        Single-line mode is triggered by input other than triple single quotes or triple double quotes.

        Multi-line mode is triggered by triple single quotes or triple double quotes and ends when the same is entered again.
        """
        input_content = input(self.__INPUT_PROMPT)
        if input_content in self.__MULTILINE_TAGS:
            tag = input_content
            lines = []
            while True:
                line = input(self.__INPUT_MULTILINE_PROMPT)
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
        print(colorama.Style.BRIGHT + "/list" +
              colorama.Style.NORMAL + " - List available agents.")
        print(colorama.Style.BRIGHT + "/load <agent-name>" + colorama.Style.NORMAL +
              " - Load an agent. The '<agent-name>' is the folder name under 'agents' folder.")
        print(colorama.Style.BRIGHT + "/history" + colorama.Style.NORMAL +
              " - Show the history of the current agent.")
        print(colorama.Style.BRIGHT + "/regen" + colorama.Style.NORMAL + " or " +
              colorama.Style.BRIGHT + "/regenerate" + colorama.Style.NORMAL + " - Regenerate the last response.")
        print(colorama.Style.BRIGHT + "/exit" + colorama.Style.NORMAL + " or " +
              colorama.Style.BRIGHT + "/bye" + colorama.Style.NORMAL + " - Exit the program.")
        print(colorama.Style.BRIGHT + "/help" + colorama.Style.NORMAL + " or " +
              colorama.Style.BRIGHT + "/?" + colorama.Style.NORMAL + " - Show this help message." + colorama.Style.RESET_ALL)

    def history(self):
        if not self.__agent:
            self.__log_agent_not_loaded()
            return

        for item in self.__agent.history()["history"]:
            print(">>> " + item["user_message"].replace("\n", "\n... "))
            print(colorama.Style.BRIGHT +
                  item["assistant_message"] + colorama.Style.RESET_ALL)

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
            print(colorama.Style.DIM, end="", flush=True)

        print(chunk, end="", flush=True)
        if not self.__is_inside_think_tag:
            self.__response += chunk

        if chunk == self.__THINK_TAG_END:
            self.__is_inside_think_tag = False
            print(colorama.Style.NORMAL, end="", flush=True)

    @property
    def response(self) -> str:
        return self.__response
