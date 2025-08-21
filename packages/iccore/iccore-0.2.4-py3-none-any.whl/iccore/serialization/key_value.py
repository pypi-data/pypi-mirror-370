"""
Collection of utilties for converting between strings and key-value
like structures, including dicts.
"""


def get_key_value(content: str, delimiter: str = ":") -> dict[str, str]:
    """
    Given some content in a string, attempt to split it into a key-value
    pair using the given delimiter. Also strip any whitespace from
    the derived pair.
    """
    key, value = content.split(delimiter)
    return {key.strip(): value.strip()}


def _get_key_value_block(lines: list[str], delimiter: str = ":") -> tuple[int, dict]:
    """
    Given a list of strings (assumed lines) return identified
    key value pairs on lines as a dictionary.

    If a blank line is found then finish the 'block' and return the number
    of lines processed up to that point.
    """
    offset: int = 0
    block: dict[str, str] = {}
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            break
        block |= get_key_value(stripped_line, delimiter)
        offset += 1
    return offset + 1, block


def get_key_value_blocks(content: str, delimiter: str = ":") -> list[dict]:
    """
    Given a string containing 'blocks' of key value pairs separated by blank lines
    convert it into a list of dictionaries, one dict per blank-line separated block.
    """

    lines = content.splitlines()
    offset: int = 0
    blocks: list[dict] = []
    while offset < len(lines):
        lines_read, block = _get_key_value_block(lines[offset:], delimiter)
        offset += lines_read
        if block:
            blocks.append(block)
    return blocks
