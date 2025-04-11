import Ajv from "ajv";
import { AgentConfigType } from "../types";
import schema from "./schema.json";

export function validateAgentConfig(config: any): AgentConfigType {
  const ajv = new Ajv({ allErrors: true });
  const validate = ajv.compile(schema.definitions.AgentConfigType);
  const valid = validate(config);

  if (!valid) {
    throw new Error(
      `Invalid agent config: ${ajv.errorsText(validate.errors, {
        dataVar: "config",
      })}`,
    );
  }

  return config as AgentConfigType;
}
