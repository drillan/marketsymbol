"""marketsymbol の例外クラス定義.

エラーコード列挙型とシンボル関連の例外クラスを提供する。
"""

from enum import Enum
from typing import Self


class ErrorCode(Enum):
    """エラーコード列挙型.

    シンボルのパース・バリデーションエラーを識別する。
    各メンバーの値は 'E' + 3桁の番号形式。
    """

    FUTURE_WITH_STRIKE = "E001"
    """先物に権利行使価格を指定."""

    OPTION_WITHOUT_STRIKE = "E002"
    """オプション (C/P) に権利行使価格なし."""

    INVALID_EXPIRY_FORMAT = "E003"
    """無効な限月形式."""

    INVALID_SEGMENT_COUNT = "E004"
    """無効なセグメント数."""

    INVALID_DATE = "E005"
    """無効な日付."""

    INVALID_OPTION_TYPE = "E006"
    """無効なオプション種別."""

    UNKNOWN_EXCHANGE = "E007"
    """不明な取引所コード."""

    INVALID_CODE = "E008"
    """無効な証券/商品コード."""

    INVALID_STRIKE_VALUE = "E009"
    """無効な権利行使価格."""

    SYMBOL_TOO_LONG = "E010"
    """シンボル文字列が長すぎる."""


class SymbolError(Exception):
    """シンボル関連例外の基底クラス.

    Attributes:
        message: エラーメッセージ (str).
        error_code: エラーコード (ErrorCode 列挙型).
    """

    def __init__(self, message: str, error_code: ErrorCode) -> None:
        """SymbolError を初期化する.

        Args:
            message: エラーメッセージ.
            error_code: エラーコード.
        """
        super().__init__(message)
        self._message = message
        self._error_code = error_code

    @property
    def message(self) -> str:
        """エラーメッセージを返す."""
        return self._message

    @property
    def error_code(self) -> ErrorCode:
        """エラーコードを返す."""
        return self._error_code

    def __str__(self) -> str:
        """エラーコードとメッセージを含む文字列を返す."""
        return f"[{self._error_code.value}] {self._message}"


class SymbolParseError(SymbolError):
    """シンボルパース失敗時の例外.

    Attributes:
        message: エラーメッセージ (str).
        error_code: エラーコード (ErrorCode 列挙型).
        raw_symbol: パースに失敗した元のシンボル文字列 (str | None).
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        *,
        raw_symbol: str | None = None,
    ) -> None:
        """SymbolParseError を初期化する.

        Args:
            message: エラーメッセージ.
            error_code: エラーコード.
            raw_symbol: パースに失敗した元のシンボル文字列.
        """
        super().__init__(message, error_code)
        self._raw_symbol = raw_symbol

    @property
    def raw_symbol(self) -> str | None:
        """パースに失敗した元のシンボル文字列を返す."""
        return self._raw_symbol

    @classmethod
    def from_parse_failure(
        cls,
        message: str,
        error_code: ErrorCode,
        raw_symbol: str,
    ) -> Self:
        """パース失敗時のファクトリメソッド.

        raw_symbol を必須パラメータとして受け取る。
        デバッグ時に失敗したシンボルを特定できるようにするため、
        パース処理からは __init__ よりもこのメソッドの使用を推奨。

        Args:
            message: エラーメッセージ.
            error_code: エラーコード.
            raw_symbol: パースに失敗した元のシンボル文字列 (必須).

        Returns:
            SymbolParseError インスタンス.
        """
        return cls(message, error_code, raw_symbol=raw_symbol)


class SymbolValidationError(SymbolError):
    """シンボルバリデーション失敗時の例外.

    Attributes:
        message: エラーメッセージ (str).
        error_code: エラーコード (ErrorCode 列挙型).
        field_name: バリデーションに失敗したフィールド名 (str | None).
        field_value: バリデーションに失敗した値 (object).
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        *,
        field_name: str | None = None,
        field_value: object = None,
    ) -> None:
        """SymbolValidationError を初期化する.

        Args:
            message: エラーメッセージ.
            error_code: エラーコード.
            field_name: バリデーションに失敗したフィールド名.
            field_value: バリデーションに失敗した値.
        """
        super().__init__(message, error_code)
        self._field_name = field_name
        self._field_value = field_value

    @property
    def field_name(self) -> str | None:
        """バリデーションに失敗したフィールド名を返す."""
        return self._field_name

    @property
    def field_value(self) -> object:
        """バリデーションに失敗した値を返す."""
        return self._field_value
