"""パフォーマンステスト (SC-PY-007 対応).

parse_symbol の処理時間が 1ms (0.001秒) 以内で完了することを検証する。
"""

import time

import pytest

from marketsymbol import parse_symbol

# パフォーマンス要件: 1ms = 0.001秒
MAX_PARSE_TIME_SECONDS = 0.001


class TestParseSymbolPerformance:
    """parse_symbol のパフォーマンステスト."""

    @pytest.mark.parametrize(
        "symbol",
        [
            "XJPX:7203",  # Equity
            "XJPX:NK:20250314:F",  # Future
            "XJPX:N225O:20250314:C:42000",  # Option
            "XJPX:N225O:20250314:O",  # Option series
        ],
        ids=["equity", "future", "option", "series"],
    )
    def test_parse_symbol_under_1ms(self, symbol: str) -> None:
        """parse_symbol が 1ms 以内で完了する.

        Args:
            symbol: テスト対象のシンボル文字列.
        """
        # Warm up - JIT やキャッシュの影響を排除
        for _ in range(100):
            parse_symbol(symbol)

        # 測定: 1000 回実行して平均を取る
        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            parse_symbol(symbol)
        elapsed = time.perf_counter() - start
        average_time = elapsed / iterations

        assert average_time < MAX_PARSE_TIME_SECONDS, (
            f"parse_symbol('{symbol}') took {average_time * 1000:.3f}ms "
            f"(expected < {MAX_PARSE_TIME_SECONDS * 1000}ms)"
        )

    def test_normalize_symbol_performance(self) -> None:
        """正規化を含む parse_symbol が 1ms 以内で完了する."""
        from marketsymbol import normalize_symbol

        # 正規化が必要な入力
        symbols = [
            "xjpx:7203",  # 小文字
            "ＸＪＰＸ：７２０３",  # noqa: RUF001  # 全角文字テスト
            "  XJPX:7203  ",  # 空白
        ]

        for symbol in symbols:
            # Warm up
            for _ in range(100):
                normalize_symbol(symbol)

            # 測定
            iterations = 1000
            start = time.perf_counter()
            for _ in range(iterations):
                normalize_symbol(symbol)
            elapsed = time.perf_counter() - start
            average_time = elapsed / iterations

            assert average_time < MAX_PARSE_TIME_SECONDS, (
                f"normalize_symbol('{symbol}') took {average_time * 1000:.3f}ms "
                f"(expected < {MAX_PARSE_TIME_SECONDS * 1000}ms)"
            )
