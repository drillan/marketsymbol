# Quickstart: marketsymbol Python

## Installation

```bash
pip install marketsymbol
```

## Basic Usage

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
from marketsymbol import parse_symbol, SymbolParseError, SymbolValidationError

try:
    symbol = parse_symbol("INVALID")
except SymbolParseError as e:
    print(f"エラーコード: {e.error_code.value}")  # E004
    print(f"メッセージ: {e}")                    # [E004] ...

try:
    symbol = parse_symbol("XXXX:7203")  # 不明な取引所
except SymbolParseError as e:
    print(f"エラーコード: {e.error_code.value}")  # E007
    print(f"メッセージ: {e}")                    # [E007] ...
```

### パターンマッチング

```python
from marketsymbol import parse_symbol, EquitySymbol, FutureSymbol, OptionSymbol

symbol = parse_symbol("XJPX:NK:20250314:F")

match symbol:
    case EquitySymbol(exchange, code):
        print(f"株式: {exchange}:{code}")
    case FutureSymbol(exchange, code, expiry):
        print(f"先物: {exchange}:{code} 限月{expiry}")
    case OptionSymbol(exchange, code, expiry, option_type, strike):
        print(f"オプション: {exchange}:{code}")
```

### パターンマッチングの網羅性チェック

```python
from typing import assert_never
from marketsymbol import Symbol, parse_symbol, EquitySymbol, FutureSymbol, OptionSymbol

def describe_symbol(symbol: Symbol) -> str:
    """mypy が全ケースを網羅していることを検証"""
    match symbol:
        case EquitySymbol(exchange, code):
            return f"Equity: {exchange}:{code}"
        case FutureSymbol(exchange, code, expiry):
            return f"Future: {exchange}:{code}:{expiry}:F"
        case OptionSymbol(exchange, code, expiry, option_type, strike):
            return f"Option: {exchange}:{code}:{expiry}:{option_type.value}"
        case _ as unreachable:
            # 新しい Symbol 型が追加されたら mypy がここでエラーを報告
            assert_never(unreachable)
```

## アダプターの実装

```python
from marketsymbol import (
    BaseAdapter,
    AdapterRegistry,
    Symbol,
    EquitySymbol,
    AssetClass,
)

class MyVendorAdapter(BaseAdapter):
    """カスタムベンダーアダプター"""

    @property
    def supported_asset_classes(self) -> frozenset[AssetClass]:
        return frozenset({AssetClass.EQUITY})

    def to_symbol(self, vendor_symbol: str) -> Symbol:
        # "7203.T" → EquitySymbol
        code, suffix = vendor_symbol.split(".")
        if suffix == "T":
            return EquitySymbol(exchange="XJPX", code=code)
        raise ValueError(f"Unknown suffix: {suffix}")

    def from_symbol(self, symbol: Symbol) -> str:
        # EquitySymbol → "7203.T"
        if isinstance(symbol, EquitySymbol) and symbol.exchange == "XJPX":
            return f"{symbol.code}.T"
        raise ValueError("Unsupported symbol")

# レジストリへの登録
registry = AdapterRegistry()
registry.register("myvendor", MyVendorAdapter())

# 使用
adapter = registry.get("myvendor")
if adapter:
    symbol = adapter.to_symbol("7203.T")
    vendor_str = adapter.from_symbol(symbol)
```

## 型ヒントの活用

```python
from marketsymbol import Symbol, parse_symbol

def process_symbol(symbol: Symbol) -> str:
    """型安全なシンボル処理"""
    return str(symbol)

# mypy で型チェック可能
symbol = parse_symbol("XJPX:7203")
result = process_symbol(symbol)
```

## 辞書のキーとして使用

```python
from marketsymbol import parse_symbol

# シンボルは hashable なので辞書のキーに使える
prices: dict[Symbol, float] = {
    parse_symbol("XJPX:7203"): 2500.0,
    parse_symbol("XJPX:9984"): 8000.0,
}

# セットにも追加可能
symbols: set[Symbol] = {
    parse_symbol("XJPX:7203"),
    parse_symbol("XJPX:9984"),
}
```

## pickle 対応

```python
import pickle
from marketsymbol import parse_symbol

# シリアライズ
symbol = parse_symbol("XJPX:7203")
data = pickle.dumps(symbol)

# デシリアライズ
restored = pickle.loads(data)
assert symbol == restored
```
