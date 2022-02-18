import shutil
from pathlib import Path
from typing import Sequence


def concatenate(inputs: Sequence[Path | str], output: Path | str) -> None:
    with open(output, "wb") as out:
        for input in inputs:
            with open(input, "rb") as inp:
                shutil.copyfileobj(inp, out)
