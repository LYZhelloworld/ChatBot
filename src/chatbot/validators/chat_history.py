schema_v0 = {
    "items": {
        "additionalProperties": False,
        "properties": {
            "content": {
                "type": "string"
            },
            "role": {
                "enum": [
                    "assistant",
                    "user"
                ],
                "type": "string"
            }
        },
        "required": [
            "content",
            "role"
        ],
        "type": "object"
    },
    "type": "array",
}

schema_v1 = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "enum": ["v1"]
        },
        "history": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "user_message": {
                        "type": "string"
                    },
                    "assistant_message": {
                        "type": "string"
                    },
                    "emotion": {
                        "type": "integer"
                    }
                },
                "required": [
                    "user_message",
                    "assistant_message",
                    "emotion"
                ]
            }
        }
    },
    "required": [
        "version",
        "history"
    ],
}
