def split_strip_lines(content: str, remove_empties: bool = True) -> list[str]:
    stripped_lines = [line.strip() for line in content.splitlines()]
    if remove_empties:
        return [line for line in stripped_lines if line]
    return stripped_lines
