import {
  ChatCompletionSystemMessageParam,
  ChatCompletionUserMessageParam,
  ChatCompletionAssistantMessageParam,
} from "openai/resources/chat";

export type ChatMessageType =
  | ChatCompletionSystemMessageParam
  | ChatCompletionUserMessageParam
  | ChatCompletionAssistantMessageParam;

export type AgentConfigType = {
  name: string;
  model: string;
  baseURL: string;
  apiKey: string;
  systemPrompt:
    | {
        type: "file";
        path: string;
      }
    | {
        type: "text";
        content: string;
      };
  temperature?: number;
};
