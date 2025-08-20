# import pysnooper

from logging import Logger, getLogger
from subprocess import PIPE, Popen

log: Logger = getLogger(__name__)


# @pysnooper.snoop()
def shell_cmd(command: list, user: str | None = None) -> tuple[str, str, int]:
    if not command:
        raise ValueError("No command specified!")
    fmt_command = " ".join(command)
    if user:
        fmt_command = f"su {user} -c '{fmt_command}'"
    log.debug("Issuing system command: (%s)", fmt_command)
    with Popen(fmt_command, shell=True, stdout=PIPE, stderr=PIPE) as process:
        output, errors = process.communicate()
        log.debug("Output: (%s), Errors: (%s)", output, errors)
        return str(output).rstrip("\n"), str(errors).rstrip("\n"), process.returncode
