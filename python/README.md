# marketsymbol

金融商品シンボルの統一表記と変換を提供する Python ライブラリ。

## Features

- シンボル文字列のパース・正規化・バリデーション
- 株式、先物、オプションの各資産クラスをサポート
- ベンダー固有フォーマットとの相互変換（アダプター機構）
- 型安全な API（`mypy --strict` 対応）
- Python 3.13+ 対応

## Installation

```bash
pip install marketsymbol
```

## Quick Start

### シンボルのパース

```python
from marketsymbol import parse_symbol

# 株式シンボル
stock = parse_symbol("XJPX:7203")
print(stock.exchange)     # "XJPX"
print(stock.code)         # "7203"
print(stock.asset_class)  # AssetClass.EQUITY
print(str(stock))         # "XJPX:7203"

# 先物シンボル
future = parse_symbol("XJPX:NK:20250314:F")
print(future.exchange)    # "XJPX"
print(future.code)        # "NK"
print(future.expiry)      # "20250314"
print(future.asset_class) # AssetClass.FUTURE

# オプションシンボル
option = parse_symbol("XJPX:N225O:20250314:C:42000")
print(option.exchange)     # "XJPX"
print(option.code)         # "N225O"
print(option.expiry)       # "20250314"
print(option.option_type)  # OptionType.CALL
print(option.strike)       # 42000
print(option.asset_class)  # AssetClass.OPTION
```

### シンボルの正規化

```python
from marketsymbol import normalize_symbol

# 小文字を大文字に
print(normalize_symbol("xjpx:7203"))      # "XJPX:7203"

# 全角を半角に
print(normalize_symbol("ＸＪＰＸ：７２０３"))  # "XJPX:7203"

# 空白を除去
print(normalize_symbol("  XJPX:7203  "))  # "XJPX:7203"
```

### シンボルの直接生成

```python
from marketsymbol import EquitySymbol, FutureSymbol, OptionSymbol, OptionType

# 株式シンボル
stock = EquitySymbol(exchange="XJPX", code="7203")
print(str(stock))  # "XJPX:7203"

# 先物シンボル
future = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
print(str(future))  # "XJPX:NK:20250314:F"

# オプションシンボル
option = OptionSymbol(
    exchange="XJPX",
    code="N225O",
    expiry="20250314",
    option_type=OptionType.CALL,
    strike=42000
)
print(str(option))  # "XJPX:N225O:20250314:C:42000"
```

### エラーハンドリング

```python
from marketsymbol import parse_symbol, SymbolParseError

try:
    symbol = parse_symbol("INVALID")
except SymbolParseError as e:
    print(f"Error code: {e.error_code.value}")  # E004
    print(f"Message: {e}")                      # [E004] ...

try:
    symbol = parse_symbol("XX:7203")  # 無効な取引所形式 (4文字でない)
except SymbolParseError as e:
    print(f"Error code: {e.error_code.value}")  # E007
```

### パターンマッチング

```python
from marketsymbol import parse_symbol, EquitySymbol, FutureSymbol, OptionSymbol

symbol = parse_symbol("XJPX:NK:20250314:F")

match symbol:
    case EquitySymbol(exchange, code):
        print(f"Equity: {exchange}:{code}")
    case FutureSymbol(exchange, code, expiry):
        print(f"Future: {exchange}:{code} expiry={expiry}")
    case OptionSymbol(exchange, code, expiry, option_type, strike):
        print(f"Option: {exchange}:{code}")
```

### 型安全な API

```python
from typing import assert_never
from marketsymbol import Symbol, parse_symbol, EquitySymbol, FutureSymbol, OptionSymbol

def describe_symbol(symbol: Symbol) -> str:
    """mypy が全ケースの網羅を検証する."""
    match symbol:
        case EquitySymbol(exchange, code):
            return f"Equity: {exchange}:{code}"
        case FutureSymbol(exchange, code, expiry):
            return f"Future: {exchange}:{code}:{expiry}:F"
        case OptionSymbol(exchange, code, expiry, option_type, strike):
            return f"Option: {exchange}:{code}:{expiry}:{option_type.value}"
        case _ as unreachable:
            assert_never(unreachable)
```

## Vendor Adapters

ベンダー固有のシンボルフォーマットと統一シンボル間の変換をサポートします。

```python
from marketsymbol import (
    BaseAdapter,
    AdapterRegistry,
    Symbol,
    EquitySymbol,
    AssetClass,
)

class MyVendorAdapter(BaseAdapter):
    """カスタムベンダーアダプター."""

    @property
    def supported_asset_classes(self) -> frozenset[AssetClass]:
        return frozenset({AssetClass.EQUITY})

    def to_symbol(self, vendor_symbol: str) -> Symbol:
        # "7203.T" -> EquitySymbol
        code, suffix = vendor_symbol.split(".")
        if suffix == "T":
            return EquitySymbol(exchange="XJPX", code=code)
        raise ValueError(f"Unknown suffix: {suffix}")

    def from_symbol(self, symbol: Symbol) -> str:
        # EquitySymbol -> "7203.T"
        if isinstance(symbol, EquitySymbol) and symbol.exchange == "XJPX":
            return f"{symbol.code}.T"
        raise ValueError("Unsupported symbol")

# Registry への登録
registry = AdapterRegistry()
registry.register("myvendor", MyVendorAdapter())

# 使用
adapter = registry.get("myvendor")
if adapter:
    symbol = adapter.to_symbol("7203.T")
    vendor_str = adapter.from_symbol(symbol)
```

## Symbol Features

### ハッシュ可能

シンボルは辞書のキーやセットの要素として使用できます。

```python
from marketsymbol import parse_symbol, Symbol

prices: dict[Symbol, float] = {
    parse_symbol("XJPX:7203"): 2500.0,
    parse_symbol("XJPX:9984"): 8000.0,
}

symbols: set[Symbol] = {
    parse_symbol("XJPX:7203"),
    parse_symbol("XJPX:9984"),
}
```

### pickle 対応

```python
import pickle
from marketsymbol import parse_symbol

symbol = parse_symbol("XJPX:7203")
data = pickle.dumps(symbol)
restored = pickle.loads(data)
assert symbol == restored
```

## Error Codes

| Code | Description |
|------|-------------|
| E001 | 先物に権利行使価格を指定 |
| E002 | オプション (C/P) に権利行使価格なし |
| E003 | 無効な限月形式 |
| E004 | 無効なセグメント数 |
| E005 | 無効な日付 |
| E006 | 無効なオプション種別 |
| E007 | 無効な取引所コード形式 |
| E008 | 無効な証券/商品コード |
| E009 | 無効な権利行使価格 |
| E010 | シンボル文字列が長すぎる |

## API Reference

### Functions

- `parse_symbol(s: str) -> Symbol` - シンボル文字列をパース
- `normalize_symbol(s: str) -> str` - シンボル文字列を正規化

### Classes

- `EquitySymbol` - 株式・ETF シンボル
- `FutureSymbol` - 先物シンボル
- `OptionSymbol` - オプションシンボル
- `BaseAdapter` - アダプター基底クラス
- `AdapterRegistry` - アダプターレジストリ

### Enums

- `AssetClass` - 資産クラス (EQUITY, FUTURE, OPTION)
- `OptionType` - オプション種別 (CALL, PUT, SERIES)
- `ErrorCode` - エラーコード (E001-E010)

### Exceptions

- `SymbolError` - シンボル例外の基底クラス
- `SymbolParseError` - パースエラー
- `SymbolValidationError` - バリデーションエラー

## License

MIT License
