# ChatBot
[简体中文](./README.md) | [English](./README_en.md)

ChatBot 是一个基于本地部署 LLM 的交互式聊天工具。

## 前置条件
此工具基于 OpenAI API 模型。

如果希望本地运行，请安装 [Ollama](https://ollama.com)，否则请在配置文件中提供 API 密钥。

### 环境设置
请确保已安装 Python 3.12 或更高版本。推荐版本为 3.13。

安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)。

```powershell
pip install uv
```

如果你没有安装 `pip`，可以使用以下命令安装 `uv`：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

如果你用的是 Mac OS X 或 Linux，请使用以下命令安装 `uv`：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

激活虚拟环境。

```powershell
# 激活虚拟环境
uv venv
.venv\Scripts\activate
```

### 创建智能体
1. 在 `src` 文件夹下创建一个名为 `agents` 的文件夹（如果不存在的话）。
    - 如果运行的是可执行文件，请在可执行文件所在目录下创建 `agents` 文件夹。
1. 在 `agents` 文件夹下创建一个文件夹，注意文件夹的名字**不能有空格**。（例如：`my-agent`）。
1. 在该文件夹中添加一个名为 `config.json` 的配置文件。例如：
    ```json
    {
      "model": "qwen2.5-7b",
      "baseURL": "http://localhost:11434/v1",
      "apiKey": "ollama",
      "agentDescription": {
        "type": "file",
        "path": "system.md"
      },
      "temperature": 0.7
    }
    ```
1. 在该目录下创建一个名为 `system.md` 的文件，用于存放智能体提示词。

## 使用方法
```powershell
uv run src/main.py
```

如果你想在运行时加载一个智能体，可以将智能体的名字作为参数传递：
  
```powershell
uv run src/main.py my-agent
```

构建可执行文件：

```powershell
pyinstaller --onefile --console --distpath dist --name "ChatBot" -y src/main.py
```

可执行文件将生成在 `dist` 文件夹中。

### 命令
可用命令：
- `/list` - 列出可用的智能体。
- `/load <agent-name>` - 加载一个智能体。`<agent-name>` 是 `agents` 文件夹下的文件夹名称。
- `/history` - 显示当前智能体的历史记录。
- `/regen` 或 `/regenerate` - 重新生成上一次的回复。
- `/exit` 或 `/bye` - 退出程序。
- `/help` 或 `/?` - 显示帮助信息。

### 聊天
输入您想发送给智能体的消息。**在发送消息之前，您需要使用 `/load` 加载一个智能体。**

如果您想发送多行消息，请使用 `Tab` 来换行。`Enter` 键将发送消息。

### 聊天记录
聊天记录会自动保存在 `agent` 文件夹下，文件名为 `history.json`。

## 智能体文件结构
- `model`: 智能体使用的模型。
- `baseURL`: LLM 服务器 API 的 URL。
- `apiKey`: LLM 服务器使用的 API 密钥。如果服务器是本地托管的，请提供任意 API 密钥。
- `agentDescription`: （可选）智能体使用的提示词。可以是文件或文本字符串。
    - 如果 `type` 是 `"file"`，请提供提示文件的 `path`。路径是相对于 `config.json` 文件的目录。
        ```json
        {
          "agentDescription": {
            "type": "file",
            "path": "system.md"
          }
        }
        ```
    - 如果 `type` 是 `"text"`，请直接在 `content` 字段中提供提示词。
        ```json
        {
          "agentDescription": {
            "type": "text",
            "content": "你是一个 AI 助手，用于回答用户问题。"
          }
        }
        ```
- `userDescription`：（可选）用户使用的提示词。可以是文件或文本字符串。格式同 `agentDescription`。
- `temperature`: （可选）模型使用的温度值。默认值为 `0.7`。