# ChatBot
ChatBot is an interactive chatting tool with local deployed LLM.

## Prerequisites
This tool is based on OpenAI API model.

Please install [Ollama](https://ollama.com) If you want to run locally. Otherwise, please provide an API token in the configuration file.

### Environment Setup
```bash
npm install
```

### Create Agent
1. Create a folder `agents` under the root directory (if it does not exist).
1. Create a folder under `agents` with a proper name **without spaces**. (For example, `my-agent`).
1. Add a configuration file in your agent folder with the name `config.json`. Below is an example:
    ```json
    {
      "name": "my-agent",
      "model": "qwen2.5-7b",
      "baseURL": "http://localhost:11434/v1",
      "apiKey": "ollama",
      "systemPrompt": {
          "type": "file",
        "path": "system.md"
      },
      "temperature": 0.7
    }
    ```
1. Create a file `system.md` in the directory with any system prompts.

## How to Use
You can either run without building:

```bash
npm run dev
```

Or run after building:
```bash
npm run build
npm start
```

### Commands
Available commands:
- `/list` - List available agents.
- `/load <agent-name>` - Load an agent. The `<agent-name>` is the folder name under `agents` folder.
- `/history` - Show the history of the current agent.
- `/exit` or `/bye` - Exit the program.
- `/help` or `/?` - Show this help message.

### Chat
Type the message you want to send to the agent. **You need to use `/load` to load an agent first before sending.**

If you want to send a multi-line message, use triple single quotes (''') or triple double quotes (""") to start and end the message. For example:

```
'''
First line
Second line
Third line
'''
```

Or

```
"""
First line
Second line
Third line
"""
```

### Chat History
Chat history is autosaved under the agent folder with the name `history.json`.

## Agent File Schema
- `name`: The name of the agent.
- `model`: The model used.
- `baseURL`: The URL of the LLM server API.
- `apiKey`: The API key used by the LLM server. Please provide an API key with any value if your server is hosted locally.
- `systemPrompt`: (Optional) The system prompt.
    - If the `type` is `"file"`, please provide a `path` to the prompt file. The path is relative to the directory of the `config.json` file.
        ```json
        {
          "systemPrompt": {
            "type": "file",
            "path": "system.md"
          }
        }
        ```
    - If the `type` is `text`, please provide the prompt directly in the `content` field.
        ```json
        {
          "systemPrompt": {
            "type": "text",
            "content": "You are an assistant that answers user's questions."
          }
        }
        ```
- `temperature`: (Optional) The temperature used by the model. Default value is `0.7`.
