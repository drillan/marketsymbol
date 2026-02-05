"""parser モジュールのテスト.

normalize_symbol と parse_symbol のテストを含む。
"""

import pytest

from marketsymbol.enums import AssetClass, OptionType
from marketsymbol.errors import ErrorCode, SymbolParseError
from marketsymbol.parser import normalize_symbol, parse_symbol
from marketsymbol.symbol import EquitySymbol, FutureSymbol, OptionSymbol


class TestNormalizeSymbol:
    """normalize_symbol() のテスト."""

    def test_uppercase_conversion(self) -> None:
        """小文字を大文字に変換する."""
        assert normalize_symbol("xjpx:7203") == "XJPX:7203"

    def test_mixed_case(self) -> None:
        """大文字小文字混在を大文字に変換する."""
        assert normalize_symbol("XjPx:nK:20250314:F") == "XJPX:NK:20250314:F"

    def test_fullwidth_to_halfwidth(self) -> None:
        """全角文字を半角文字に変換する (NFKC 正規化)."""
        assert normalize_symbol("ＸＪＰＸ：７２０３") == "XJPX:7203"  # noqa: RUF001

    def test_fullwidth_lowercase_to_halfwidth_uppercase(self) -> None:
        """全角小文字を半角大文字に変換する."""
        assert normalize_symbol("ｘｊｐｘ：７２０３") == "XJPX:7203"  # noqa: RUF001

    def test_strip_leading_whitespace(self) -> None:
        """前方の空白を除去する."""
        assert normalize_symbol("  XJPX:7203") == "XJPX:7203"

    def test_strip_trailing_whitespace(self) -> None:
        """後方の空白を除去する."""
        assert normalize_symbol("XJPX:7203  ") == "XJPX:7203"

    def test_strip_both_whitespace(self) -> None:
        """前後の空白を除去する."""
        assert normalize_symbol("  XJPX:7203  ") == "XJPX:7203"

    def test_strip_fullwidth_whitespace(self) -> None:
        """全角スペースを除去する."""
        assert normalize_symbol("\u3000XJPX:7203\u3000") == "XJPX:7203"

    def test_fullwidth_colon_to_halfwidth(self) -> None:
        """全角コロンを半角コロンに変換する."""
        assert normalize_symbol("XJPX：7203") == "XJPX:7203"  # noqa: RUF001

    def test_combined_normalization(self) -> None:
        """複数の正規化を組み合わせる."""
        # 全角小文字 + 全角コロン + 全角数字 + 前後空白
        assert (
            normalize_symbol("　ｘｊｐｘ：ｎｋ：２０２５０３１４：Ｆ　")  # noqa: RUF001
            == "XJPX:NK:20250314:F"
        )

    def test_already_normalized(self) -> None:
        """既に正規化済みの文字列はそのまま返す."""
        assert normalize_symbol("XJPX:7203") == "XJPX:7203"

    def test_empty_string(self) -> None:
        """空文字列は空文字列を返す."""
        assert normalize_symbol("") == ""

    def test_whitespace_only(self) -> None:
        """空白のみは空文字列を返す."""
        assert normalize_symbol("   ") == ""

    def test_option_symbol_normalization(self) -> None:
        """オプションシンボルの正規化."""
        assert (
            normalize_symbol("xjpx:nk:20250314:c:40000") == "XJPX:NK:20250314:C:40000"
        )


class TestParseSymbolEquity:
    """parse_symbol() の Equity テスト."""

    def test_parse_equity_symbol(self) -> None:
        """株式シンボルをパースする."""
        result = parse_symbol("XJPX:7203")
        assert isinstance(result, EquitySymbol)
        assert result.exchange == "XJPX"
        assert result.code == "7203"
        assert result.asset_class == AssetClass.EQUITY

    def test_parse_equity_symbol_with_alpha_code(self) -> None:
        """英字コードの株式シンボルをパースする."""
        result = parse_symbol("XNAS:AAPL")
        assert isinstance(result, EquitySymbol)
        assert result.exchange == "XNAS"
        assert result.code == "AAPL"

    def test_parse_equity_symbol_normalized(self) -> None:
        """小文字の株式シンボルをパース (正規化される)."""
        result = parse_symbol("xjpx:7203")
        assert isinstance(result, EquitySymbol)
        assert result.exchange == "XJPX"
        assert result.code == "7203"

    def test_parse_equity_symbol_fullwidth(self) -> None:
        """全角の株式シンボルをパース (正規化される)."""
        result = parse_symbol("ＸＪＰＸ：７２０３")  # noqa: RUF001
        assert isinstance(result, EquitySymbol)
        assert result.exchange == "XJPX"
        assert result.code == "7203"


