import argparse

from strands import Agent, tool
from strands.agent.conversation_manager import SummarizingConversationManager
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


PDM_SYSTEM_PROMPT = """\
You are a PDM (Product Development Manager) assistant. You work alongside the user as a partner \
in deciding what the product should become, what tasks to prioritize, and how to execute them.

Your role is NOT just project management. You are expected to:
- Discuss product direction and strategy with the user
- Propose what should be built next and why
- Analyze repositories and discover tasks that need to be done
- Refine vague ideas into actionable, well-specified issues
- Break large issues into sub-issues
- Delegate implementation work to a coding worker agent
- Track PR status and follow up on reviews
- Provide status reports across multiple repositories

## How to interact

You are in a conversation with the user. Listen carefully, ask clarifying questions, \
and propose concrete actions. When the user agrees, execute them.

Do not act autonomously without confirmation unless the user has explicitly asked you to.

## Available tools

- **bash**: Execute shell commands. Use `gh` CLI for all GitHub operations:
  - `gh issue list -R owner/repo` - List issues
  - `gh issue view NUMBER -R owner/repo` - View issue details
  - `gh issue create -R owner/repo -t "title" -b "body"` - Create issues
  - `gh issue edit NUMBER -R owner/repo` - Edit issues
  - `gh pr list -R owner/repo` - List PRs
  - `gh pr view NUMBER -R owner/repo` - View PR details
  - `gh pr checks NUMBER -R owner/repo` - Check CI status
  - `gh api ...` - GitHub API calls for advanced operations
  - Other shell commands as needed

- **delegate_task**: Hand off coding/implementation tasks to a worker agent. \
Use this when the user approves executing a task. Provide detailed context.

## Managed repositories

{repos}

## Guidelines

1. When analyzing repositories, look at issues, PRs, recent commits, and overall project health
2. When suggesting new tasks, explain WHY they matter for the product
3. When refining issues, produce a clear spec with acceptance criteria
4. When breaking down issues, create sub-issues on GitHub and link them
5. Always confirm with the user before creating issues, closing issues, or delegating tasks
6. Present information in a structured, scannable format
7. Respond in the same language the user uses
"""

AUTO_ANALYZE_PROMPT = """\
Analyze the following repositories and provide a comprehensive status report:

{repo_commands}

For each repository:
1. List open issues and their priorities
2. List open PRs and their review status
3. Check recent commits for activity
4. Identify the most important/urgent items
5. Recommend next actions

Present a clear, structured summary.
"""

AUTO_EXECUTE_PROMPT = """\
Analyze the following repositories and execute the most important task:

{repo_commands}

1. List open issues across all repos
2. Analyze priority and urgency
3. Pick the most important task
4. Delegate it to the worker agent
5. Report the result as a comment on the issue
"""


def create_pdm_agent(repos: list[str]) -> Agent:
    model = OpenAIModel(
        model_id="gpt-4o",
        params={"max_tokens": 8192},
    )

    repo_lines = [f"- {repo}" for repo in repos] if repos else ["- (current repository)"]
    repo_display = "\n".join(repo_lines)

    system_prompt = PDM_SYSTEM_PROMPT.format(repos=repo_display)

    return Agent(
        model=model,
        tools=[bash, delegate_task],
        system_prompt=system_prompt,
        conversation_manager=SummarizingConversationManager(),
    )


def interactive_loop(agent: Agent, repos: list[str]):
    repo_display = ", ".join(repos) if repos else "current repo"
    print(f"\nPDM Assistant ready. Managing: {repo_display}")
    print("Type your message (Ctrl+D or 'exit' to quit).\n")

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        agent(user_input)
        print()


def auto_run(agent: Agent, repos: list[str], analyze_only: bool = False):
    repo_commands = []
    for repo in repos:
        repo_commands.append(f"- Repository: {repo} (use `-R {repo}` with gh commands)")
    if not repo_commands:
        repo_commands.append("- Current repository (no -R flag needed)")
    repo_cmd_text = "\n".join(repo_commands)

    if analyze_only:
        prompt = AUTO_ANALYZE_PROMPT.format(repo_commands=repo_cmd_text)
    else:
        prompt = AUTO_EXECUTE_PROMPT.format(repo_commands=repo_cmd_text)

    agent(prompt)


def main():
    parser = argparse.ArgumentParser(description="PDM Assistant - AI-powered product development manager")
    parser.add_argument("--repo", "-r", action="append", default=None,
                        help="Target repository (can be specified multiple times)")
    parser.add_argument("--auto", action="store_true",
                        help="Autonomous mode: act without user interaction")
    parser.add_argument("--analyze", action="store_true",
                        help="Analysis-only mode (implies --auto)")
    args = parser.parse_args()

    repos = args.repo or []
    agent = create_pdm_agent(repos)

    if args.analyze or args.auto:
        auto_run(agent, repos, analyze_only=args.analyze)
    else:
        interactive_loop(agent, repos)


if __name__ == "__main__":
    main()
