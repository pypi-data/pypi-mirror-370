"""
shell utils
"""

import subprocess

from waflibs import log, filedir

logger = log.logger().get_logger()


def run_command(
    cmd,
    cwd=None,
    dry_run=False,
    shell=False,
    check=False,
    capture_output=True,
    pipe=False,
    input=None,
    split=True,
    env=None,
):
    """execute shell command"""

    logger.debug(f"original shell command: {cmd}")
    command = cmd
    if split and type(cmd) is str and not shell:
        logger.debug("command is of type string... splitting")

        command = cmd.split(" ")
        logger.debug(f"command join from split: {' '.join(command)}")
    logger.debug(f"shell command to execute: {command}")

    logger.debug(f"env: {env}")
    logger.debug(f"input: {input}")
    logger.debug(f"orig cwd: {cwd}")
    if cwd is None:
        real_cwd = None
    else:
        real_cwd = filedir.expand_vars(cwd)
    logger.debug(f"real cwd: {real_cwd}")

    if dry_run:
        if capture_output:
            return (
                "would return stdout",
                "would return stderr",
                "would return process",
            )
        else:
            return "would return process"
    else:
        stdout = None
        stderr = None
        if pipe:
            stdout = subprocess.PIPE
            capture_output = False

        process = subprocess.run(
            command,
            text=True,
            cwd=real_cwd,
            shell=shell,
            capture_output=capture_output,
            check=check,
            input=input,
            stdout=stdout,
            stderr=stderr,
            env=env,
        )
        if capture_output:
            return (process.stdout.strip(), process.stderr.strip(), process)
        else:
            return process


shell_command = run_command
command = run_command
cmd = run_command
