"""ErrorCode, SymbolError, SymbolParseError, SymbolValidationError のテスト."""

import pytest

from marketsymbol.errors import (
    ErrorCode,
    SymbolError,
    SymbolParseError,
    SymbolValidationError,
)


class TestErrorCode:
    """ErrorCode 列挙型のテスト."""

    def test_future_with_strike(self) -> None:
        """E001: 先物に権利行使価格を指定."""
        assert ErrorCode.FUTURE_WITH_STRIKE.value == "E001"

    def test_option_without_strike(self) -> None:
        """E002: オプション (C/P) に権利行使価格なし."""
        assert ErrorCode.OPTION_WITHOUT_STRIKE.value == "E002"

    def test_invalid_expiry_format(self) -> None:
        """E003: 無効な限月形式."""
        assert ErrorCode.INVALID_EXPIRY_FORMAT.value == "E003"

    def test_invalid_segment_count(self) -> None:
        """E004: 無効なセグメント数."""
        assert ErrorCode.INVALID_SEGMENT_COUNT.value == "E004"

    def test_invalid_date(self) -> None:
        """E005: 無効な日付."""
        assert ErrorCode.INVALID_DATE.value == "E005"

    def test_invalid_option_type(self) -> None:
        """E006: 無効なオプション種別."""
        assert ErrorCode.INVALID_OPTION_TYPE.value == "E006"

    def test_unknown_exchange(self) -> None:
        """E007: 不明な取引所コード."""
        assert ErrorCode.UNKNOWN_EXCHANGE.value == "E007"

    def test_member_count(self) -> None:
        """ErrorCode は 7 つのメンバーを持つ (E001-E007)."""
        assert len(ErrorCode) == 7


class TestSymbolError:
    """SymbolError 基底例外のテスト."""

    def test_message_and_error_code(self) -> None:
        """message と error_code 属性が設定される."""
        error = SymbolError("Test message", ErrorCode.UNKNOWN_EXCHANGE)
        assert error.message == "Test message"
        assert error.error_code == ErrorCode.UNKNOWN_EXCHANGE

    def test_str_format(self) -> None:
        """str() で '[エラーコード] メッセージ' 形式になる."""
        error = SymbolError("Test message", ErrorCode.UNKNOWN_EXCHANGE)
        assert str(error) == "[E007] Test message"

    def test_is_exception(self) -> None:
        """SymbolError は Exception を継承している."""
        error = SymbolError("Test", ErrorCode.INVALID_DATE)
        assert isinstance(error, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        """raise して except で捕捉できる."""
        with pytest.raises(SymbolError) as exc_info:
            raise SymbolError("Test error", ErrorCode.INVALID_DATE)
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE


class TestSymbolParseError:
    """SymbolParseError のテスト."""

    def test_inherits_symbol_error(self) -> None:
        """SymbolError を継承している."""
        error = SymbolParseError("Parse failed", ErrorCode.INVALID_SEGMENT_COUNT)
        assert isinstance(error, SymbolError)

    def test_raw_symbol_attribute(self) -> None:
        """raw_symbol 属性が設定される."""
        error = SymbolParseError(
            "Parse failed",
            ErrorCode.INVALID_SEGMENT_COUNT,
            raw_symbol="INVALID:SYMBOL",
        )
        assert error.raw_symbol == "INVALID:SYMBOL"

    def test_raw_symbol_default_none(self) -> None:
        """raw_symbol のデフォルトは None."""
        error = SymbolParseError("Parse failed", ErrorCode.INVALID_SEGMENT_COUNT)
        assert error.raw_symbol is None

    def test_str_format(self) -> None:
        """str() で '[エラーコード] メッセージ' 形式になる."""
        error = SymbolParseError("Parse failed", ErrorCode.INVALID_SEGMENT_COUNT)
        assert str(error) == "[E004] Parse failed"

    def test_error_code_attribute(self) -> None:
        """error_code 属性を持つ (受入条件)."""
        error = SymbolParseError("Parse failed", ErrorCode.INVALID_SEGMENT_COUNT)
        assert error.error_code == ErrorCode.INVALID_SEGMENT_COUNT

    def test_exception_chaining(self) -> None:
        """例外チェーン (__cause__) が正しく設定される."""
        original = ValueError("original error")
        try:
            raise SymbolParseError(
                "Parse failed", ErrorCode.INVALID_SEGMENT_COUNT
            ) from original
        except SymbolParseError as e:
            assert e.__cause__ is original

    def test_from_parse_failure_factory(self) -> None:
        """from_parse_failure ファクトリメソッドで raw_symbol が必須になる."""
        error = SymbolParseError.from_parse_failure(
            "Parse failed",
            ErrorCode.INVALID_SEGMENT_COUNT,
            "INVALID:SYMBOL",
        )
        assert error.message == "Parse failed"
        assert error.error_code == ErrorCode.INVALID_SEGMENT_COUNT
        assert error.raw_symbol == "INVALID:SYMBOL"


class TestSymbolValidationError:
    """SymbolValidationError のテスト."""

    def test_inherits_symbol_error(self) -> None:
        """SymbolError を継承している."""
        error = SymbolValidationError("Validation failed", ErrorCode.INVALID_DATE)
        assert isinstance(error, SymbolError)

    def test_field_name_attribute(self) -> None:
        """field_name 属性が設定される."""
        error = SymbolValidationError(
            "Validation failed",
            ErrorCode.INVALID_DATE,
            field_name="expiry",
        )
        assert error.field_name == "expiry"

    def test_field_value_attribute(self) -> None:
        """field_value 属性が設定される."""
        error = SymbolValidationError(
            "Validation failed",
            ErrorCode.INVALID_DATE,
            field_name="expiry",
            field_value="20250332",
        )
        assert error.field_value == "20250332"

    def test_field_attributes_default_none(self) -> None:
        """field_name, field_value のデフォルトは None."""
        error = SymbolValidationError("Validation failed", ErrorCode.INVALID_DATE)
        assert error.field_name is None
        assert error.field_value is None

    def test_str_format(self) -> None:
        """str() で '[エラーコード] メッセージ' 形式になる."""
        error = SymbolValidationError("Validation failed", ErrorCode.INVALID_DATE)
        assert str(error) == "[E005] Validation failed"

    def test_error_code_attribute(self) -> None:
        """error_code 属性を持つ (受入条件)."""
        error = SymbolValidationError("Validation failed", ErrorCode.INVALID_DATE)
        assert error.error_code == ErrorCode.INVALID_DATE
