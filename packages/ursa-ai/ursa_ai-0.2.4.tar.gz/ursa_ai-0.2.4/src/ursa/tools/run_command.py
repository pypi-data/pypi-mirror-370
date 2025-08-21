import subprocess

from langchain_core.tools import tool


@tool
def run_cmd(query: str, workspace_dir: str) -> str:
    """Run command from commandline in the directory workspace_dir"""

    print("RUNNING: ", query)
    print(
        "DANGER DANGER DANGER - THERE IS NO GUARDRAIL FOR SAFETY IN THIS IMPLEMENTATION - DANGER DANGER DANGER"
    )
    process = subprocess.Popen(
        query.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=workspace_dir,
    )

    stdout, stderr = process.communicate(timeout=600)

    print("STDOUT: ", stdout)
    print("STDERR: ", stderr)

    return f"STDOUT: {stdout} and STDERR: {stderr}"
