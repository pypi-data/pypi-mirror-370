"""
git utils
"""

from . import log, shell

logger = log.logger().get_logger()


def commit_to_git(message, cwd=None):
    """shell command to commit to git"""

    cmd = ["git", "commit", "--all", "--message", message]

    stdout, stderr, _ = shell.command(cmd, cwd=cwd)
    return (stdout, stderr)


def push_to_git(cwd=None, *args):
    """shell command to push to git"""

    if args:
        cmd = [
            "git",
            "push",
            args,
        ]
    else:
        cmd = [
            "git",
            "push",
        ]
    logger.debug(f"current working dir: {cwd}")

    stdout, stderr, _ = shell.command(cmd, cwd=cwd)
    return (stdout, stderr)


def commit_and_push_to_git(message, cwd=None, *args):
    """shell command to command and push to git"""

    commit_stdout, commit_stderr = commit_to_git(message, cwd)
    push_stdout, push_stderr = push_to_git(cwd, *args)

    return (commit_stdout, commit_stderr, push_stdout, push_stderr)
