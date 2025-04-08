export type AgentConfigType = {
  /**
   * The name of the agent.
   */
  name: string;

  /**
   * The model used by the agent.
   */
  model: string;

  /**
   * The URL of the LLM server API.
   */
  baseURL: string;

  /**
   * The API key used by the LLM server. Please provide an arbitrary API key if your server is hosted locally.
   */
  apiKey: string;

  /**
   * The system prompt to be used by the agent. It can be either a file or a text string.
   */
  systemPrompt?:
    | {
        type: "file";
        path: string;
      }
    | {
        type: "text";
        content: string;
      };

  /**
   * The temperature used by the model. Default value is 0.7.
   */
  temperature?: number;
};

export type ChatHistoryType = {
  role: "user" | "assistant";
  content: string;
}[];
