from typing import *

import click
import preparse

__all__ = ["calculate", "main", "score"]

_VALUES: dict = {
    "A": 1.8,
    "C": 2.5,
    "D": -3.5,
    "E": -3.5,
    "F": 2.8,
    "G": -0.4,
    "H": -3.2,
    "I": 4.5,
    "K": -3.9,
    "L": 3.8,
    "M": 1.9,
    "N": -3.5,
    "P": -1.6,
    "Q": -3.5,
    "R": -4.5,
    "S": -0.8,
    "T": -0.7,
    "V": 4.2,
    "W": -0.9,
    "X": None,
    "Y": -1.3,
    "-": None,
}


def score(seq: Iterable) -> float:
    "This function calculates the GRAVY score."
    l: list = list()
    x: Any
    for x in seq:
        y = _VALUES[str(x)]
        if y is not None:
            l.append(y)
    if len(l):
        return sum(l) / len(l)
    else:
        return float("nan")


calculate = score  # for legacy


@preparse.PreParser().click()
@click.command(add_help_option=False)
@click.option(
    "--format",
    "f",
    help="format of the output",
    default=".5f",
    show_default=True,
)
@click.help_option("-h", "--help")
@click.version_option(None, "-V", "--version")
@click.argument("seq")
def main(seq: Iterable, f: str) -> None:
    "This command calculates the GRAVY score of seq."
    ans: float = score(seq)
    out: str = format(ans, f)
    click.echo(out)
