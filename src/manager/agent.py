import sys

from strands import Agent
from strands.models.openai import OpenAIModel

from manager.tools import bash

SYSTEM_PROMPT = """\
You are a project management assistant. You help manage GitHub issues and tasks.

You have access to a bash tool that can execute shell commands.
Use the `gh` CLI to interact with GitHub repositories.

Useful gh commands:
- `gh issue list` - List issues in the current repository
- `gh issue view <number>` - View a specific issue
- `gh issue create --title "..." --body "..."` - Create a new issue
- `gh issue list --label "bug"` - Filter issues by label
- `gh issue list --assignee "@me"` - List issues assigned to you
"""


def create_agent() -> Agent:
    model = OpenAIModel(
        model_id="gpt-4o",
        params={"max_tokens": 4096},
    )

    return Agent(
        model=model,
        tools=[bash],
        system_prompt=SYSTEM_PROMPT,
    )


def main():
    agent = create_agent()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "List all open issues in this repository."

    agent(query)


if __name__ == "__main__":
    main()
