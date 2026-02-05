# marketsymbol

金融市場商品のシンボル仕様と実装。

```{toctree}
:maxdepth: 2
:caption: 目次

guides/index
api/index
glossary
adr/index
research/index
```

## 概要

marketsymbol は金融市場商品の標準化されたシンボルフォーマットを提供します。

### 主な機能

- シンボル文字列のパース・正規化・バリデーション
- 株式、先物、オプションの各資産クラスをサポート
- ベンダー固有フォーマットとの相互変換（アダプター機構）
- 型安全な API（`mypy --strict` 対応）
- Python 3.13+ 対応

### クイックスタート

```python
from marketsymbol import parse_symbol

# 株式シンボル
stock = parse_symbol("XJPX:7203")
print(stock.exchange)     # "XJPX"
print(stock.code)         # "7203"

# 先物シンボル
future = parse_symbol("XJPX:NK:20250314:F")

# オプションシンボル
option = parse_symbol("XJPX:N225O:20250314:C:42000")
```

詳細は {doc}`guides/getting-started` を参照してください。

## インデックス

- {ref}`genindex`
- {ref}`search`
