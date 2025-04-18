import sys
from ui.command import ConsoleCommand


def main(agent_name: str = None):
    command = ConsoleCommand()
    if agent_name:
        command.load_agent(agent_name)
    command.start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
