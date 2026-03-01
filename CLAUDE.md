# Manager - PDM Assistant

## Tech Stack

- Python 3.11+, uv (package manager)
- Strands Agents SDK (OpenAI provider, gpt-4o)
- GitHub CLI (`gh`) for issue management
- AWS Bedrock AgentCore Runtime (worker deployment)

## Architecture

- **PDM Agent** (`agent.py`): 対話型のPDMアシスタント。リポジトリの分析、タスク発見・精査、実装指示、PR管理を行う
- **Worker** (`worker.py`): コーディングタスクを受け取り自律的に実行するエージェント
- **Runtime** (`runtime.py`): AgentCore Runtime用のラッパー（ワーカーをHTTPエンドポイントとして公開）

## Secret Management

- **Infisical** を使用してシークレットを管理する
- `.env` ファイルは使わない
- アプリケーション実行時は `infisical run -- <command>` でシークレットを注入する

## Commands

- Interactive mode: `infisical run -- uv run manager -r owner/repo`
- Multiple repos: `infisical run -- uv run manager -r owner/repo1 -r owner/repo2`
- Auto analyze: `infisical run -- uv run manager --analyze -r owner/repo`
- Auto execute: `infisical run -- uv run manager --auto -r owner/repo`
- Run worker standalone: `infisical run -- uv run worker "<task>"`
- Run runtime locally: `infisical run -- uv run python -m manager.runtime`
- Install deps: `uv sync`

## Project Structure

```
src/manager/
  __init__.py
  agent.py    # PDM assistant (interactive REPL + auto modes)
  worker.py   # Worker agent (coding task execution)
  runtime.py  # AgentCore Runtime wrapper
  tools.py    # Shared tools (bash)
```
