"""ゲームの文字数（難易度）を選ぶ機能。"""

from __future__ import annotations

from typing import Callable

from .mode import ModeName, available_lengths


def choose_length(
    mode: ModeName,
    default: int | None = None,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    """モードに応じた有効な長さを選ばせる。"""

    choices = available_lengths(mode)
    selected_default = default if default in choices else choices[0]
    choices_text = ", ".join(str(value) for value in choices)

    while True:
        answer = input_fn(
            f"文字数を選んでください ({choices_text}) [{selected_default}] > "
        ).strip()
        if not answer:
            return selected_default
        if answer.isdigit() and int(answer) in choices:
            return int(answer)
        output_fn(f"{choices_text} の中から選んでね")
