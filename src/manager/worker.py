import sys

from strands import Agent
from strands.models.openai import OpenAIModel

from manager.tools import bash

SYSTEM_PROMPT = """\
You are a coding agent. You receive a task description and execute it autonomously.

You have access to a bash tool that can execute any shell command.
Use it to read files, write code, run tests, and interact with git.

## Guidelines

- Read existing code before making changes
- Follow the project's coding conventions
- Make minimal, focused changes
- Test your changes when possible
- Use git to create branches and commits for your work

## Available tools

- bash: Execute any shell command (file operations, git, code editing, etc.)

Execute the given task completely and report what you did.
"""


def create_worker() -> Agent:
    model = OpenAIModel(
        model_id="gpt-4o",
        params={"max_tokens": 4096},
    )

    return Agent(
        model=model,
        tools=[bash],
        system_prompt=SYSTEM_PROMPT,
    )


def run_worker(task: str) -> str:
    """Run the worker agent with a task and return the result."""
    agent = create_worker()
    result = agent(task)
    return str(result)


def main():
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        print("Usage: worker <task description>")
        sys.exit(1)

    run_worker(task)


if __name__ == "__main__":
    main()
