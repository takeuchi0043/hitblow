"""ゲームの進行（入力・表示・ループ）。

★ チームで足す機能は **自分の担当の場所**に書く（1機能=1ファイル）。
   下の「ここに足す」場所は3か所（① 開始時 ② 入力コマンド ③ 勝利時）。
   ペアごとに**別の場所**を直すので、並行作業でも衝突しない。
   import も自分の場所の近くに書くこと（ファイル先頭にまとめない＝衝突回避）。
"""

from .core import judge


def play(digits=3):
    # ===== ① 開始時に足す（難易度・あいさつ など）: ここに書く =====
    from .continuous import ContinuousSession
    from .difficulty import choose_length
    from .history import GuessResult, format_history
    from .mode import choose_mode, make_mode_secret, mode_description
    from .time_limit import GameTimer, choose_time_limit

    mode = choose_mode()
    length = choose_length(mode, default=digits)
    continuous_session = ContinuousSession() if mode == "continuous" else None
    time_limit = (
        continuous_session.time_limit
        if continuous_session is not None
        else choose_time_limit()
    )
    secret = make_mode_secret(mode, length)
    timer = GameTimer(time_limit)

    print(f"Hit & Blow（{mode_description(mode, length)}）")
    if continuous_session is not None:
        print(f"第1問（制限時間 {continuous_session.time_limit} 秒）")

    tries = 0
    history: list[GuessResult] = []
    while True:
        # ===== ② 入力コマンドに足す（ヒント など）: ここに書く（import もここに） =====
        # 例:  from .hint import hint
        #      if guess == "h":
        #          print(hint(secret)); continue
        from .mode import normalize_guess, validate_guess
        from .time_limit import timed_input

        try:
            guess = timed_input("予想 > ", timer.remaining())
        except TimeoutError:
            print(f"時間切れ！ 答えは {secret} でした")
            if continuous_session is not None:
                print(f"最終スコア: {continuous_session.score} 問")
            return

        guess = normalize_guess(mode, guess)
        validation_error = validate_guess(mode, guess, length)
        if validation_error is not None:
            print(validation_error)
            continue

        tries += 1
        hit, blow = judge(secret, guess)
        history.append(GuessResult(guess, hit, blow))
        print(format_history(history))
        if hit == length:

            # ===== ③ 勝利時に足す（スコア・履歴 など）: ここに書く =====
            print(f"経過時間: {timer.elapsed():.1f} 秒")

            print(f"正解！ {tries} 回で当たり（答え {secret}）")
            if continuous_session is None:
                break

            continuous_session.record_clear()
            print(f"現在のスコア: {continuous_session.score} 問")

            secret = make_mode_secret(mode, length)
            timer = GameTimer(continuous_session.time_limit)
            tries = 0
            history = []
            print(
                f"\n第{continuous_session.score + 1}問"
                f"（制限時間 {continuous_session.time_limit} 秒）"
            )
