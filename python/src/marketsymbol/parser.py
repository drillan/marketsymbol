"""marketsymbol のパーサー機能.

シンボル文字列の正規化とパースを提供する。
"""

import unicodedata

from marketsymbol.enums import OptionType
from marketsymbol.errors import ErrorCode, SymbolParseError, SymbolValidationError
from marketsymbol.symbol import EquitySymbol, FutureSymbol, OptionSymbol, Symbol
from marketsymbol.validator import (
    validate_code,
    validate_exchange,
    validate_expiry,
    validate_option_type,
    validate_strike,
)

# セグメント数の定数
_EQUITY_SEGMENT_COUNT = 2
_FUTURE_SEGMENT_COUNT = 4
_OPTION_SEGMENT_COUNT = 5
_SERIES_SEGMENT_COUNT = 4


def normalize_symbol(raw: str) -> str:
    """シンボル文字列を正規化する.

    以下の正規化を順に適用する:
    1. NFKC 正規化 (全角->半角変換)
    2. 大文字変換
    3. 前後空白除去

    Args:
        raw: 正規化前のシンボル文字列.

    Returns:
        正規化後のシンボル文字列.
    """
    # NFKC 正規化: 全角→半角、合字の分解など
    normalized = unicodedata.normalize("NFKC", raw)
    # 大文字変換
    normalized = normalized.upper()
    # 前後空白除去
    normalized = normalized.strip()
    return normalized


def parse_symbol(raw: str) -> Symbol:
    """シンボル文字列をパースして Symbol オブジェクトを返す.

    パース処理:
    1. 型チェック (str 以外は TypeError)
    2. 正規化 (normalize_symbol)
    3. セグメント分割 (':')
    4. セグメント数に応じてバリデーション・Symbol 生成

    セグメント数による分岐:
    - 2: EquitySymbol (exchange:code)
    - 4: FutureSymbol または OptionSymbol(SERIES) (exchange:code:expiry:type)
    - 5: OptionSymbol (exchange:code:expiry:type:strike)

    Args:
        raw: シンボル文字列.

    Returns:
        パース結果の Symbol オブジェクト.

    Raises:
        TypeError: raw が str でない場合.
        SymbolParseError: パース失敗時.
    """
    if not isinstance(raw, str):
        raise TypeError(f"Expected str, got {type(raw).__name__}")

    normalized = normalize_symbol(raw)

    if not normalized:
        raise SymbolParseError.from_parse_failure(
            "Empty symbol string",
            ErrorCode.INVALID_SEGMENT_COUNT,
            raw,
        )

    segments = normalized.split(":")
    segment_count = len(segments)

    try:
        if segment_count == _EQUITY_SEGMENT_COUNT:
            return _parse_equity(segments, raw)
        elif segment_count == _FUTURE_SEGMENT_COUNT:
            return _parse_future_or_series(segments, raw)
        elif segment_count == _OPTION_SEGMENT_COUNT:
            return _parse_option(segments, raw)
        else:
            raise SymbolParseError.from_parse_failure(
                f"Invalid segment count: {segment_count} (expected 2, 4, or 5)",
                ErrorCode.INVALID_SEGMENT_COUNT,
                raw,
            )
    except SymbolValidationError as e:
        raise SymbolParseError.from_parse_failure(
            e.message,
            e.error_code,
            raw,
        ) from e


def _parse_equity(segments: list[str], raw: str) -> EquitySymbol:  # noqa: ARG001
    """2セグメントを EquitySymbol としてパースする."""
    exchange, code = segments

    validate_exchange(exchange)
    validate_code(code)

    return EquitySymbol(exchange=exchange, code=code)


def _parse_future_or_series(
    segments: list[str], raw: str
) -> FutureSymbol | OptionSymbol:
    """4セグメントを FutureSymbol または OptionSymbol(SERIES) としてパースする."""
    exchange, code, expiry, type_indicator = segments

    validate_exchange(exchange)
    validate_code(code)
    validate_expiry(expiry)
    validate_option_type(type_indicator)

    if type_indicator == "F":
        return FutureSymbol(exchange=exchange, code=code, expiry=expiry)
    elif type_indicator == "O":
        return OptionSymbol(
            exchange=exchange,
            code=code,
            expiry=expiry,
            option_type=OptionType.SERIES,
            strike=None,
        )
    else:
        # C または P だが strike がない
        raise SymbolParseError.from_parse_failure(
            f"Option type '{type_indicator}' requires strike price",
            ErrorCode.OPTION_WITHOUT_STRIKE,
            raw,
        )


def _parse_option(segments: list[str], raw: str) -> OptionSymbol | FutureSymbol:
    """5セグメントを OptionSymbol としてパースする."""
    exchange, code, expiry, type_indicator, strike_str = segments

    validate_exchange(exchange)
    validate_code(code)
    validate_expiry(expiry)
    validate_option_type(type_indicator)

    # strike を整数に変換
    try:
        strike = int(strike_str)
    except ValueError:
        raise SymbolParseError.from_parse_failure(
            f"Invalid strike: '{strike_str}' (must be a positive integer)",
            ErrorCode.INVALID_SEGMENT_COUNT,
            raw,
        ) from None

    # F または O に strike が指定された場合はエラー
    if type_indicator in ("F", "O"):
        raise SymbolParseError.from_parse_failure(
            f"Type '{type_indicator}' must not have strike price",
            ErrorCode.FUTURE_WITH_STRIKE,
            raw,
        )

    validate_strike(strike)

    option_type = OptionType.CALL if type_indicator == "C" else OptionType.PUT

    return OptionSymbol(
        exchange=exchange,
        code=code,
        expiry=expiry,
        option_type=option_type,
        strike=strike,
    )
