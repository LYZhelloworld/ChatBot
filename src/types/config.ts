import {
  ChatCompletionSystemMessageParam,
  ChatCompletionUserMessageParam,
  ChatCompletionAssistantMessageParam,
} from "openai/resources/chat";

export type ChatMessage =
  | ChatCompletionSystemMessageParam
  | ChatCompletionUserMessageParam
  | ChatCompletionAssistantMessageParam;

export type BotConfigType = {
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
  history:
    | {
        type: "file";
        path: string;
      }
    | {
        type: "array";
        content: ChatMessage[];
      };
  temperature?: number;
};
