import fs from "fs";
import path from "path";
import ChatBot from "../chatbot/chatbot";
import { AgentConfigType, ChatHistoryType } from "../types";
import { validateAgentConfig, validateChatHistory } from "../validators";

const isPkg =
  typeof (process as NodeJS.Process & { pkg?: unknown }).pkg !== "undefined";

export default class Agent {
  private static readonly BASE_PATH = isPkg
    ? path.dirname(process.execPath)
    : path.join(__dirname, "..", "..");
  private static readonly AGENT_FOLDER = path.join(Agent.BASE_PATH, "agents");
  private static readonly CONFIG_FILE_NAME = "config.json";
  private static readonly HISTORY_FILE_NAME = "history.json";

  private bot: ChatBot;

  /**
   * List available agents.
   */
  static listAgents() {
    if (!fs.existsSync(Agent.AGENT_FOLDER)) {
      return [];
    }

    if (!fs.statSync(Agent.AGENT_FOLDER).isDirectory()) {
      throw new Error(
        `Agent folder '${Agent.AGENT_FOLDER}' is not a directory.`,
      );
    }

    return fs
      .readdirSync(Agent.AGENT_FOLDER)
      .filter(
        (file) => fs.statSync(path.join(Agent.AGENT_FOLDER, file)).isDirectory,
      );
  }

  constructor(private _name: string) {
    this._name = _name;

    // Config file is loacted in `./agents/${agentName}/config.json`.
    const configFilePath = path.join(
      Agent.AGENT_FOLDER,
      this.name,
      Agent.CONFIG_FILE_NAME,
    );
    if (!fs.existsSync(configFilePath)) {
      throw new Error(
        `Agent '${this.name}' does not exist. Please create a config file at ${configFilePath}`,
      );
    }

    const configFileContent = validateAgentConfig(
      JSON.parse(fs.readFileSync(configFilePath, "utf-8")),
    );

    this.bot = new ChatBot(
      configFileContent.model,
      configFileContent.baseURL,
      configFileContent.apiKey,
      {
        systemPrompt: this.getSystemPrompt(
          configFileContent.systemPrompt,
          path.dirname(configFilePath),
        ),
        temperature: configFileContent.temperature,
      },
    );

    const historyFilePath = path.join(
      path.dirname(configFilePath),
      Agent.HISTORY_FILE_NAME,
    );
    if (!fs.existsSync(historyFilePath)) {
      this.saveHistory([]);
    } else {
      try {
        const historyContent = validateChatHistory(
          JSON.parse(fs.readFileSync(historyFilePath, "utf-8")),
        );
        this.bot.loadChatHistory(historyContent);
      } catch (e) {
        if (e instanceof Error) {
          console.error("Warning: " + e.message);
        } else {
          console.error("Warning: " + e);
        }
        console.error("Cannot load history file. History will be empty.");
      }
    }
  }

  get name() {
    return this._name;
  }

  chat(userInput: string) {
    return this.bot.chat(userInput);
  }

  history() {
    return this.bot.dumpChatHistory();
  }

  save() {
    this.saveHistory(this.bot.dumpChatHistory());
  }

  private getSystemPrompt(
    systemPrompt: AgentConfigType["systemPrompt"],
    agentPath: string,
  ): string {
    if (systemPrompt === undefined) {
      return "";
    }

    if (systemPrompt.type === "text") {
      return systemPrompt.content;
    }

    if (systemPrompt.type === "file") {
      return fs.readFileSync(path.join(agentPath, systemPrompt.path), "utf-8");
    }

    return "";
  }

  private saveHistory(history: ChatHistoryType) {
    fs.writeFileSync(
      path.join(Agent.AGENT_FOLDER, this.name, Agent.HISTORY_FILE_NAME),
      JSON.stringify(history, null, 2),
    );
  }
}
