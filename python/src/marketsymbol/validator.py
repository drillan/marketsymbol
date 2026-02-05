"""marketsymbol のバリデーション機能.

各フィールドのバリデーション関数を提供する。
"""

import calendar
import re

from marketsymbol.constants import (
    EXPIRY_LENGTH,
    MAX_CODE_LENGTH,
    MIN_CODE_LENGTH,
    MIN_STRIKE,
)
from marketsymbol.errors import ErrorCode, SymbolValidationError

# 有効なオプション/アセットタイプ識別子
VALID_TYPE_IDENTIFIERS = frozenset({"C", "P", "O", "F"})

# 正規表現パターン
_MIC_PATTERN = re.compile(r"^[A-Z]{4}$")
_CODE_PATTERN = re.compile(r"^[A-Z0-9]+$")
_EXPIRY_PATTERN = re.compile(r"^\d{8}$")


def validate_exchange(exchange: str) -> None:
    """取引所コード (MIC) をバリデーションする.

    Args:
        exchange: 取引所コード.

    Raises:
        SymbolValidationError: バリデーション失敗時 (E007).
    """
    if not _MIC_PATTERN.match(exchange):
        raise SymbolValidationError(
            f"Invalid exchange code: '{exchange}' (must be 4 uppercase letters)",
            ErrorCode.UNKNOWN_EXCHANGE,
            field_name="exchange",
            field_value=exchange,
        )


def validate_code(code: str) -> None:
    """証券/商品コードをバリデーションする.

    Args:
        code: 証券/商品コード.

    Raises:
        SymbolValidationError: バリデーション失敗時 (E004).
    """
    if not code or len(code) < MIN_CODE_LENGTH or len(code) > MAX_CODE_LENGTH:
        raise SymbolValidationError(
            f"Invalid code: '{code}' (must be {MIN_CODE_LENGTH}-{MAX_CODE_LENGTH} characters)",
            ErrorCode.INVALID_SEGMENT_COUNT,
            field_name="code",
            field_value=code,
        )
    if not _CODE_PATTERN.match(code):
        raise SymbolValidationError(
            f"Invalid code: '{code}' (must be uppercase alphanumeric)",
            ErrorCode.INVALID_SEGMENT_COUNT,
            field_name="code",
            field_value=code,
        )


def validate_expiry(expiry: str) -> None:
    """限月 (YYYYMMDD) をバリデーションする.

    Args:
        expiry: 限月 (YYYYMMDD 形式).

    Raises:
        SymbolValidationError: フォーマット不正時 (E003)、日付不正時 (E005).
    """
    if not _EXPIRY_PATTERN.match(expiry) or len(expiry) != EXPIRY_LENGTH:
        raise SymbolValidationError(
            f"Invalid expiry format: '{expiry}' (must be YYYYMMDD)",
            ErrorCode.INVALID_EXPIRY_FORMAT,
            field_name="expiry",
            field_value=expiry,
        )

    year = int(expiry[:4])
    month = int(expiry[4:6])
    day = int(expiry[6:8])

    if month < 1 or month > 12:
        raise SymbolValidationError(
            f"Invalid date: '{expiry}' (invalid month: {month})",
            ErrorCode.INVALID_DATE,
            field_name="expiry",
            field_value=expiry,
        )

    # 月の最大日数を取得 (うるう年考慮)
    _, max_day = calendar.monthrange(year, month)
    if day < 1 or day > max_day:
        raise SymbolValidationError(
            f"Invalid date: '{expiry}' (invalid day: {day} for month {month})",
            ErrorCode.INVALID_DATE,
            field_name="expiry",
            field_value=expiry,
        )


def validate_option_type(option_type: str) -> None:
    """オプション/資産タイプ識別子をバリデーションする.

    Args:
        option_type: タイプ識別子 (C/P/O/F).

    Raises:
        SymbolValidationError: バリデーション失敗時 (E006).
    """
    if option_type not in VALID_TYPE_IDENTIFIERS:
        raise SymbolValidationError(
            f"Invalid option type: '{option_type}' (must be C, P, O, or F)",
            ErrorCode.INVALID_OPTION_TYPE,
            field_name="option_type",
            field_value=option_type,
        )


def validate_strike(strike: int) -> None:
    """権利行使価格をバリデーションする.

    Args:
        strike: 権利行使価格.

    Raises:
        SymbolValidationError: バリデーション失敗時 (E002).
    """
    if strike < MIN_STRIKE:
        raise SymbolValidationError(
            f"Invalid strike: {strike} (must be positive integer >= {MIN_STRIKE})",
            ErrorCode.OPTION_WITHOUT_STRIKE,
            field_name="strike",
            field_value=strike,
        )
