# ChatBot
[简体中文](./README.md) | [English](./README_en.md) | [日本語](./README_ja.md)

ChatBot は、ローカルにデプロイされた LLM を使用したインタラクティブなチャットツールです。

## 前提条件
このツールは OpenAI API モデルに基づいています。

ローカルで実行する場合は [Ollama](https://ollama.com) をインストールしてください。そうでない場合は、設定ファイルに API トークンを提供してください。

### 環境設定
Python 3.12 以上がインストールされていることを確認してください。推奨バージョンは 3.13 です。

[uv](https://docs.astral.sh/uv/getting-started/installation/) をインストールします。

```powershell
pip install uv
```

`pip` がインストールされていない場合は、以下のコマンドを使用して `uv` をインストールできます：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Mac OS X または Linux を使用している場合は、以下のコマンドを使用して `uv` をインストールできます：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

仮想環境を有効化します。

```powershell
# 仮想環境を有効化
uv venv
.venv\Scripts\activate
```

### エージェントの作成
1. `src` フォルダの下に `agents` フォルダを作成します（存在しない場合）。
    - 実行可能ファイルを実行している場合は、実行可能ファイルと同じディレクトリに `agents` フォルダを作成します。
1. `agents` フォルダの下に適切な名前のフォルダを作成します（例：`my-agent`）。名前にはスペースを含めないでください。
1. エージェントフォルダに `config.json` という名前の設定ファイルを追加します。以下はその例です：
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
1. ディレクトリに `system.md` というファイルを作成し、システムプロンプトを記述します。

## 使用方法
Python 環境で実行します：

```powershell
uv run src/main.py
```

起動時にエージェントをロードしたい場合は、エージェント名を引数として渡すことができます：

```powershell
uv run src/main.py my-agent
```

実行可能ファイルをビルドします：

```powershell
pyinstaller --onefile --console --distpath dist --name "ChatBot" -y src/main.py
```

実行可能ファイルは `dist` フォルダに生成されます。

### コマンド
利用可能なコマンド：
- `/list` - 利用可能なエージェントを一覧表示します。
- `/load <agent-name>` - エージェントをロードします。`<agent-name>` は `agents` フォルダの下のフォルダ名です。
- `/history` - 現在のエージェントの履歴を表示します。
- `/regen` または `/regenerate` - 最後の応答を再生成します。
- `/exit` または `/bye` - プログラムを終了します。
- `/help` または `/?` - このヘルプメッセージを表示します。

### チャット
エージェントに送信したいメッセージを入力します。**メッセージを送信する前に、まず `/load` を使用してエージェントをロードする必要があります。**

複数行のメッセージを送信したい場合は、`Tab` キーを押して改行を挿入します。`Enter` キーでメッセージを送信します。

### チャット履歴
チャット履歴は `agent` フォルダの下に `history.json` という名前で自動保存されます。

## エージェントファイルのスキーマ
- `model`: エージェントが使用するモデル。
- `baseURL`: LLM サーバー API の URL。
- `apiKey`: LLM サーバーが使用する API キー。サーバーがローカルでホストされている場合は、任意の API キーを提供してください。
- `systemPrompt`: （オプション）エージェントが使用するシステムプロンプト。ファイルまたはテキスト文字列のいずれかです。
    - `type` が `"file"` の場合、プロンプトファイルの `path` を提供してください。パスは `config.json` ファイルのディレクトリに対して相対的です。
        ```json
        {
          "systemPrompt": {
            "type": "file",
            "path": "system.md"
          }
        }
        ```
    - `type` が `"text"` の場合、`content` フィールドにプロンプトを直接提供してください。
        ```json
        {
          "systemPrompt": {
            "type": "text",
            "content": "あなたはユーザーの質問に答えるアシスタントです。"
          }
        }
        ```
- `temperature`: （オプション）モデルが使用する温度値。デフォルト値は `0.7` です。
