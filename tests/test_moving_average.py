"""Скользящие средние: SMA, центрированное MA, EMA + benchmark."""
from __future__ import annotations
import time
from collections import deque
from typing import List, Sequence


def _check_window(window: int, n: int) -> None:
    if not isinstance(window, int) or isinstance(window, bool):
        raise ValueError(f"window должен быть целым, получено: {window!r}")
    if window < 1:
        raise ValueError(f"window должен быть >= 1, получено: {window}")
    if window > n:
        # ИСПРАВЛЕНО: добавлено слово "больше" для прохождения теста
        raise ValueError(f"window ({window}) больше длины ряда ({n})")


def _check_alpha(alpha: float) -> None:
    if not (0 < alpha <= 1):
        raise ValueError(f"alpha должен быть в (0, 1], получено: {alpha}")


def simple_moving_average(data: Sequence[float], window: int) -> List[float]:
    """SMA через бегущую сумму (O(n))."""
    if not data:
        raise ValueError("Ряд пуст: расчёт невозможен")
    _check_window(window, len(data))

    running = sum(data[:window])
    result = [running / window]
    for i in range(window, len(data)):
        running += data[i] - data[i - window]
        result.append(running / window)
    return result


def centered_moving_average(data: Sequence[float], window: int) -> List[float]:
    """Центрированное MA. Окно должно быть нечётным."""
    if not data:
        raise ValueError("Ряд пуст: расчёт невозможен")
    if window % 2 == 0:
        raise ValueError(f"Центрированное МА требует нечётного window, получено: {window}")
    _check_window(window, len(data))

    half = window // 2
    return [
        sum(data[i - half:i + half + 1]) / window
        for i in range(half, len(data) - half)
    ]


def exponential_moving_average(data: Sequence[float], alpha: float) -> List[float]:
    """EMA: EMA[0]=data[0]; EMA[i]=alpha*data[i]+(1-alpha)*EMA[i-1]."""
    if not data:
        raise ValueError("Ряд пуст: расчёт невозможен")
    _check_alpha(alpha)

    result = [float(data[0])]
    for i in range(1, len(data)):
        result.append(alpha * data[i] + (1 - alpha) * result[-1])
    return result


def simple_moving_average_deque(data: Sequence[float], window: int) -> List[float]:
    """SMA с использованием deque (для бенчмарка)."""
    _check_window(window, len(data))
    result = []
    d = deque()
    running_sum = 0.0
    for x in data:
        d.append(x)
        running_sum += x
        if len(d) > window:
            running_sum -= d.popleft()
        if len(d) == window:
            result.append(running_sum / window)
    return result


def benchmark_moving_average(data: Sequence[float], window: int, repeats: int = 1000) -> dict:
    """Замеряет среднее время SMA: list vs deque."""
    _check_window(window, len(data))

    t0 = time.perf_counter()
    for _ in range(repeats):
        simple_moving_average(data, window)
    t_list = (time.perf_counter() - t0) / repeats

    t0 = time.perf_counter()
    for _ in range(repeats):
        simple_moving_average_deque(data, window)
    t_deque = (time.perf_counter() - t0) / repeats

    return {"list": t_list, "deque": t_deque}