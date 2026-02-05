"""validator モジュールのテスト.

各フィールドのバリデーション関数をテストする。
"""

import pytest

from marketsymbol.errors import ErrorCode, SymbolValidationError
from marketsymbol.validator import (
    validate_code,
    validate_exchange,
    validate_expiry,
    validate_option_type,
    validate_strike,
)


class TestValidateExchange:
    """validate_exchange() のテスト."""

    def test_valid_exchange_xjpx(self) -> None:
        """有効な MIC コード XJPX はパスする."""
        validate_exchange("XJPX")  # 例外が発生しないことを確認

    def test_valid_exchange_xnas(self) -> None:
        """有効な MIC コード XNAS はパスする."""
        validate_exchange("XNAS")

    def test_valid_exchange_xnys(self) -> None:
        """有効な MIC コード XNYS はパスする."""
        validate_exchange("XNYS")

    def test_invalid_exchange_too_short(self) -> None:
        """3文字の exchange は E007 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_exchange("XJP")
        assert exc_info.value.error_code == ErrorCode.UNKNOWN_EXCHANGE
        assert exc_info.value.field_name == "exchange"
        assert exc_info.value.field_value == "XJP"

    def test_invalid_exchange_too_long(self) -> None:
        """5文字の exchange は E007 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_exchange("XJPXX")
        assert exc_info.value.error_code == ErrorCode.UNKNOWN_EXCHANGE

    def test_invalid_exchange_lowercase(self) -> None:
        """小文字の exchange は E007 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_exchange("xjpx")
        assert exc_info.value.error_code == ErrorCode.UNKNOWN_EXCHANGE

    def test_invalid_exchange_with_digit(self) -> None:
        """数字を含む exchange は E007 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_exchange("XJP1")
        assert exc_info.value.error_code == ErrorCode.UNKNOWN_EXCHANGE

    def test_invalid_exchange_empty(self) -> None:
        """空の exchange は E007 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_exchange("")
        assert exc_info.value.error_code == ErrorCode.UNKNOWN_EXCHANGE


class TestValidateCode:
    """validate_code() のテスト."""

    def test_valid_code_numeric(self) -> None:
        """数字のみのコードはパスする (証券コード)."""
        validate_code("7203")

    def test_valid_code_alphanumeric(self) -> None:
        """英数字のコードはパスする."""
        validate_code("NK225")

    def test_valid_code_alpha(self) -> None:
        """英字のみのコードはパスする."""
        validate_code("NK")

    def test_valid_code_single_char(self) -> None:
        """1文字のコードはパスする."""
        validate_code("A")

    def test_valid_code_10_chars(self) -> None:
        """10文字のコードはパスする (最大長)."""
        validate_code("ABCDEFGHIJ")

    def test_invalid_code_empty(self) -> None:
        """空のコードは E008 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_code("")
        assert exc_info.value.error_code == ErrorCode.INVALID_CODE
        assert exc_info.value.field_name == "code"

    def test_invalid_code_too_long(self) -> None:
        """11文字のコードは E008 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_code("ABCDEFGHIJK")
        assert exc_info.value.error_code == ErrorCode.INVALID_CODE

    def test_invalid_code_lowercase(self) -> None:
        """小文字のコードは E008 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_code("nk")
        assert exc_info.value.error_code == ErrorCode.INVALID_CODE

    def test_invalid_code_with_special_char(self) -> None:
        """特殊文字を含むコードは E008 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_code("NK-225")
        assert exc_info.value.error_code == ErrorCode.INVALID_CODE


class TestValidateExpiry:
    """validate_expiry() のテスト."""

    def test_valid_expiry(self) -> None:
        """有効な限月 YYYYMMDD はパスする."""
        validate_expiry("20250314")

    def test_valid_expiry_leap_year(self) -> None:
        """うるう年の 2/29 はパスする."""
        validate_expiry("20240229")

    def test_valid_expiry_end_of_month(self) -> None:
        """月末日はパスする."""
        validate_expiry("20250131")

    def test_invalid_expiry_too_short(self) -> None:
        """7桁の expiry は E003 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_expiry("2025031")
        assert exc_info.value.error_code == ErrorCode.INVALID_EXPIRY_FORMAT
        assert exc_info.value.field_name == "expiry"

    def test_invalid_expiry_too_long(self) -> None:
        """9桁の expiry は E003 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_expiry("202503141")
        assert exc_info.value.error_code == ErrorCode.INVALID_EXPIRY_FORMAT

    def test_invalid_expiry_non_numeric(self) -> None:
        """数字以外を含む expiry は E003 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_expiry("2025031A")
        assert exc_info.value.error_code == ErrorCode.INVALID_EXPIRY_FORMAT

    def test_invalid_expiry_invalid_month(self) -> None:
        """無効な月 (13月) は E005 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_expiry("20251314")
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE

    def test_invalid_expiry_invalid_day(self) -> None:
        """無効な日 (2月30日) は E005 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_expiry("20250230")
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE

    def test_invalid_expiry_non_leap_year_feb29(self) -> None:
        """非うるう年の 2/29 は E005 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_expiry("20250229")
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE

    def test_invalid_expiry_month_00(self) -> None:
        """月が 00 は E005 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_expiry("20250014")
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE

    def test_invalid_expiry_day_00(self) -> None:
        """日が 00 は E005 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_expiry("20250300")
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE


class TestValidateOptionType:
    """validate_option_type() のテスト."""

    def test_valid_option_type_call(self) -> None:
        """C (CALL) はパスする."""
        validate_option_type("C")

    def test_valid_option_type_put(self) -> None:
        """P (PUT) はパスする."""
        validate_option_type("P")

    def test_valid_option_type_series(self) -> None:
        """O (SERIES) はパスする."""
        validate_option_type("O")

    def test_valid_option_type_future(self) -> None:
        """F (FUTURE) はパスする."""
        validate_option_type("F")

    def test_invalid_option_type_lowercase(self) -> None:
        """小文字は E006 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_option_type("c")
        assert exc_info.value.error_code == ErrorCode.INVALID_OPTION_TYPE
        assert exc_info.value.field_name == "option_type"

    def test_invalid_option_type_unknown(self) -> None:
        """未知の文字は E006 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_option_type("X")
        assert exc_info.value.error_code == ErrorCode.INVALID_OPTION_TYPE

    def test_invalid_option_type_empty(self) -> None:
        """空の文字列は E006 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_option_type("")
        assert exc_info.value.error_code == ErrorCode.INVALID_OPTION_TYPE


class TestValidateStrike:
    """validate_strike() のテスト."""

    def test_valid_strike_positive(self) -> None:
        """正の整数はパスする."""
        validate_strike(40000)

    def test_valid_strike_minimum(self) -> None:
        """最小値 1 はパスする."""
        validate_strike(1)

    def test_valid_strike_large(self) -> None:
        """大きな値もパスする."""
        validate_strike(1000000)

    def test_invalid_strike_zero(self) -> None:
        """0 は E009 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_strike(0)
        assert exc_info.value.error_code == ErrorCode.INVALID_STRIKE_VALUE
        assert exc_info.value.field_name == "strike"

    def test_invalid_strike_negative(self) -> None:
        """負の値は E009 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            validate_strike(-100)
        assert exc_info.value.error_code == ErrorCode.INVALID_STRIKE_VALUE
