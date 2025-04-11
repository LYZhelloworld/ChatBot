export type AgentConfigType = {
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

  /**
   * The maximum number of history records to be used as the context. Default value is 20.
   *
   * Note that one pair of user-assistant chat history is counted as two records.
   */
  historyLimit?: number;

  /**
   * The maximum number of tokens to be used in the response. Default value is 2048.
   */
  maxTokens?: number;
};

export type ChatHistoryType = {
  role: "user" | "assistant";
  content: string;
}[];
