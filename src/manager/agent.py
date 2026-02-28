import argparse

from strands import Agent
from strands.models.openai import OpenAIModel

from manager.tools import bash

SYSTEM_PROMPT = """\
You are an autonomous task execution agent. Your job is to:

1. List open GitHub issues from the target repository
2. Analyze them and decide which task to work on next based on priority, urgency, and dependencies
3. Execute the chosen task using the bash tool
4. Report what you did and the result

You have access to a bash tool that can execute any shell command.
Use the `gh` CLI to interact with GitHub, and any other CLI tools as needed.

## Workflow

1. First, list all open issues using the gh command provided in the user prompt
2. Read the details of promising issues with `gh issue view <number> {repo_flag}`
3. Pick the most important/urgent one to work on
4. Execute the task (e.g. write code, run commands, create PRs, comment on issues)
5. Summarize what you accomplished

Be autonomous. Make decisions and take action.
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
    parser = argparse.ArgumentParser(description="AI task management agent")
    parser.add_argument("--repo", "-r", default=None, help="Target GitHub repository (e.g. myuon/some-repo)")
    args = parser.parse_args()

    agent = create_agent()

    if args.repo:
        repo_flag = f"-R {args.repo}"
    else:
        repo_flag = ""

    prompt = f"""\
Run `gh issue list {repo_flag}` to see all open issues, then pick the most important one and execute it.
Use `{repo_flag}` flag for all gh commands if specified.
"""

    agent(prompt)


if __name__ == "__main__":
    main()
