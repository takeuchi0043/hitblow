"""ゲーム全体の制限時間を扱う機能。"""

from __future__ import annotations

import queue
import threading
import time
from typing import Callable


class GameTimer:
    """残り時間と経過時間を計算する小さなタイマー。"""

    def __init__(
        self,
        limit_seconds: int | None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if limit_seconds is not None and limit_seconds <= 0:
            raise ValueError("制限時間は正の整数または None にしてください")
        self.limit_seconds = limit_seconds
        self._clock = clock
        self._started_at = clock()

    def elapsed(self) -> float:
        return max(0.0, self._clock() - self._started_at)

    def remaining(self) -> float | None:
        if self.limit_seconds is None:
            return None
        return max(0.0, self.limit_seconds - self.elapsed())

    def expired(self) -> bool:
        remaining = self.remaining()
        return remaining is not None and remaining <= 0


def choose_time_limit(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int | None:
    """制限時間を選ばせる。0または空入力なら時間制限なし。"""

    output_fn("制限時間: 0=なし、30/60/120=秒")
    while True:
        answer = input_fn("制限時間 [0] > ").strip() or "0"
        if answer in {"0", "なし", "none"}:
            return None
        if answer in {"30", "60", "120"}:
            return int(answer)
        output_fn("0、30、60、120 のどれかを入力してね")


def timed_input(
    prompt: str,
    timeout_seconds: float | None,
    input_fn: Callable[[str], str] = input,
) -> str:
    """指定秒数以内に入力を受け取る。

    input() はタイムアウト機能を持たないため、入力専用のデーモンスレッドを使う。
    時間切れ後はゲーム自体を終了する設計なので、待機中の入力スレッドが
    次の入力を奪う問題は起こらない。
    """

    if timeout_seconds is None:
        return input_fn(prompt)
    if timeout_seconds <= 0:
        raise TimeoutError("制限時間を超えました")

    result_queue: queue.Queue[tuple[bool, object]] = queue.Queue(maxsize=1)

    def read_input() -> None:
        try:
            result_queue.put((True, input_fn(prompt)))
        except BaseException as error:  # 入力側の例外を呼び出し元へ渡す
            result_queue.put((False, error))

    thread = threading.Thread(target=read_input, daemon=True)
    thread.start()

    try:
        succeeded, value = result_queue.get(timeout=timeout_seconds)
    except queue.Empty as error:
        raise TimeoutError("制限時間を超えました") from error

    if succeeded:
        return str(value)
    raise value  # type: ignore[misc]
