"""数字・単語・記号モードを扱う機能。

1機能を1ファイルに分けるというチーム開発ルールに合わせ、
出題、入力の正規化、入力チェックをこのファイルにまとめる。
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Literal, Protocol

ModeName = Literal["number", "word", "symbol"]


class RandomSource(Protocol):
    def sample(self, population, k: int): ...

    def choice(self, sequence): ...


@dataclass(frozen=True)
class ModeSpec:
    """各ゲームモードの表示名と利用可能な長さ。"""

    name: ModeName
    label: str
    lengths: tuple[int, ...]


NUMBER_ALPHABET = "0123456789"
SYMBOL_ALPHABET = "!?#$%&@*+-"

# 答えとして出題する「意味のある英単語」。
# Hit & Blowとして分かりやすいよう、同じ文字を含まない単語を選んでいる。
WORDS: dict[int, tuple[str, ...]] = {
    4: ("GAME", "CODE", "PLAY", "MATH", "QUIZ", "FISH", "BIRD", "STAR"),
    5: ("BRAIN", "MUSIC", "WORLD", "LIGHT", "HOUSE", "TRAIN", "BEACH", "CLOUD"),
    6: ("PLANET", "FRIEND", "MARKET", "STREAM", "BRIGHT", "GARDEN"),
}

MODES: dict[ModeName, ModeSpec] = {
    "number": ModeSpec("number", "数字", tuple(range(3, 11))),
    "word": ModeSpec("word", "英単語", tuple(WORDS)),
    "symbol": ModeSpec("symbol", "記号", tuple(range(3, 9))),
}

MENU_TO_MODE: dict[str, ModeName] = {
    "1": "number",
    "2": "word",
    "3": "symbol",
    "number": "number",
    "word": "word",
    "symbol": "symbol",
}


def choose_mode(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> ModeName:
    """プレイヤーにモードを選ばせる。空入力なら数字モード。"""

    output_fn("モードを選んでください")
    output_fn("  1: 数字  2: 意味のある英単語  3: 記号")

    while True:
        answer = input_fn("モード [1] > ").strip().lower() or "1"
        mode = MENU_TO_MODE.get(answer)
        if mode is not None:
            return mode
        output_fn("1、2、3 のどれかを入力してね")


def available_lengths(mode: ModeName) -> tuple[int, ...]:
    """指定モードで選べる文字数を返す。"""

    return MODES[mode].lengths


def make_mode_secret(
    mode: ModeName,
    length: int,
    rng: RandomSource | None = None,
) -> str:
    """モードと長さに合う答えを生成する。"""

    if length not in available_lengths(mode):
        raise ValueError(f"{mode} モードでは長さ {length} を使えません")

    source = rng if rng is not None else random

    if mode == "number":
        return "".join(source.sample(NUMBER_ALPHABET, length))
    if mode == "word":
        return source.choice(WORDS[length])
    return "".join(source.sample(SYMBOL_ALPHABET, length))


def normalize_guess(mode: ModeName, guess: str) -> str:
    """比較しやすいよう入力を整える。英単語は大文字化する。"""

    cleaned = guess.strip()
    return cleaned.upper() if mode == "word" else cleaned


def validate_guess(mode: ModeName, guess: str, length: int) -> str | None:
    """入力がルールに合わない場合はエラーメッセージを返す。"""

    if len(guess) != length:
        return f"{length} 文字で入力してね"

    if mode == "number":
        if not guess.isascii() or not guess.isdigit():
            return "数字だけで入力してね"
        if len(set(guess)) != length:
            return "同じ数字は2回使わないでね"
        return None

    if mode == "word":
        if not guess.isascii() or not guess.isalpha():
            return "半角英字だけで入力してね"
        return None

    if any(character not in SYMBOL_ALPHABET for character in guess):
        return f"使える記号は {SYMBOL_ALPHABET} です"
    if len(set(guess)) != length:
        return "同じ記号は2回使わないでね"
    return None


def mode_description(mode: ModeName, length: int) -> str:
    """ゲーム開始時に表示するルール説明を返す。"""

    if mode == "number":
        return f"数字モード（{length}桁・重複なし）"
    if mode == "word":
        return f"英単語モード（{length}文字・答えは意味のある英単語）"
    return f"記号モード（{length}文字・重複なし・使用可能: {SYMBOL_ALPHABET}）"
