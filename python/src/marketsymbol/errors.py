"""marketsymbol の例外クラス定義.

エラーコード列挙型とシンボル関連の例外クラスを提供する。
"""

from enum import Enum


class ErrorCode(Enum):
    """エラーコード (E001-E007).

    シンボルのパース・バリデーションエラーを識別する。
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


class SymbolError(Exception):
    """シンボル関連例外の基底クラス.

    Attributes:
        message: エラーメッセージ.
        error_code: エラーコード.
    """

    def __init__(self, message: str, error_code: ErrorCode) -> None:
        """SymbolError を初期化する.

        Args:
            message: エラーメッセージ.
            error_code: エラーコード.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        """エラーコードとメッセージを含む文字列を返す."""
        return f"[{self.error_code.value}] {self.message}"


class SymbolParseError(SymbolError):
    """シンボルパース失敗時の例外.

    Attributes:
        message: エラーメッセージ.
        error_code: エラーコード.
        raw_symbol: パースに失敗した元のシンボル文字列.
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
        self.raw_symbol = raw_symbol


class SymbolValidationError(SymbolError):
    """シンボルバリデーション失敗時の例外.

    Attributes:
        message: エラーメッセージ.
        error_code: エラーコード.
        field_name: バリデーションに失敗したフィールド名.
        field_value: バリデーションに失敗した値.
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
        self.field_name = field_name
        self.field_value = field_value