class TestParseSymbolFuture:
    """parse_symbol() の Future テスト."""

    def test_parse_future_symbol(self) -> None:
        """先物シンボルをパースする."""
        result = parse_symbol("XJPX:NK:20250314:F")
        assert isinstance(result, FutureSymbol)
        assert result.exchange == "XJPX"
        assert result.code == "NK"
        assert result.expiry == "20250314"
        assert result.asset_class == AssetClass.FUTURE

    def test_parse_future_symbol_normalized(self) -> None:
        """小文字の先物シンボルをパース (正規化される)."""
        result = parse_symbol("xjpx:nk:20250314:f")
        assert isinstance(result, FutureSymbol)
        assert result.exchange == "XJPX"
        assert result.code == "NK"
        assert result.expiry == "20250314"


class TestParseSymbolOption:
    """parse_symbol() の Option テスト."""

    def test_parse_call_option_symbol(self) -> None:
        """コールオプションシンボルをパースする."""
        result = parse_symbol("XJPX:NK:20250314:C:40000")
        assert isinstance(result, OptionSymbol)
        assert result.exchange == "XJPX"
        assert result.code == "NK"
        assert result.expiry == "20250314"
        assert result.option_type == OptionType.CALL
        assert result.strike == 40000
        assert result.asset_class == AssetClass.OPTION

    def test_parse_put_option_symbol(self) -> None:
        """プットオプションシンボルをパースする."""
        result = parse_symbol("XJPX:NK:20250314:P:38000")
        assert isinstance(result, OptionSymbol)
        assert result.option_type == OptionType.PUT
        assert result.strike == 38000

    def test_parse_series_option_symbol(self) -> None:
        """シリーズオプションシンボルをパースする."""
        result = parse_symbol("XJPX:NK:20250314:O")
        assert isinstance(result, OptionSymbol)
        assert result.option_type == OptionType.SERIES
        assert result.strike is None

    def test_parse_option_symbol_normalized(self) -> None:
        """小文字のオプションシンボルをパース (正規化される)."""
        result = parse_symbol("xjpx:nk:20250314:c:40000")
        assert isinstance(result, OptionSymbol)
        assert result.exchange == "XJPX"
        assert result.code == "NK"
        assert result.option_type == OptionType.CALL
        assert result.strike == 40000


