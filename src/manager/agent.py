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

ANALYZE_PROMPT = """\
You are a project manager agent in analysis mode. Your job is to:

1. For each target repository, list open GitHub issues
2. Read the details of each issue
3. Analyze priority, urgency, and dependencies
4. Report a summary of what should be done next for each repository

Do NOT execute any tasks or delegate to workers. Only analyze and report.
Output a clear summary for each repository with:
- Repository name
- Number of open issues
- The most important/urgent issue and why
- Recommended next action
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
    parser.add_argument("--repo", "-r", action="append", default=None, help="Target GitHub repository (e.g. myuon/some-repo). Can be specified multiple times.")
    parser.add_argument("--analyze", action="store_true", help="Analysis-only mode: report what to do without executing")
    args = parser.parse_args()

    if args.analyze:
        # Analysis mode: no worker delegation needed
        model = OpenAIModel(
            model_id="gpt-4o",
            params={"max_tokens": 4096},
        )
        agent = Agent(
            model=model,
            tools=[bash],
            system_prompt=ANALYZE_PROMPT,
        )
    else:
        agent = create_agent()

    repos = args.repo or [None]

    if args.analyze:
        repo_parts = []
        for repo in repos:
            if repo:
                repo_parts.append(f"- `gh issue list -R {repo}` (repo: {repo})")
            else:
                repo_parts.append("- `gh issue list` (current repo)")
        repo_list = "\n".join(repo_parts)

        prompt = f"""\
Analyze the following repositories and report what should be done next for each:

{repo_list}

For each repo, run `gh issue list` with the appropriate `-R` flag, then `gh issue view` for important issues.
Provide a comprehensive analysis summary.
"""
        agent(prompt)
    else:
        for repo in repos:
            if repo:
                repo_flag = f"-R {repo}"
            else:
                repo_flag = ""

            prompt = f"""\
Run `gh issue list {repo_flag}` to see all open issues, then pick the most important one and execute it.
Use `{repo_flag}` flag for all gh commands if specified.
"""
            agent(prompt)


if __name__ == "__main__":
    main()
