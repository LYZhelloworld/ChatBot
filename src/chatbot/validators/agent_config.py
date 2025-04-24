__prompt_schema = {
    "anyOf": [
        {
            "additionalProperties": False,
            "properties": {
                "path": {
                    "type": "string"
                },
                "type": {
                    "const": "file",
                    "type": "string"
                }
            },
            "required": [
                "path",
                "type"
            ],
            "type": "object"
        },
        {
            "additionalProperties": False,
            "properties": {
                "content": {
                    "type": "string"
                },
                "type": {
                    "const": "text",
                    "type": "string"
                }
            },
            "required": [
                "content",
                "type"
            ],
            "type": "object"
        }
    ],
    "description": "The prompt to be used by the agent. It can be either a file or a text string."
}

schema = {
    "additionalProperties": False,
    "properties": {
        "apiKey": {
            "description": "The API key used by the LLM server. Please provide an arbitrary API key if your server is hosted locally.",
            "type": "string"
        },
        "baseURL": {
            "description": "The URL of the LLM server API.",
            "type": "string"
        },
        "historyLimit": {
            "description": "The maximum number of history records to be used as the context. Default value is 20.\n\nNote that one pair of user-assistant chat history is counted as one record.",
            "type": "number"
        },
        "model": {
            "description": "The model used by the agent.",
            "type": "string"
        },
        "modelParams": {
            "additionalProperties": False,
            "description": "The parameters passed to the model.",
            "properties": {
                "frequency_penalty": {
                    "description": "Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
                    "type": "number"
                },
                "max_tokens": {
                    "description": "The maximum number of tokens that can be generated in the chat completion. This value can be used to control costs for text generated via API.",
                    "type": "number"
                },
                "presence_penalty": {
                    "description": "Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
                    "type": "number"
                },
                "temperature": {
                    "description": "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.",
                    "type": "number"
                },
                "top_p": {
                    "description": "An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.",
                    "type": "number"
                }
            },
            "type": "object",
        },
        "agentDescription": {
            **__prompt_schema,
            "description": "The prompt to be used by the agent. It can be either a file or a text string."
        },
        "userDescription": {
            **__prompt_schema,
            "description": "The prompt to be used by the user. It can be either a file or a text string."
        }
    },
    "required": [
        "apiKey",
        "baseURL",
        "model"
    ],
    "type": "object"
}
