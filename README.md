# ChatBot
[简体中文](./README.md) | [English](./README_en.md)

ChatBot 是一个基于本地部署 LLM 的交互式聊天工具。

## 前置条件
此工具基于 OpenAI API 模型。

如果希望本地运行，请安装 [Ollama](https://ollama.com)，否则请在配置文件中提供 API 密钥。

### 环境设置
请确保已安装 Python 3.10 或更高版本。推荐版本为 3.13。

安装 [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)。

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# 检查 Poetry 是否安装成功
poetry --version
```

激活虚拟环境并安装依赖项。参见：[Managing environments](https://python-poetry.org/docs/managing-environments/#powershell)。

```powershell
# 激活虚拟环境
python -m venv .venv
Invoke-Expression (poetry env activate)

# 安装依赖项
poetry install
```

### 创建 Agent
1. 在 `src` 文件夹下创建一个名为 `agents` 的文件夹（如果不存在的话）。
    - 如果运行的是可执行文件，请在可执行文件所在目录下创建 `agents` 文件夹。
1. 在 `agents` 文件夹下创建一个文件夹，注意文件夹的名字**不能有空格**。（例如：`my-agent`）。
1. 在该文件夹中添加一个名为 `config.json` 的配置文件。例如：
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
1. 在该目录下创建一个名为 `system.md` 的文件，用于存放系统提示词。

## 使用方法
在 Python 环境中运行：

```powershell
python src/main.py
```

构建可执行文件：

```powershell
pyinstaller --onefile --console --distpath dist --name "ChatBot" -y src/main.py
```

可执行文件将生成在 `dist` 文件夹中。

### 命令
可用命令：
- `/list` - 列出可用的 agents。
- `/load <agent-name>` - 加载一个 agent。`<agent-name>` 是 `agents` 文件夹下的文件夹名称。
- `/history` - 显示当前 agent 的历史记录。
- `/regen` 或 `/regenerate` - 重新生成上一次的回复。
- `/exit` 或 `/bye` - 退出程序。
- `/help` 或 `/?` - 显示帮助信息。

### 聊天
输入您想发送给 agent 的消息。**在发送消息之前，您需要使用 `/load` 加载一个 agent。**

如果您想发送多行消息，请使用三个单引号（`'''`）或三个双引号（`"""`）来开始和结束消息。例如：

```
'''
第一行
第二行
第三行
'''
```

或者

```
"""
第一行
第二行
第三行
"""
```

### 聊天记录
聊天记录会自动保存在 agent 文件夹下，文件名为 `history.json`。

## Agent 文件结构
- `model`: agent 使用的模型。
- `baseURL`: LLM 服务器 API 的 URL。
- `apiKey`: LLM 服务器使用的 API 密钥。如果服务器是本地托管的，请提供任意 API 密钥。
- `systemPrompt`: （可选）agent 使用的系统提示词。可以是文件或文本字符串。
    - 如果 `type` 是 `"file"`，请提供提示文件的 `path`。路径是相对于 `config.json` 文件的目录。
        ```json
        {
          "systemPrompt": {
            "type": "file",
            "path": "system.md"
          }
        }
        ```
    - 如果 `type` 是 `"text"`，请直接在 `content` 字段中提供提示词。
        ```json
        {
          "systemPrompt": {
            "type": "text",
            "content": "你是一个 AI 助手，用于回答用户问题。"
          }
        }
        ```
- `temperature`: （可选）模型使用的温度值。默认值为 `0.7`。