class TestParseSymbolErrors:
    """parse_symbol() のエラーテスト."""

    def test_parse_empty_string(self) -> None:
        """空文字列は E004 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("")
        assert exc_info.value.error_code == ErrorCode.INVALID_SEGMENT_COUNT

    def test_parse_invalid_exchange(self) -> None:
        """無効な exchange は E007 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XXX:7203")
        assert exc_info.value.error_code == ErrorCode.UNKNOWN_EXCHANGE

    def test_parse_single_segment(self) -> None:
        """セグメントが1つだけは E004 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX")
        assert exc_info.value.error_code == ErrorCode.INVALID_SEGMENT_COUNT

    def test_parse_three_segments_no_type(self) -> None:
        """3セグメントでタイプなしは E004 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314")
        assert exc_info.value.error_code == ErrorCode.INVALID_SEGMENT_COUNT

    def test_parse_future_with_strike(self) -> None:
        """先物に strike を指定すると E001 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:F:40000")
        assert exc_info.value.error_code == ErrorCode.FUTURE_WITH_STRIKE

    def test_parse_call_without_strike(self) -> None:
        """コールオプションに strike なしは E002 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:C")
        assert exc_info.value.error_code == ErrorCode.OPTION_WITHOUT_STRIKE

    def test_parse_put_without_strike(self) -> None:
        """プットオプションに strike なしは E002 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:P")
        assert exc_info.value.error_code == ErrorCode.OPTION_WITHOUT_STRIKE

    def test_parse_series_with_strike(self) -> None:
        """シリーズオプションに strike を指定すると E001 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:O:40000")
        assert exc_info.value.error_code == ErrorCode.FUTURE_WITH_STRIKE

    def test_parse_invalid_expiry_format(self) -> None:
        """無効な expiry フォーマットは E003 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:2025031:F")
        assert exc_info.value.error_code == ErrorCode.INVALID_EXPIRY_FORMAT

    def test_parse_invalid_expiry_date(self) -> None:
        """無効な日付は E005 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250230:F")
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE

    def test_parse_invalid_option_type(self) -> None:
        """無効な option_type は E006 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:X")
        assert exc_info.value.error_code == ErrorCode.INVALID_OPTION_TYPE

    def test_parse_invalid_strike_not_numeric(self) -> None:
        """数値でない strike は E009 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:C:ABC")
        assert exc_info.value.error_code == ErrorCode.INVALID_STRIKE_VALUE

    def test_parse_invalid_strike_zero(self) -> None:
        """strike が 0 は E009 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:C:0")
        assert exc_info.value.error_code == ErrorCode.INVALID_STRIKE_VALUE

    def test_parse_invalid_strike_negative(self) -> None:
        """負の strike は E009 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:C:-100")
        assert exc_info.value.error_code == ErrorCode.INVALID_STRIKE_VALUE

    def test_parse_too_many_segments(self) -> None:
        """セグメントが多すぎると E004 エラーを発生する."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("XJPX:NK:20250314:C:40000:EXTRA")
        assert exc_info.value.error_code == ErrorCode.INVALID_SEGMENT_COUNT

    def test_parse_type_error_not_string(self) -> None:
        """str でない入力は TypeError を発生する."""
        with pytest.raises(TypeError):
            parse_symbol(12345)  # type: ignore[arg-type]

    def test_raw_symbol_in_error(self) -> None:
        """エラーに raw_symbol が含まれる."""
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol("INVALID")
        assert exc_info.value.raw_symbol == "INVALID"


class TestParseSymbolEdgeCases:
    """parse_symbol() のエッジケーステスト."""

    def test_parse_max_code_length(self) -> None:
        """10文字のコードをパースできる."""
        result = parse_symbol("XJPX:ABCDEFGHIJ")
        assert isinstance(result, EquitySymbol)
        assert result.code == "ABCDEFGHIJ"

    def test_parse_single_char_code(self) -> None:
        """1文字のコードをパースできる."""
        result = parse_symbol("XJPX:A")
        assert isinstance(result, EquitySymbol)
        assert result.code == "A"

    def test_str_roundtrip_equity(self) -> None:
        """EquitySymbol の str() → parse_symbol() が等価."""
        original = EquitySymbol(exchange="XJPX", code="7203")
        parsed = parse_symbol(str(original))
        assert parsed == original

    def test_str_roundtrip_future(self) -> None:
        """FutureSymbol の str() → parse_symbol() が等価."""
        original = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        parsed = parse_symbol(str(original))
        assert parsed == original

    def test_str_roundtrip_option_call(self) -> None:
        """OptionSymbol (CALL) の str() → parse_symbol() が等価."""
        original = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        parsed = parse_symbol(str(original))
        assert parsed == original

    def test_str_roundtrip_option_series(self) -> None:
        """OptionSymbol (SERIES) の str() → parse_symbol() が等価."""
        original = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.SERIES,
            strike=None,
        )
        parsed = parse_symbol(str(original))
        assert parsed == original

    def test_str_roundtrip_option_put(self) -> None:
        """OptionSymbol (PUT) の str() → parse_symbol() が等価."""
        original = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.PUT,
            strike=38000,
        )
        parsed = parse_symbol(str(original))
        assert parsed == original

    def test_parse_symbol_too_long(self) -> None:
        """シンボルが MAX_SYMBOL_LENGTH を超えると E010 エラーを発生する."""
        long_symbol = "XJPX:" + "A" * 100
        with pytest.raises(SymbolParseError) as exc_info:
            parse_symbol(long_symbol)
        assert exc_info.value.error_code == ErrorCode.SYMBOL_TOO_LONG

    def test_parse_symbol_at_max_length(self) -> None:
        """MAX_SYMBOL_LENGTH ちょうどのシンボルはパースできる."""
        # MAX_SYMBOL_LENGTH = 100
        # "XJPX:" (5文字) + 95文字 = 100文字
        long_code = "A" * 10  # 最大コード長は10文字
        symbol = f"XJPX:{long_code}"
        result = parse_symbol(symbol)
        assert isinstance(result, EquitySymbol)
        assert result.code == long_code
