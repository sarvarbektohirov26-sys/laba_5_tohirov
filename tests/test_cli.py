"""Интеграционные тесты CLI через subprocess."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "main.py"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Запустить main.py с аргументами и вернуть результат."""
    return subprocess.run(
        [sys.executable, str(MAIN), *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )


class TestCLIBasic:
    def test_help_returns_zero(self):
        r = run_cli("--help")
        assert r.returncode == 0
        assert "--kind" in r.stdout

    def test_default_sine_success(self):
        r = run_cli("--kind", "sine", "--n", "10", "--window", "3", "--seed", "1")
        assert r.returncode == 0
        assert "SMA" in r.stdout
        assert "EMA" in r.stdout

    def test_random_kind_success(self):
        r = run_cli("--kind", "random", "--n", "15", "--window", "5", "--seed", "2")
        assert r.returncode == 0
        assert "Источник данных" in r.stdout

    def test_invalid_n_exits_1(self):
        r = run_cli("--n", "0")
        assert r.returncode == 1
        assert "Ошибка" in r.stderr

    def test_window_bigger_than_n_exits_1(self):
        r = run_cli("--kind", "sine", "--n", "5", "--window", "50")
        assert r.returncode == 1
        assert "Ошибка" in r.stderr


class TestCLIVariant11:
    def test_two_harmonics_runs(self):
        r = run_cli(
            "--kind", "two_harmonics", "--n", "200", "--seed", "42",
            "--window-values", "5", "25", "75",
        )
        assert r.returncode == 0
        assert "Экстремумы" in r.stdout
        assert "Сравнение сглаживания" in r.stdout

    def test_two_harmonics_warns_big_window(self):
        r = run_cli(
            "--kind", "two_harmonics", "--n", "50",
            "--window-values", "5", "100",
        )
        assert r.returncode == 0
        assert "[WARN]" in r.stdout


class TestCLIO:
    def test_save_and_load_roundtrip(self, tmp_path):
        save_path = tmp_path / "series.json"
        r1 = run_cli(
            "--kind", "sine", "--n", "20", "--seed", "1",
            "--save", str(save_path),
        )
        assert r1.returncode == 0
        assert save_path.exists()

        r2 = run_cli("--load", str(save_path), "--window", "3")
        assert r2.returncode == 0
        assert "файл:" in r2.stdout

    def test_export_csv(self, tmp_path):
        out = tmp_path / "out.csv"
        r = run_cli(
            "--kind", "trend", "--n", "10", "--seed", "3",
            "--export", str(out),
        )
        assert r.returncode == 0
        assert out.exists()
        # проверим, что файл содержит заголовок i,value
        text = out.read_text(encoding="utf-8")
        assert "i,value" in text

    def test_benchmark_flag(self):
        r = run_cli(
            "--kind", "sine", "--n", "100", "--window", "10", "--benchmark",
        )
        assert r.returncode == 0
        assert "list" in r.stdout
        assert "deque" in r.stdout