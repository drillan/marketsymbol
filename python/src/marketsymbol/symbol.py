"""marketsymbol の Symbol クラス定義.

EquitySymbol, FutureSymbol, OptionSymbol の dataclass と
Symbol 型エイリアスを提供する。
"""

from dataclasses import dataclass

from marketsymbol.enums import AssetClass, OptionType


@dataclass(frozen=True, slots=True)
class EquitySymbol:
    """株式・ETF シンボル.

    Attributes:
        exchange: ISO 10383 MIC コード (4文字英大文字).
        code: 証券コード (1-10文字英数字).
    """

    exchange: str
    code: str

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
        code: 商品コード (2-6文字英数字).
        expiry: 限月 (YYYYMMDD 形式).
    """

    exchange: str
    code: str
    expiry: str

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
        code: 商品コード (2-10文字英数字).
        expiry: 限月 (YYYYMMDD 形式).
        option_type: オプション種別 (CALL/PUT/SERIES).
        strike: 権利行使価格 (CALL/PUT は正の整数必須、SERIES は None).
    """

    exchange: str
    code: str
    expiry: str
    option_type: OptionType
    strike: int | None

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
