import fs from "fs";
import { BotConfigType, ChatMessage } from "../types/config";
import ChatBot from "../chatbot/chatbot";

export default class BotLoader {
  private configFileContent: BotConfigType;

  constructor(configFilePath: string) {
    this.configFileContent = JSON.parse(
      fs.readFileSync(configFilePath, "utf-8"),
    );
  }

  create() {
    const bot = new ChatBot(
      this.configFileContent.model,
      this.configFileContent.baseURL,
      this.configFileContent.apiKey,
      {
        systemPrompt:
          this.configFileContent.systemPrompt.type === "text"
            ? this.configFileContent.systemPrompt.content
            : fs.readFileSync(
                this.configFileContent.systemPrompt.path,
                "utf-8",
              ),
        temperature: this.configFileContent.temperature,
      },
    );

    bot.loadChatHistory(
      this.configFileContent.history.type === "file"
        ? (fs.readFileSync(
            this.configFileContent.history.path,
          ) as unknown as ChatMessage[])
        : this.configFileContent.history.content,
    );
  }
}
