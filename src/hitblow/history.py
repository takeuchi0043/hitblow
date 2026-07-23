"""予想と判定結果の入力履歴を表形式で表示する機能。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class GuessResult:
    """1ターン分の予想と判定結果。"""

    guess: str
    hit: int
    blow: int


def format_history(history: Sequence[GuessResult]) -> str:
    """入力履歴を見やすい表に整形する。"""

    guess_width = max(5, *(len(result.guess) for result in history))

    header = f"TURN | {'GUESS':^{guess_width}} | HIT | BLOW"
    separator = f"-----+{'-' * (guess_width + 2)}+-----+-----"
    rows = [
        (
            f"{turn:^5}| {result.guess:^{guess_width}} |"
            f" {result.hit:^3} | {result.blow:^3}"
        ).rstrip()
        for turn, result in enumerate(history, start=1)
    ]

    return "\n".join((header, separator, *rows))
