# アダプター実装ガイド

ベンダー固有のシンボルフォーマットと統一シンボル間の変換を行うカスタムアダプターの実装方法を解説します。

## 概要

marketsymbol では、各ベンダー（データプロバイダー）固有のシンボルフォーマットと統一シンボル間の双方向変換を「アダプター」として実装します。

```
ベンダー固有シンボル ←→ 統一シンボル
     "7203.T"      ←→  XJPX:7203
```

## BaseAdapter の継承

カスタムアダプターは `BaseAdapter` 抽象基底クラスを継承して実装します。

### 実装が必要なメソッド

| メソッド/プロパティ | 説明 |
|--------------------|------|
| `to_symbol(vendor_symbol: str) -> Symbol` | ベンダー固有シンボル → 統一シンボル |
| `from_symbol(symbol: Symbol) -> str` | 統一シンボル → ベンダー固有シンボル |
| `supported_asset_classes: frozenset[AssetClass]` | サポートする資産クラス |

### 実装例

```python
from marketsymbol import (
    BaseAdapter,
    Symbol,
    EquitySymbol,
    FutureSymbol,
    AssetClass,
)


class YahooFinanceAdapter(BaseAdapter):
    """Yahoo Finance 形式のアダプター.

    Yahoo Finance 形式:
    - 株式: "7203.T" (東証)
    - 先物: 未対応
    """

    # 取引所サフィックスのマッピング
    SUFFIX_TO_EXCHANGE = {
        ".T": "XJPX",   # 東証
        ".N": "XNYS",   # NYSE
        ".O": "XNAS",   # NASDAQ
    }

    EXCHANGE_TO_SUFFIX = {v: k for k, v in SUFFIX_TO_EXCHANGE.items()}

    @property
    def supported_asset_classes(self) -> frozenset[AssetClass]:
        """サポートする資産クラス."""
        return frozenset({AssetClass.EQUITY})

    def to_symbol(self, vendor_symbol: str) -> Symbol:
        """ベンダー固有シンボルを統一シンボルに変換.

        Args:
            vendor_symbol: ベンダー固有シンボル (例: "7203.T")

        Returns:
            統一シンボル

        Raises:
            ValueError: 変換できない形式の場合
        """
        # サフィックスを検索
        for suffix, exchange in self.SUFFIX_TO_EXCHANGE.items():
            if vendor_symbol.endswith(suffix):
                code = vendor_symbol[:-len(suffix)]
                return EquitySymbol(exchange=exchange, code=code)

        raise ValueError(f"Unknown vendor symbol format: {vendor_symbol}")

    def from_symbol(self, symbol: Symbol) -> str:
        """統一シンボルをベンダー固有シンボルに変換.

        Args:
            symbol: 統一シンボル

        Returns:
            ベンダー固有シンボル (例: "7203.T")

        Raises:
            ValueError: 変換できないシンボルの場合
            TypeError: サポートしていない資産クラスの場合
        """
        if not isinstance(symbol, EquitySymbol):
            raise TypeError(
                f"Unsupported asset class: {symbol.asset_class}"
            )

        suffix = self.EXCHANGE_TO_SUFFIX.get(symbol.exchange)
        if suffix is None:
            raise ValueError(f"Unknown exchange: {symbol.exchange}")

        return f"{symbol.code}{suffix}"
```

## AdapterRegistry への登録

実装したアダプターは `AdapterRegistry` に登録して使用します。

```python
from marketsymbol import AdapterRegistry

# アダプターのインスタンスを作成
adapter = YahooFinanceAdapter()

# レジストリに登録
registry = AdapterRegistry()
registry.register("yahoo", adapter)

# 使用
yahoo_adapter = registry.get("yahoo")
if yahoo_adapter:
    # ベンダー形式 → 統一シンボル
    symbol = yahoo_adapter.to_symbol("7203.T")
    print(symbol)  # XJPX:7203

    # 統一シンボル → ベンダー形式
    vendor_str = yahoo_adapter.from_symbol(symbol)
    print(vendor_str)  # 7203.T
```

## 複数資産クラスのサポート

先物やオプションもサポートする場合の例:

```python
class MultiAssetAdapter(BaseAdapter):
    """複数資産クラスをサポートするアダプター."""

    @property
    def supported_asset_classes(self) -> frozenset[AssetClass]:
        return frozenset({
            AssetClass.EQUITY,
            AssetClass.FUTURE,
            AssetClass.OPTION,
        })

    def to_symbol(self, vendor_symbol: str) -> Symbol:
        # ベンダー固有の形式を解析
        parts = vendor_symbol.split("_")

        if len(parts) == 2:
            # 株式形式: "7203_T"
            code, exchange_code = parts
            return EquitySymbol(exchange=self._to_mic(exchange_code), code=code)

        elif len(parts) == 4:
            # 先物形式: "NK_202503_F_T"
            code, expiry, asset_type, exchange_code = parts
            if asset_type == "F":
                return FutureSymbol(
                    exchange=self._to_mic(exchange_code),
                    code=code,
                    expiry=self._to_expiry(expiry),
                )

        raise ValueError(f"Unknown format: {vendor_symbol}")

    def from_symbol(self, symbol: Symbol) -> str:
        match symbol:
            case EquitySymbol(exchange, code):
                return f"{code}_{self._from_mic(exchange)}"
            case FutureSymbol(exchange, code, expiry):
                return f"{code}_{self._from_expiry(expiry)}_F_{self._from_mic(exchange)}"
            case _:
                raise TypeError(f"Unsupported: {type(symbol)}")

    def _to_mic(self, code: str) -> str:
        # ベンダー取引所コード → MIC
        mapping = {"T": "XJPX", "N": "XNYS"}
        return mapping.get(code, code)

    def _from_mic(self, mic: str) -> str:
        # MIC → ベンダー取引所コード
        mapping = {"XJPX": "T", "XNYS": "N"}
        return mapping.get(mic, mic)

    def _to_expiry(self, expiry: str) -> str:
        # "202503" → "20250314" (SQ日に変換)
        # 実際の実装では marketsched を使用
        return f"{expiry}14"

    def _from_expiry(self, expiry: str) -> str:
        # "20250314" → "202503"
        return expiry[:6]
```

## エラーハンドリングのベストプラクティス

```python
def to_symbol(self, vendor_symbol: str) -> Symbol:
    # 空文字チェック
    if not vendor_symbol:
        raise ValueError("Empty vendor symbol")

    # 形式チェック
    if "." not in vendor_symbol:
        raise ValueError(
            f"Invalid format: expected 'CODE.SUFFIX', got '{vendor_symbol}'"
        )

    # 変換処理...
```

## スレッドセーフ性

`AdapterRegistry` はスレッドセーフに実装されています。複数スレッドから同時にアクセスしても安全です。

```python
# グローバルレジストリとして使用可能
global_registry = AdapterRegistry()
global_registry.register("yahoo", YahooFinanceAdapter())

# 複数スレッドから安全にアクセス
adapter = global_registry.get("yahoo")
```

## 関連ドキュメント

- {doc}`../api/adapter` - API リファレンス
- {doc}`symbol-format` - シンボルフォーマット仕様
