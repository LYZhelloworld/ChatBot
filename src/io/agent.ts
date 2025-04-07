import fs from "fs";
import path from "path";
import ChatBot from "../chatbot/chatbot";
import { ChatMessageType } from "../types/config";

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

    const configFileContent = JSON.parse(
      fs.readFileSync(configFilePath, "utf-8"),
    );

    this.bot = new ChatBot(
      configFileContent.model,
      configFileContent.baseURL,
      configFileContent.apiKey,
      {
        systemPrompt:
          configFileContent.systemPrompt.type === "text"
            ? configFileContent.systemPrompt.content
            : fs.readFileSync(
                path.join(
                  path.dirname(configFilePath),
                  configFileContent.systemPrompt.path,
                ),
                "utf-8",
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
      const historyContent = JSON.parse(
        fs.readFileSync(historyFilePath, "utf-8"),
      );
      this.bot.loadChatHistory(historyContent);
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

  private saveHistory(history: ChatMessageType[]) {
    fs.writeFileSync(
      path.join(Agent.AGENT_FOLDER, this.agentName, Agent.HISTORY_FILE_NAME),
      JSON.stringify(history, null, 2),
    );
  }
}
