import fs from "fs";
import path from "path";
import ChatBot from "../chatbot/chatbot";
import { AgentConfigType, ChatHistoryType } from "../types";
import { validateAgentConfig, validateChatHistory } from "../validators";

export default class Agent {
  private static readonly AGENT_FOLDER = path.join(process.cwd(), "agents");
  private static readonly CONFIG_FILE_NAME = "config.json";
  private static readonly HISTORY_FILE_NAME = "history.json";

  private agentName: string;
  private bot: ChatBot;

  /**
   * List available agents.
   */
  static listAgents() {
    return fs
      .readdirSync(Agent.AGENT_FOLDER)
      .filter(
        (file) => fs.statSync(path.join(Agent.AGENT_FOLDER, file)).isDirectory,
      );
  }

  constructor(agentName: string) {
    this.agentName = agentName;

    // Config file is loacted in `./agents/${agentName}/config.json`.
    const configFilePath = path.join(
      Agent.AGENT_FOLDER,
      agentName,
      Agent.CONFIG_FILE_NAME,
    );
    if (!fs.existsSync(configFilePath)) {
      throw new Error(
        `Agent '${agentName}' does not exist. Please create a config file at ${configFilePath}`,
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
      path.join(Agent.AGENT_FOLDER, this.agentName, Agent.HISTORY_FILE_NAME),
      JSON.stringify(history, null, 2),
    );
  }
}
