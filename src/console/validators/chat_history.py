schema = {
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
    "type": "array"
}
