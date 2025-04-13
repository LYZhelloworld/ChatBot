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
            "description": "The maximum number of history records to be used as the context. Default value is 20.\n\nNote that one pair of user-assistant chat history is counted as two records.",
            "type": "number"
        },
        "maxTokens": {
            "description": "The maximum number of tokens to be used in the response. Default value is 2048.",
            "type": "number"
        },
        "model": {
            "description": "The model used by the agent.",
            "type": "string"
        },
        "agentDescription": {
            **__prompt_schema,
            "description": "The prompt to be used by the agent. It can be either a file or a text string."
        },
        "userDescription": {
            **__prompt_schema,
            "description": "The prompt to be used by the user. It can be either a file or a text string."
        },
        "temperature": {
            "description": "The temperature used by the model. Default value is 0.7.",
            "type": "number"
        }
    },
    "required": [
        "apiKey",
        "baseURL",
        "model"
    ],
    "type": "object"
}
