import readline from "node:readline";
import Agent from "./agent";

export default class ConsoleCommand {
  private static readonly MULTILINE_TAGS = ["'''", '"""'];
  private static readonly INPUT_PROMPT = ">>> ";
  private static readonly INPUT_MULTILINE_PROMPT = "... ";

  private rl: readline.Interface;
  private agent?: Agent;

  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
  }

  async start() {
    while (true) {
      const inputContent = await this.input();
      if (inputContent.startsWith("/")) {
        this.handleCommands(inputContent);
        continue;
      }

      if (!this.agent) {
        console.error("Please load an agent with `/load <agent-name>` first.");
        continue;
      }

      try {
        const response = this.agent.chat(inputContent);
        for await (const chunk of response) {
          process.stdout.write(chunk);
        }

        this.agent.save();
        console.log();
      } catch (e) {
        if (e instanceof Error) {
          console.error(e.message);
        } else {
          console.error(e);
        }
      }
    }
  }

  private handleCommands(command: string) {
    const commands = command.trim().toLocaleLowerCase().split(" ");
    switch (commands[0]) {
      case "/list":
        console.log("Available agents:");
        console.log(Agent.listAgents().join("- "));
        break;
      case "/load":
        if (commands[1]) {
          try {
            this.agent = new Agent(commands[1]);
          } catch (e) {
            if (e instanceof Error) {
              console.error(e.message);
            } else {
              console.error(e);
            }
          }
        } else {
          console.error("Please provide an agent name to load.");
          this.help();
        }
      case "/history":
        this.history();
        break;
      case "/exit":
      case "/bye":
        this.exit();
        break;
      default:
        console.error("Unknown command. Type `/help` for a list of commands.");
      case "/help":
      case "/?":
        this.help();
        break;
    }
  }

  /**
   * Accept user input with support for single-line and multi-line modes.
   *
   * Single-line mode is triggered by input other than triple single quotes or triple double quotes.
   *
   * Multi-line mode is triggered by triple single quotes or triple double quotes and ends when the same is entered again.
   */
  private input(): Promise<string> {
    return new Promise((resolve) => {
      this.rl.question(ConsoleCommand.INPUT_PROMPT, (inputContent) => {
        if (ConsoleCommand.MULTILINE_TAGS.includes(inputContent)) {
          const tag = inputContent;
          const lines: string[] = [];
          this.rl.question(ConsoleCommand.INPUT_MULTILINE_PROMPT, (line) => {
            if (line != tag) {
              lines.push(line);
            } else {
              resolve(lines.join("\n"));
            }
          });
        } else {
          resolve(inputContent);
        }
      });
    });
  }

  private help() {
    console.log("Type the message you want to send to the agent.");
    console.log(
      "If you want to send a multi-line message, use triple single quotes (''') or triple double quotes (\"\"\") to start and end the message.",
    );
    console.log("");
    console.log("Available commands:");
    console.log("/list - List available agents.");
    console.log("/load <agent-name> - Load an agent.");
    console.log("/history - Show the history of the current agent.");
    console.log("/exit or /bye - Exit the program.");
    console.log("/help or /? - Show this help message.");
  }

  private history() {
    if (!this.agent) {
      console.error("Please load an agent with `/load <agent-name>` first.");
      return;
    }

    for (const item of this.agent.history()) {
      switch (item.role) {
        case "user":
          console.log(
            ">>> " + (item.content as string).split("\n").join("\n... "),
          );
          break;
        case "assistant":
          console.log(item.content as string);
          break;
      }
    }
  }

  private exit() {
    if (this.agent) {
      this.agent.save();
    }

    process.exit();
  }
}
