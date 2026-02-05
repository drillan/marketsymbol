"""marketsymbol の Symbol クラス定義.

EquitySymbol, FutureSymbol, OptionSymbol の dataclass と
Symbol 型エイリアスを提供する。
"""

from dataclasses import dataclass

from marketsymbol.enums import AssetClass, OptionType
from marketsymbol.errors import ErrorCode, SymbolValidationError
from marketsymbol.validator import (
    validate_code,
    validate_exchange,
    validate_expiry,
    validate_strike,
)


@dataclass(frozen=True, slots=True)
class EquitySymbol:
    """株式・ETF シンボル.

    Attributes:
        exchange: ISO 10383 MIC コード (4文字英大文字).
        code: 証券コード (1-10文字英数字).
    """

    exchange: str
    code: str

    def __post_init__(self) -> None:
        """コンストラクタ後のバリデーション."""
        validate_exchange(self.exchange)
        validate_code(self.code)

    @property
    def asset_class(self) -> AssetClass:
        """資産クラスを返す."""
        return AssetClass.EQUITY

    def __str__(self) -> str:
        """'exchange:code' 形式の文字列を返す."""
        return f"{self.exchange}:{self.code}"


@dataclass(frozen=True, slots=True)
class FutureSymbol:
    """先物シンボル.

    Attributes:
        exchange: ISO 10383 MIC コード (4文字英大文字).
        code: 商品コード (1-10文字英数字).
        expiry: 限月 (YYYYMMDD 形式).
    """

    exchange: str
    code: str
    expiry: str

    def __post_init__(self) -> None:
        """コンストラクタ後のバリデーション."""
        validate_exchange(self.exchange)
        validate_code(self.code)
        validate_expiry(self.expiry)

    @property
    def asset_class(self) -> AssetClass:
        """資産クラスを返す."""
        return AssetClass.FUTURE

    def __str__(self) -> str:
        """'exchange:code:expiry:F' 形式の文字列を返す."""
        return f"{self.exchange}:{self.code}:{self.expiry}:F"


@dataclass(frozen=True, slots=True)
class OptionSymbol:
    """オプションシンボル.

    Attributes:
        exchange: ISO 10383 MIC コード (4文字英大文字).
        code: 商品コード (1-10文字英数字).
        expiry: 限月 (YYYYMMDD 形式).
        option_type: オプション種別 (CALL/PUT/SERIES).
        strike: 権利行使価格 (CALL/PUT は正の整数必須、SERIES は None).
    """

    exchange: str
    code: str
    expiry: str
    option_type: OptionType
    strike: int | None

    def __post_init__(self) -> None:
        """コンストラクタ後のバリデーション."""
        validate_exchange(self.exchange)
        validate_code(self.code)
        validate_expiry(self.expiry)

        # option_type と strike の依存関係を検証
        if self.option_type in (OptionType.CALL, OptionType.PUT):
            if self.strike is None:
                raise SymbolValidationError(
                    f"Option type '{self.option_type.value}' requires strike price",
                    ErrorCode.OPTION_WITHOUT_STRIKE,
                    field_name="strike",
                    field_value=self.strike,
                )
            validate_strike(self.strike)
        elif self.option_type == OptionType.SERIES:
            if self.strike is not None:
                raise SymbolValidationError(
                    "Option type 'SERIES' must not have strike price",
                    ErrorCode.FUTURE_WITH_STRIKE,
                    field_name="strike",
                    field_value=self.strike,
                )

    @property
    def asset_class(self) -> AssetClass:
        """資産クラスを返す."""
        return AssetClass.OPTION

    def __str__(self) -> str:
        """シンボル文字列を返す.

        CALL/PUT: 'exchange:code:expiry:C/P:strike' 形式
        SERIES:   'exchange:code:expiry:O' 形式
        """
        if self.option_type == OptionType.SERIES:
            return f"{self.exchange}:{self.code}:{self.expiry}:O"
        return f"{self.exchange}:{self.code}:{self.expiry}:{self.option_type.value}:{self.strike}"


# Symbol 型エイリアス (Union 型)
Symbol = EquitySymbol | FutureSymbol | OptionSymbol
