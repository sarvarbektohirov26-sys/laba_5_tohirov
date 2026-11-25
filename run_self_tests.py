"""Автономный запуск проверок без pytest.

Запуск:
    python run_self_tests.py
"""
import traceback

CHECKS = []


def check(name):
    """Декоратор: регистрирует функцию как проверку."""
    def decorator(func):
        CHECKS.append((name, func))
        return func
    return decorator


# --- Проверки ---
@check("mean: базовый пример")
def _():
    from num_series.stats import mean
    assert mean([1, 2, 3]) == 2.0


@check("mean: пустой ряд → ValueError")
def _():
    from num_series.stats import mean
    try:
        mean([])
    except ValueError:
        return
    raise AssertionError("Ожидался ValueError")


@check("median: чётное и нечётное")
def _():
    from num_series.stats import median
    assert median([1, 2, 3]) == 2
    assert median([1, 2, 3, 4]) == 2.5


@check("spread: базовый пример")
def _():
    from num_series.stats import spread
    assert spread([1, 5, 2]) == 4.0


@check("SMA: классический пример")
def _():
    from num_series.moving_average import simple_moving_average
    assert simple_moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]


@check("SMA: окно > длины → ValueError")
def _():
    from num_series.moving_average import simple_moving_average
    try:
        simple_moving_average([1, 2], 3)
    except ValueError:
        return
    raise AssertionError("Ожидался ValueError")


@check("CMA: нечётное окно")
def _():
    from num_series.moving_average import centered_moving_average
    assert centered_moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]


@check("EMA: рекурсивная формула")
def _():
    from num_series.moving_average import exponential_moving_average
    res = exponential_moving_average([1, 2, 3], 0.5)
    assert abs(res[0] - 1.0) < 1e-9
    assert abs(res[1] - 1.5) < 1e-9
    assert abs(res[2] - 2.25) < 1e-9


@check("deque SMA == list SMA")
def _():
    from num_series.moving_average import simple_moving_average
    from num_series.deque_average import simple_moving_average_deque
    data = [1.5, -2.0, 3.25, 0.0, 7.1, -4.4]
    a = simple_moving_average(data, 3)
    b = simple_moving_average_deque(data, 3)
    assert len(a) == len(b)
    for x, y in zip(a, b):
        assert abs(x - y) < 1e-9


@check("JSON roundtrip")
def _():
    import tempfile
    from pathlib import Path
    from num_series.io_json import save_series_json, load_series_json
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "sub" / "s.json"
        save_series_json([1.0, 2.5, -3.75], p, meta={"kind": "sine"})
        loaded, meta = load_series_json(p, with_meta=True)
        assert loaded == [1.0, 2.5, -3.75]
        assert meta["kind"] == "sine"


@check("TXT: комментарии и пустые строки")
def _():
    import tempfile
    from pathlib import Path
    from num_series.io_file import load_series_txt
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.txt"
        p.write_text("# comment\n\n1.5\n\n2\n", encoding="utf-8")
        assert load_series_txt(p) == [1.5, 2.0]


@check("CSV: заголовок и разные разделители")
def _():
    import tempfile
    from pathlib import Path
    from num_series.io_file import load_series_csv
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.csv"
        p.write_text("value\n1.0,2.5\n3.0;4.5\n", encoding="utf-8")
        assert load_series_csv(p) == [1.0, 2.5, 3.0, 4.5]


@check("Вариант 11: экстремумы на простом ряду")
def _():
    from num_series.stats import count_extrema
    # 0 1 2 1 2 1 0: максимумы (2,4), минимум (3) → 3 экстремума
    assert count_extrema([0, 1, 2, 1, 2, 1, 0]) == 3


# --- Запуск ---
def run() -> int:
    total = len(CHECKS)
    passed = 0
    for name, func in CHECKS:
        try:
            func()
            print(f"[OK]   {name}")
            passed += 1
        except Exception:
            print(f"[FAIL] {name}")
            traceback.print_exc()
    print(f"\nИтого: {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(run())