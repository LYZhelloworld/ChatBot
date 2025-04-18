# ChatBot
[简体中文](./README.md) | [English](./README_en.md) | [日本語](./README_ja.md)

ChatBot is an interactive chatting tool with local deployed LLM.

## Prerequisites
This tool is based on OpenAI API model.

Please install [Ollama](https://ollama.com) If you want to run locally. Otherwise, please provide an API token in the configuration file.

### Environment Setup
Please make sure you have Python 3.12 or higher installed. Recommended version is 3.13.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

```powershell
pip install uv
```

If you don't have `pip` installed, you can install `uv` using the following command:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If you are using Mac OS X or Linux, you can install `uv` using the following command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Activate the virtual environment.

```powershell
# Activate virtual environment
uv venv
.venv\Scripts\activate
```

### Create Agent
1. Create a folder `agents` under the `src` folder (if it does not exist).
    - If you are running the executable file, create the folder `agents` under the same directory as the executable file.
1. Create a folder under `agents` with a proper name **without spaces**. (For example, `my-agent`).
1. Add a configuration file in your agent folder with the name `config.json`. Below is an example:
    ```json
    {
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
Run with Python environment:

```powershell
uv run src/main.py
```

If you want to load an agent at startup, you can pass the agent name as an argument:

```powershell
uv run src/main.py my-agent
```

Build an executable file:

```powershell
pyinstaller --onefile --console --distpath dist --name "ChatBot" -y src/main.py
```

The executable file will be generated in the `dist` folder.

### Commands
Available commands:
- `/list` - List available agents.
- `/load <agent-name>` - Load an agent. The `<agent-name>` is the folder name under `agents` folder.
- `/history` - Show the history of the current agent.
- `/regen` or `/regenerate` - Regenerate the last response.
- `/exit` or `/bye` - Exit the program.
- `/help` or `/?` - Show this help message.

### Chat
Type the message you want to send to the agent. **You need to use `/load` to load an agent first before sending.**

Please press `Tab` key if you want to insert a newline to send multi-line messages. `Enter` key will send the message.

### Chat History
Chat history is autosaved under the `agent` folder with the name `history.json`.

## Agent File Schema
- `model`: The model used by the agent.
- `baseURL`: The URL of the LLM server API.
- `apiKey`: The API key used by the LLM server. Please provide an arbitrary API key if your server is hosted locally.
- `systemPrompt`: (Optional) The system prompt to be used by the agent. It can be either a file or a text string.
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
