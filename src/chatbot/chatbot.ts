import OpenAI from "openai";
import { ChatHistoryType } from "../types";

type ChatHistoryTypeWithSystem = {
  role: "user" | "assistant" | "system";
  content: string;
}[];

export default class ChatBot {
  private client: OpenAI;
  private systemPrompt: string;
  private temperature: number;
  private history: ChatHistoryType;
  private historyLimit: number;
  private maxTokens: number;

  constructor(
    private model: string,
    baseURL: string,
    apiKey: string,
    {
      systemPrompt = "",
      temperature = 0.7,
      historyLimit = 20,
      maxTokens = 2048,
    }: {
      systemPrompt?: string;
      temperature?: number;
      historyLimit?: number;
      maxTokens?: number;
    },
  ) {
    this.client = new OpenAI({
      baseURL: baseURL,
      apiKey: apiKey,
    });
    this.systemPrompt = systemPrompt.trim();
    this.temperature = temperature;
    this.historyLimit = historyLimit;
    this.maxTokens = maxTokens;
    this.history = [];
  }

  async *chat(userInput: string) {
    const messages: ChatHistoryTypeWithSystem = [
      { role: "system", content: this.systemPrompt },
    ];
    messages.push(...this.history.slice(-this.historyLimit));
    messages.push({ role: "user", content: userInput });

    const response = await this.client.chat.completions.create({
      model: this.model,
      messages,
      stream: true,
      temperature: this.temperature,
      max_completion_tokens: this.maxTokens,
    });

    let responseContent = "";
    for await (const chunk of response) {
      if (chunk.choices[0].finish_reason == "stop") {
        break;
      }

      const content = chunk.choices[0].delta.content ?? "";
      yield content;
      responseContent += content;
    }

    responseContent = this.removeThinkTags(responseContent);
    if (responseContent) {
      this.history.push({ role: "user", content: userInput });
      this.history.push({ role: "assistant", content: responseContent });
    }

    return responseContent;
  }

  dumpChatHistory(): ChatHistoryType {
    return this.history;
  }

  loadChatHistory(history: ChatHistoryType) {
    this.history = history;
  }

  private removeThinkTags(text: string) {
    if (text.includes("<think>") && text.includes("</think>")) {
      return text.replace(/\<think\>.*?\<\/think\>/s, "").trim();
    } else if (text.includes("<think>")) {
      // The tag is not closed.
      return "";
    } else {
      return text.trim();
    }
  }
}
