from iccore import runtime
from iccore import logging_utils


def launch_common(args):
    runtime.ctx.set_is_dry_run(args.dry_run)
    logging_utils.setup_default_logger()


def serialize_args(cli_args: dict[str, str | None], delimiter="--") -> str:
    """
    Convert command line args given as dict key, value pairs
    to a string format.
    """
    ret = ""
    for key, value in cli_args.items():
        if value is None:
            value = ""
        ret += f" {delimiter}{key} {value}"
    return ret


def deserialize_args(cli_args: str, delimiter: str = "--") -> dict[str, str]:
    """
    Convert command line args in the form 'program --key0 value0 --key1 value1'
    to a dict of key value pairs.
    """
    stripped_entries = [e.strip() for e in cli_args.split()]
    args: dict = {}
    last_key = ""
    for entry in stripped_entries:
        if entry.startswith(delimiter):
            if last_key:
                # Flag
                args[last_key] = None
            last_key = entry[len(delimiter) :]
        else:
            if last_key:
                args[last_key] = entry
                last_key = ""
    if last_key:
        args[last_key] = None  # Handle trailing flag
    return args
