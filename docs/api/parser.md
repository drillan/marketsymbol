# パース・正規化

シンボル文字列のパースと正規化機能を提供する関数群。

## parse_symbol

シンボル文字列をパースして Symbol オブジェクトを返す。

```{eval-rst}
.. autofunction:: marketsymbol.parse_symbol
```

### 使用例

```python
from marketsymbol import parse_symbol

# 株式シンボル
stock = parse_symbol("XJPX:7203")
print(stock.exchange)  # "XJPX"
print(stock.code)      # "7203"

# 先物シンボル
future = parse_symbol("XJPX:NK:20250314:F")

# オプションシンボル
option = parse_symbol("XJPX:N225O:20250314:C:42000")
```

## normalize_symbol

シンボル文字列を正規化する。

```{eval-rst}
.. autofunction:: marketsymbol.normalize_symbol
```

### 使用例

```python
from marketsymbol import normalize_symbol

# 小文字を大文字に
normalize_symbol("xjpx:7203")  # "XJPX:7203"

# 全角を半角に
normalize_symbol("ＸＪＰＸ：７２０３")  # "XJPX:7203"

# 空白を除去
normalize_symbol("  XJPX:7203  ")  # "XJPX:7203"
```
