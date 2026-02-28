import argparse

from strands import Agent, tool
from strands.models.openai import OpenAIModel

from manager.tools import bash
from manager.worker import run_worker


@tool
def delegate_task(task: str) -> str:
    """Delegate a coding task to the worker agent.

    Use this tool to hand off implementation tasks to a coding agent.
    Provide a clear, detailed task description including context from the issue.

    Args:
        task: A detailed description of the task to execute.
    """
    return run_worker(task)


SYSTEM_PROMPT = """\
You are a project manager agent. Your job is to:

1. List open GitHub issues from the target repository
2. Analyze them and decide which task to work on next based on priority, urgency, and dependencies
3. Delegate the chosen task to the worker agent using the delegate_task tool
4. Report the result back to the issue as a comment

You have access to:
- bash: Execute shell commands (use for gh CLI, reading issue details, commenting)
- delegate_task: Hand off coding/implementation tasks to a worker agent

## Workflow

1. Run `gh issue list` to see all open issues
2. Read the details of promising issues with `gh issue view <number>`
3. Pick the most important/urgent one
4. Use delegate_task to hand off the implementation work with a clear task description
5. Comment on the issue with the result using `gh issue comment`

Important: Use bash for GitHub CLI operations, and delegate_task for actual coding work.
"""


def create_agent() -> Agent:
    model = OpenAIModel(
        model_id="gpt-4o",
        params={"max_tokens": 4096},
    )

    return Agent(
        model=model,
        tools=[bash, delegate_task],
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
