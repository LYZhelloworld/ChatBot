import readline from "node:readline";
import chalk from "chalk";
import Agent from "./agent";
import { StreamedResponseType } from "../chatbot";

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
        await this.handleCommands(inputContent);
        continue;
      }

      if (!this.agent) {
        this.logAgentNotLoaded();
        continue;
      }

      await this.receiveResponse(this.agent.chat(inputContent));
    }
  }

  private async receiveResponse(response: StreamedResponseType) {
    try {
      const printer = new StreamResponsePrinter();
      for await (const chunk of response) {
        printer.write(chunk);
      }
      console.log();
    } catch (e) {
      if (e instanceof Error) {
        console.error(e.message);
      } else {
        console.error(e);
      }
    }
  }

  private logAgentNotLoaded() {
    console.error(
      chalk.red(
        "Please load an agent with " +
          chalk.bold("/load <agent-name>") +
          " first.",
      ),
    );
  }

  private async handleCommands(command: string) {
    const commands = command.trim().toLocaleLowerCase().split(" ");
    switch (commands[0]) {
      case "/list":
        const currentAgent = this.agent?.name;
        console.log(chalk.bold("Available agents:"));
        console.log(
          Agent.listAgents()
            .map((agent) =>
              agent === currentAgent
                ? chalk.greenBright(agent) + chalk.gray(" (current)")
                : agent,
            )
            .map((agent) => `- ${agent}`)
            .join("\n"),
        );
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

          // Print history.
          this.history();
          console.log(chalk.gray("(History restored)"));
        } else {
          console.error("Please provide an agent name to load.");
          this.help();
        }
        break;
      case "/history":
        this.history();
        break;
      case "/regen":
      case "/regenerate":
        if (!this.agent) {
          this.logAgentNotLoaded();
          return;
        }

        await this.receiveResponse(this.agent.regenerate());
        break;
      case "/exit":
      case "/bye":
        this.exit();
        break;
      default:
        console.error(
          chalk.red(
            "Unknown command. Type " +
              chalk.bold("/help") +
              " for a list of commands.",
          ),
        );
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
    console.log(chalk.bold("/list") + " - List available agents.");
    console.log(
      chalk.bold("/load <agent-name>") +
        " - Load an agent. The '<agent-name>' is the folder name under 'agents' folder.",
    );
    console.log(
      chalk.bold("/history") + " - Show the history of the current agent.",
    );
    console.log(
      chalk.bold("/regen") +
        " or " +
        chalk.bold("/regenerate") +
        " - Regenerate the last response.",
    );
    console.log(
      chalk.bold("/exit") +
        " or " +
        chalk.bold("/bye") +
        " - Exit the program.",
    );
    console.log(
      chalk.bold("/help") +
        " or " +
        chalk.bold("/?") +
        " - Show this help message.",
    );
  }

  private history() {
    if (!this.agent) {
      this.logAgentNotLoaded();
      return;
    }

    for (const item of this.agent.history()) {
      switch (item.role) {
        case "user":
          console.log(">>> " + item.content.split("\n").join("\n... "));
          break;
        case "assistant":
          console.log(chalk.whiteBright(item.content));
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

class StreamResponsePrinter {
  private static readonly THINK_TAG_START = "<think>";
  private static readonly THINK_TAG_END = "</think>";

  /**
   * Whether the current content is inside a `<think>...</think>` tag.
   */
  private isInsideThinkTag = false;

  /**
   * Final response string.
   */
  private _response: string = "";

  write(chunk: string) {
    if (chunk === StreamResponsePrinter.THINK_TAG_START) {
      this.isInsideThinkTag = true;
    }

    if (this.isInsideThinkTag) {
      process.stdout.write(chalk.gray(chunk));
    } else {
      process.stdout.write(chalk.whiteBright(chunk));
      this._response += chunk;
    }

    if (chunk === StreamResponsePrinter.THINK_TAG_END) {
      this.isInsideThinkTag = false;
    }
  }

  get response(): string {
    return this._response;
  }
}
