import os
import sys


def get_script_dir():
    return os.path.dirname(__file__)


def detect_shell():
    shell = os.path.basename(os.getenv("SHELL", ""))
    return shell


def get_current_shell_addins():
    shell = detect_shell()
    script_dir = get_script_dir()

    if "zsh" in shell:
        return os.path.join(script_dir, "shell_addins.zsh")
    if "bash" in shell:
        return os.path.join(script_dir, "shell_addins.sh")
    if "fish" in shell:
        return os.path.join(script_dir, "shell_addins.fish")
    else:
        print(f"Unsupported shell: {shell}", file=sys.stderr)

    return ""
