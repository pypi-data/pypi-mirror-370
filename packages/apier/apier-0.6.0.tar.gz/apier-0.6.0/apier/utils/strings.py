import re


def to_pascal_case(text: str) -> str:
    """
    Returns the PascalCase string of the given input.
    """
    words = re.findall("[a-zA-Z0-9]+", text)
    pascal_case_text = "".join(word[0].upper() + word[1:] for word in words)
    return pascal_case_text


def to_snake_case(text: str) -> str:
    """
    Returns the snake_case string of the given input.
    """
    temp = re.sub("([A-Z]+)", r" \1", text.replace("-", " "))
    temp = re.sub("([^a-zA-Z0-9\n]+)", r"_", temp.strip().replace("-", " "))
    return temp.lower()
