# ChatBot
[简体中文](./README.md) | [English](./README_en.md)

ChatBot is an interactive chatting tool with local deployed LLM.

## Prerequisites
This tool uses Ollama to run LLM locally.

## Environment Setup

### With Docker

Build and run container:

```bash
docker-compose up -d
```

Stop container:

```bash
docker-compose down
```

### Without Docker

Please make sure you have Python 3.12 or higher installed. Recommended version is 3.13.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
pip install uv
```

If you don't have `pip` installed, you can install `uv` using the following command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create virtual environment and install dependencies.

```bash
uv venv
uv sync
```

Run:
```bash
uv run streamlit run src/main.py
```

## Create An Agent
1. Create a folder `agents` under the `src` folder (if it does not exist).
    - If you are running the executable file, create the folder `agents` under the same directory as the executable file.
1. Create a folder under `agents` with a proper name **without spaces**. (For example, `my-agent`).
1. Add a configuration file in your agent folder with the name `config.json`. Below is an example:
    ```json
    {
      "model": "qwen2.5:7b",
      "agentDescription": {
        "type": "file",
        "path": "system.md"
      }
    }
    ```
1. Create a file `system.md` in the directory with any agent prompts.

### Chat History
Chat history is autosaved under the `agent` folder with the name `history.json`.

## Agent File Schema
- `model`: The model used by the agent.
- `baseURL`: The URL of the LLM server API. Leave it empty if you are using Docker deployment.
- `agentDescription`: (Optional) The prompt to be used by the agent. It can be either a file or a text string.
    - If the `type` is `"file"`, please provide a `path` to the prompt file. The path is relative to the directory of the `config.json` file.
        ```json
        {
          "agentDescription": {
            "type": "file",
            "path": "system.md"
          }
        }
        ```
    - If the `type` is `text`, please provide the prompt directly in the `content` field.
        ```json
        {
          "agentDescription": {
            "type": "text",
            "content": "You are an assistant that answers user's questions."
          }
        }
        ```
- `userDescription`: (Optional) The prompt to be used by the user. It can be either a file or a text string. The format is similar to `agentDescription`.
- `modelParams`: (Optional) The parameters passed to the model.
    - `temperature`: (Optional) What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
    - `top_p`: (Optional) An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.