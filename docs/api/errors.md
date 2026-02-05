# 例外クラス

シンボル関連の例外クラスとエラーコード。

## ErrorCode

エラーコードを表す列挙型。

```{eval-rst}
.. autoclass:: marketsymbol.ErrorCode
   :members:
   :undoc-members:
```

### エラーコード一覧

| コード | 説明 |
|--------|------|
| `E001` | 先物に権利行使価格を指定 |
| `E002` | オプション (C/P) に権利行使価格なし |
| `E003` | 無効な限月形式 |
| `E004` | 無効なセグメント数 |
| `E005` | 無効な日付 |
| `E006` | 無効なオプション種別 |
| `E007` | 無効な取引所コード形式 |
| `E008` | 無効な証券/商品コード |
| `E009` | 無効な権利行使価格 |
| `E010` | シンボル文字列が長すぎる |

## SymbolError

シンボル関連例外の基底クラス。

```{eval-rst}
.. autoclass:: marketsymbol.SymbolError
   :members:
   :special-members: __str__
   :undoc-members:
```

## SymbolParseError

パース失敗時に発生する例外。

```{eval-rst}
.. autoclass:: marketsymbol.SymbolParseError
   :members:
   :undoc-members:
```

### 使用例

```python
from marketsymbol import parse_symbol, SymbolParseError

try:
    symbol = parse_symbol("INVALID")
except SymbolParseError as e:
    print(f"Error code: {e.error_code.value}")  # E004
    print(f"Message: {e}")
```

## SymbolValidationError

バリデーション失敗時に発生する例外。

```{eval-rst}
.. autoclass:: marketsymbol.SymbolValidationError
   :members:
   :undoc-members:
```
