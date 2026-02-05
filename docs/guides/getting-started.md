# はじめに

marketsymbol のインストールから基本的な使い方までを解説します。

## インストール

```bash
pip install marketsymbol
```

## 基本的な使い方

### シンボルのパース

`parse_symbol()` 関数を使用してシンボル文字列をパースします。

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

`normalize_symbol()` 関数を使用してシンボル文字列を正規化します。

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

パースせずに構成要素を指定してシンボルを生成できます。

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

## エラーハンドリング

不正なシンボル文字列をパースすると `SymbolParseError` が発生します。

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

エラーコードの詳細は {doc}`../api/errors` を参照してください。

## パターンマッチング

Python 3.10+ のパターンマッチングを使用できます。

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

## 次のステップ

- {doc}`symbol-format` - シンボルフォーマットの詳細仕様
- {doc}`adapter-implementation` - カスタムアダプターの実装方法
- {doc}`../api/index` - API リファレンス
