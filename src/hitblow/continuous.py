"""連続モードのスコアと各問題の制限時間を管理する。"""

from __future__ import annotations

from dataclasses import dataclass


START_TIME_SECONDS = 120
TIME_DECREMENT_SECONDS = 10
MIN_TIME_SECONDS = 10


@dataclass
class ContinuousSession:
    """連続モード1回分の進行状態。"""

    score: int = 0

    @property
    def time_limit(self) -> int:
        """現在の問題に使う制限時間を秒で返す。"""

        return max(
            MIN_TIME_SECONDS,
            START_TIME_SECONDS - self.score * TIME_DECREMENT_SECONDS,
        )

    def record_clear(self) -> None:
        """問題を1問クリアしたことを記録する。"""

        self.score += 1
