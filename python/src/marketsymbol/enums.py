"""marketsymbol の列挙型定義.

資産クラスとオプション種別の列挙型を提供する。
"""

from enum import Enum


class AssetClass(Enum):
    """資産クラス.

    シンボルが表す金融商品の種類を識別する。
    """

    EQUITY = "equity"
    """株式・ETF."""

    FUTURE = "future"
    """先物."""

    OPTION = "option"
    """オプション."""


class OptionType(Enum):
    """オプション種別.

    オプションのコール/プット/シリーズを識別する。
    """

    CALL = "C"
    """コールオプション."""

    PUT = "P"
    """プットオプション."""

    SERIES = "O"
    """シリーズ識別用: 特定の権利行使価格を持たないオプション銘柄群を表す."""
