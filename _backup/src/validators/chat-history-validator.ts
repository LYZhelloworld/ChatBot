import Ajv from "ajv";
import { ChatHistoryType } from "../types";
import schema from "./schema.json";

export function validateChatHistory(config: any): ChatHistoryType {
  const ajv = new Ajv({ allErrors: true });
  const validate = ajv.compile(schema.definitions.ChatHistoryType);
  const valid = validate(config);

  if (!valid) {
    throw new Error(
      `Invalid chat history: ${ajv.errorsText(validate.errors, {
        dataVar: "config",
      })}`,
    );
  }

  return config as ChatHistoryType;
}
