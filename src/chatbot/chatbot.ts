import OpenAI from "openai";
import { ChatHistoryType } from "../types";

type ChatHistoryTypeWithSystem = {
  role: "user" | "assistant" | "system";
  content: string;
}[];

export default class ChatBot {
  private client: OpenAI;
  private model: string;
  private systemPrompt: string;
  private temperature: number;
  private history: ChatHistoryType;

  private static readonly HISTORY_LIMIT = 20;
  private static readonly MAX_TOKENS = 2048;

  constructor(
    model: string,
    baseURL: string,
    apiKey: string,
    {
      systemPrompt = "",
      temperature = 0.7,
    }: {
      systemPrompt?: string;
      temperature?: number;
    },
  ) {
    this.client = new OpenAI({
      baseURL: baseURL,
      apiKey: apiKey,
    });
    this.model = model;
    this.systemPrompt = systemPrompt.trim();
    this.temperature = temperature;
    this.history = [];
  }

  async *chat(userInput: string) {
    const messages: ChatHistoryTypeWithSystem = [
      { role: "system", content: this.systemPrompt },
    ];
    messages.push(...this.history.slice(-ChatBot.HISTORY_LIMIT));
    messages.push({ role: "user", content: userInput });

    const response = await this.client.chat.completions.create({
      model: this.model,
      messages,
      stream: true,
      temperature: this.temperature,
      max_tokens: ChatBot.MAX_TOKENS,
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
    this.history.push({ role: "user", content: userInput });
    this.history.push({ role: "assistant", content: responseContent });
    return responseContent;
  }

  dumpChatHistory(): ChatHistoryType {
    return this.history;
  }

  loadChatHistory(history: ChatHistoryType) {
    this.history = history;
  }

  private removeThinkTags(text: string) {
    return text.replace(/\<think\>.*?\<\/think\>/s, "").trim();
  }
}
