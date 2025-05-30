# ChatBot
[简体中文](./README.md) | [English](./README_en.md)

ChatBot 是一个基于本地部署 LLM 的交互式聊天工具。

## 前置条件
此工具基于 OpenAI API 模型。

如果希望本地运行 LLM，可以考虑安装 [Ollama](https://ollama.com)，否则请在配置文件中提供 API 密钥。

## 环境设置

### 使用 Docker

构建容器：

```bash
docker build -t chatbot .
```

运行容器：

```bash
docker run -v "./src/agents:/app/src/agents" -it --rm -p 8501:8501 chatbot
```

如果你使用的是 Docker 上部署的 Ollama 服务器，并且创建了一个网络（假设名为 `ollama`）：

```bash
docker run -v "./src/agents:/app/src/agents" -it --rm -p 8501:8501 --network ollama chatbot
# 记得在 Agent 文件中设置 `baseURL` 为 `http://ollama:11434/v1`
```

### 不使用 Docker

请确保已安装 Python 3.12 或更高版本。推荐版本为 3.13。

安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)。

```bash
pip install uv
```

如果你没有安装 `pip`，可以使用以下命令安装 `uv`：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

创建虚拟环境并下载依赖。

```bash
uv venv
uv sync
```

## 创建智能体
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
      }
    }
    ```
1. 在该目录下创建一个名为 `system.md` 的文件，用于存放智能体提示词。

## 使用方法
```bash
uv run streamlit run src/main.py
```

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
- `modelParams`：（可选）智能体使用模型的参数。
    - `frequency_penalty`：（可选）在-2.0到2.0之间的数值。正值会根据新 token 在已有文本中的出现频率进行惩罚，降低模型逐字重复相同内容的可能性。
    - `max_tokens`：（可选）聊天补全生成的最大 token 数量。此参数可用于控制通过 API 生成文本的成本。
    - `presence_penalty`：（可选）在-2.0到2.0之间的数值。正值会根据新token是否已出现在文本中进行惩罚，增加模型转向新话题的可能性。
    - `temperature`：（可选）采样温度值，范围0到2。较高值（如0.8）会使输出更随机，较低值（如0.2）会使输出更专注且确定。
    - `top_p`：（可选）称为核采样的替代采样方式，模型会基于概率分布考虑结果。仅生成概率总和达到该阈值的最可能 token 组合（例如 top_p=0.9 时，模型会动态选择概率总和达 90% 的候选 token）。