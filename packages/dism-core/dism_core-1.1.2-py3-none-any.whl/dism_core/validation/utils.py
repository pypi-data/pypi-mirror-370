import re
from pathlib import Path


def has_handler_class(file_path: str | Path, class_name: str) -> bool:
    pattern = re.compile(rf"(?m)^\s*class\s+{class_name}\s*\(")
    with open(file_path) as file:
        for line in file:
            if pattern.search(line):
                return True
    return False
