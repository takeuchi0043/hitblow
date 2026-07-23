"""入力履歴の表表示をテストする。"""

from hitblow.history import GuessResult, format_history


def test_format_history():
    history = [
        GuessResult("1234", 1, 2),
        GuessResult("1567", 0, 1),
    ]

    assert format_history(history) == (
        "TURN | GUESS | HIT | BLOW\n"
        "-----+-------+-----+-----\n"
        "  1  | 1234  |  1  |  2\n"
        "  2  | 1567  |  0  |  1"
    )


def test_format_history_expands_guess_column_for_long_input():
    history = [GuessResult("ABCDEFGHIJ", 10, 0)]

    lines = format_history(history).splitlines()

    assert lines[0] == "TURN |   GUESS    | HIT | BLOW"
    assert lines[1] == "-----+------------+-----+-----"
    assert lines[2] == "  1  | ABCDEFGHIJ | 10  |  0"
