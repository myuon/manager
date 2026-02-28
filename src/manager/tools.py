import subprocess

from strands import tool


@tool
def bash(command: str) -> str:
    """Execute a bash command and return its output.

    Args:
        command: The bash command to execute.
    """
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    output = ""
    if result.stdout:
        output += result.stdout
    if result.stderr:
        output += f"\nSTDERR:\n{result.stderr}"
    if result.returncode != 0:
        output += f"\nExit code: {result.returncode}"

    return output.strip()
