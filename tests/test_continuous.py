"""連続モードのテスト。"""

from hitblow.continuous import ContinuousSession
from hitblow.game import play
from hitblow.mode import validate_guess


def test_time_limit_decreases_after_each_clear():
    session = ContinuousSession()

    assert session.time_limit == 120

    session.record_clear()
    assert session.score == 1
    assert session.time_limit == 110

    session.record_clear()
    assert session.score == 2
    assert session.time_limit == 100


def test_time_limit_does_not_drop_below_ten_seconds():
    session = ContinuousSession(score=20)

    assert session.time_limit == 10


def test_continuous_mode_uses_number_guess_rules():
    assert validate_guess("continuous", "123", 3) is None
    assert validate_guess("continuous", "112", 3) == "同じ数字は2回使わないでね"
    assert validate_guess("continuous", "ABC", 3) == "数字だけで入力してね"


def test_continuous_game_starts_next_question_and_reports_score(monkeypatch, capsys):
    from hitblow import difficulty, mode, time_limit

    secrets = iter(("123", "456"))
    guesses: list[str | BaseException] = ["123", TimeoutError()]

    class FakeTimer:
        limits: list[int | None] = []

        def __init__(self, limit_seconds):
            self.limit_seconds = limit_seconds
            self.limits.append(limit_seconds)

        def remaining(self):
            return self.limit_seconds

        def elapsed(self):
            return 1.0

    def fake_timed_input(_prompt, _timeout):
        result = guesses.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    monkeypatch.setattr(mode, "choose_mode", lambda: "continuous")
    monkeypatch.setattr(mode, "make_mode_secret", lambda _mode, _length: next(secrets))
    monkeypatch.setattr(difficulty, "choose_length", lambda _mode, default: default)
    monkeypatch.setattr(time_limit, "GameTimer", FakeTimer)
    monkeypatch.setattr(time_limit, "timed_input", fake_timed_input)
    monkeypatch.setattr(
        time_limit,
        "choose_time_limit",
        lambda: (_ for _ in ()).throw(AssertionError("連続モードでは呼ばない")),
    )

    play()

    output = capsys.readouterr().out
    assert FakeTimer.limits == [120, 110]
    assert "第1問（制限時間 120 秒）" in output
    assert "現在のスコア: 1 問" in output
    assert "第2問（制限時間 110 秒）" in output
    assert "時間切れ！ 答えは 456 でした" in output
    assert "最終スコア: 1 問" in output
