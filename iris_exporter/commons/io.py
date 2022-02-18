import shutil
from pathlib import Path


def concatenate(inputs: list[Path | str], output: Path | str):
    with open(output, "wb") as out:
        for input in inputs:
            with open(input, "rb") as inp:
                shutil.copyfileobj(inp, out)
