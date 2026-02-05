"""marketsymbol - 統一シンボル表記のためのライブラリ.

このパッケージは金融商品シンボルのパース、バリデーション、
正規化機能を提供する。

Example:
    >>> from marketsymbol import parse_symbol
    >>> s = parse_symbol("XJPX:7203")
    >>> s.exchange
    'XJPX'
    >>> s.code
    '7203'

    >>> from marketsymbol import normalize_symbol
    >>> normalize_symbol("xjpx:7203")  # noqa: RUF002
    'XJPX:7203'
"""

from marketsymbol.adapter import AdapterRegistry, BaseAdapter
from marketsymbol.enums import AssetClass, OptionType
from marketsymbol.errors import (
    ErrorCode,
    SymbolError,
    SymbolParseError,
    SymbolValidationError,
)
from marketsymbol.parser import normalize_symbol, parse_symbol
from marketsymbol.symbol import (
    EquitySymbol,
    FutureSymbol,
    OptionSymbol,
    Symbol,
)

__all__ = [
    "AdapterRegistry",
    "AssetClass",
    "BaseAdapter",
    "EquitySymbol",
    "ErrorCode",
    "FutureSymbol",
    "OptionSymbol",
    "OptionType",
    "Symbol",
    "SymbolError",
    "SymbolParseError",
    "SymbolValidationError",
    "normalize_symbol",
    "parse_symbol",
]
