# Manager - AI-powered Task Management Agent

## Tech Stack

- Python 3.11+, uv (package manager)
- Strands Agents SDK (OpenAI provider, gpt-4o)
- GitHub CLI (`gh`) for issue management

## Secret Management

- **Infisical** を使用してシークレットを管理する
- `.env` ファイルは使わない
- アプリケーション実行時は `infisical run -- <command>` でシークレットを注入する
- 例: `infisical run -- uv run manager`

## Commands

- Run agent: `infisical run -- uv run manager "<query>"`
- Install deps: `uv sync`

## Project Structure

```
src/manager/
  __init__.py
  agent.py    # Agent definition and entry point
  tools.py    # Custom tools (bash)
```
