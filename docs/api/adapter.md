# アダプター基盤

ベンダー固有シンボルと統一シンボル間の変換を行うアダプター基盤。

## BaseAdapter

アダプター抽象基底クラス。カスタムアダプターはこのクラスを継承して実装する。

```{eval-rst}
.. autoclass:: marketsymbol.BaseAdapter
   :members:
   :undoc-members:
```

### 実装が必要なメソッド

| メソッド/プロパティ | 説明 |
|--------------------|------|
| `to_symbol(vendor_symbol)` | ベンダー固有シンボル → 統一シンボル |
| `from_symbol(symbol)` | 統一シンボル → ベンダー固有シンボル |
| `supported_asset_classes` | サポートする資産クラスの frozenset |

## AdapterRegistry

アダプターの登録・検索を管理するレジストリ。スレッドセーフ。

```{eval-rst}
.. autoclass:: marketsymbol.AdapterRegistry
   :members:
   :undoc-members:
```

### 使用例

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
        code, suffix = vendor_symbol.split(".")
        if suffix == "T":
            return EquitySymbol(exchange="XJPX", code=code)
        raise ValueError(f"Unknown suffix: {suffix}")

    def from_symbol(self, symbol: Symbol) -> str:
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
