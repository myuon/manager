# Manager - AI-powered Task Management Agent

## Tech Stack

- Python 3.11+, uv (package manager)
- Strands Agents SDK (OpenAI provider, gpt-4o)
- GitHub CLI (`gh`) for issue management
- AWS Bedrock AgentCore Runtime (worker deployment)

## Architecture

- **Controller** (`agent.py`): GitHub Issuesを監視し、優先度を判断してワーカーにタスクを委譲
- **Worker** (`worker.py`): コーディングタスクを受け取り自律的に実行するエージェント
- **Runtime** (`runtime.py`): AgentCore Runtime用のラッパー（ワーカーをHTTPエンドポイントとして公開）

## Secret Management

- **Infisical** を使用してシークレットを管理する
- `.env` ファイルは使わない
- アプリケーション実行時は `infisical run -- <command>` でシークレットを注入する
- 例: `infisical run -- uv run manager`

## Commands

- Run controller: `infisical run -- uv run manager`
- Run controller (specific repo): `infisical run -- uv run manager --repo owner/repo`
- Run worker standalone: `infisical run -- uv run worker "<task>"`
- Run runtime locally: `infisical run -- uv run python -m manager.runtime`
- Install deps: `uv sync`

## Project Structure

```
src/manager/
  __init__.py
  agent.py    # Controller agent (issue triage + delegation)
  worker.py   # Worker agent (coding task execution)
  runtime.py  # AgentCore Runtime wrapper
  tools.py    # Shared tools (bash)
```
