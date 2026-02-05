# Data Model: marketsymbol Python 実装

**Date**: 2026-02-05
**Phase**: Phase 1 - Design
**Status**: Complete

## Entity Relationship

```
┌─────────────────────────────────────────────────────────────────┐
│                        Symbol (Protocol)                        │
│  - exchange: str                                                │
│  - code: str                                                    │
│  - asset_class: AssetClass                                      │
│  - __str__() -> str                                             │
└─────────────────────────────────────────────────────────────────┘
                                ▲
                                │ implements
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────┴───────┐       ┌───────┴───────┐       ┌───────┴───────┐
│  EquitySymbol │       │ FutureSymbol  │       │ OptionSymbol  │
│  (dataclass)  │       │  (dataclass)  │       │  (dataclass)  │
├───────────────┤       ├───────────────┤       ├───────────────┤
│ exchange: str │       │ exchange: str │       │ exchange: str │
│ code: str     │       │ code: str     │       │ code: str     │
│               │       │ expiry: str   │       │ expiry: str   │
│               │       │               │       │ option_type:  │
│               │       │               │       │   OptionType  │
│               │       │               │       │ strike: int   │
└───────────────┘       └───────────────┘       └───────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      AdapterRegistry                            │
│  - _adapters: dict[str, BaseAdapter]                            │
│  - _lock: threading.Lock                                        │
│  + register(vendor: str, adapter: BaseAdapter) -> None          │
│  + get(vendor: str) -> BaseAdapter | None                       │
│  + list() -> list[str]                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ manages
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BaseAdapter (ABC)                           │
│  + to_symbol(vendor_symbol: str) -> Symbol                      │
│  + from_symbol(symbol: Symbol) -> str                           │
│  + supported_asset_classes: frozenset[AssetClass]               │
└─────────────────────────────────────────────────────────────────┘
```

## Entities

### 1. EquitySymbol

株式・ETF を識別するシンボル。

```python
@dataclass(frozen=True, slots=True)
class EquitySymbol:
    """株式・ETF シンボル"""
    exchange: str  # ISO 10383 MIC (4文字)
    code: str      # 証券コード (1-10文字)

    @property
    def asset_class(self) -> AssetClass:
        return AssetClass.EQUITY

    def __str__(self) -> str:
        return f"{self.exchange}:{self.code}"
```

**Validation Rules**:
- `exchange`: 4文字の英大文字 (ISO 10383 MIC)
- `code`: 1-10文字の英数字

### 2. FutureSymbol

先物を識別するシンボル。

```python
@dataclass(frozen=True, slots=True)
class FutureSymbol:
    """先物シンボル"""
    exchange: str  # ISO 10383 MIC (4文字)
    code: str      # 商品コード (2-6文字)
    expiry: str    # 限月 (YYYYMMDD形式)

    @property
    def asset_class(self) -> AssetClass:
        return AssetClass.FUTURE

    def __str__(self) -> str:
        return f"{self.exchange}:{self.code}:{self.expiry}:F"
```

**Validation Rules**:
- `exchange`: 4文字の英大文字 (ISO 10383 MIC)
- `code`: 2-6文字の英数字
- `expiry`: 8桁の数字 (YYYYMMDD)、有効な日付

### 3. OptionSymbol

オプションを識別するシンボル。

```python
@dataclass(frozen=True, slots=True)
class OptionSymbol:
    """オプションシンボル"""
    exchange: str           # ISO 10383 MIC (4文字)
    code: str               # 商品コード (2-10文字)
    expiry: str             # 限月 (YYYYMMDD形式)
    option_type: OptionType # C/P/O (CALL/PUT/SERIES)
    strike: int | None      # 権利行使価格 (C/Pは必須、Oはなし)

    @property
    def asset_class(self) -> AssetClass:
        return AssetClass.OPTION

    def __str__(self) -> str:
        if self.option_type == OptionType.SERIES:
            return f"{self.exchange}:{self.code}:{self.expiry}:O"
        return f"{self.exchange}:{self.code}:{self.expiry}:{self.option_type.value}:{self.strike}"
```

**Validation Rules**:
- `exchange`: 4文字の英大文字 (ISO 10383 MIC)
- `code`: 2-10文字の英数字
- `expiry`: 8桁の数字 (YYYYMMDD)、有効な日付
- `option_type`: C, P, または O
- `strike`: C/P の場合は正の整数が必須、O の場合は None

### 4. AssetClass (Enum)

資産クラス列挙型。

```python
class AssetClass(Enum):
    """資産クラス"""
    EQUITY = "equity"
    FUTURE = "future"
    OPTION = "option"
```

### 5. OptionType (Enum)

オプション種別列挙型。

```python
class OptionType(Enum):
    """オプション種別"""
    CALL = "C"
    PUT = "P"
    SERIES = "O"  # シリーズ識別用（権利行使価格なし）
```

### 6. ErrorCode (Enum)

エラーコード列挙型。

```python
class ErrorCode(Enum):
    """エラーコード（E001-E007）"""
    FUTURE_WITH_STRIKE = "E001"      # 先物に権利行使価格を指定
    OPTION_WITHOUT_STRIKE = "E002"   # オプション（C/P）に権利行使価格なし
    INVALID_EXPIRY_FORMAT = "E003"   # 無効な限月形式
    INVALID_SEGMENT_COUNT = "E004"   # 無効なセグメント数
    INVALID_DATE = "E005"            # 無効な日付
    INVALID_OPTION_TYPE = "E006"     # 無効なオプション種別
    UNKNOWN_EXCHANGE = "E007"        # 不明な取引所コード
```

### 7. SymbolError (Base Exception)

シンボル関連例外の基底クラス。

```python
class SymbolError(Exception):
    """シンボル関連例外の基底クラス"""

    def __init__(self, message: str, error_code: ErrorCode) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"[{self.error_code.value}] {self.message}"
```

### 8. SymbolParseError

パース失敗時の例外。

```python
class SymbolParseError(SymbolError):
    """シンボルパース失敗時の例外"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        *,
        raw_symbol: str | None = None,
    ) -> None:
        super().__init__(message, error_code)
        self.raw_symbol = raw_symbol
```

### 9. SymbolValidationError

バリデーション失敗時の例外。

```python
class SymbolValidationError(SymbolError):
    """シンボルバリデーション失敗時の例外"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        *,
        field_name: str | None = None,
        field_value: object = None,
    ) -> None:
        super().__init__(message, error_code)
        self.field_name = field_name
        self.field_value = field_value
```

### 10. BaseAdapter (ABC)

アダプター抽象基底クラス。

```python
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """ベンダーアダプター抽象基底クラス"""

    @abstractmethod
    def to_symbol(self, vendor_symbol: str) -> Symbol:
        """ベンダー固有シンボルを統一シンボルに変換"""
        ...

    @abstractmethod
    def from_symbol(self, symbol: Symbol) -> str:
        """統一シンボルをベンダー固有シンボルに変換"""
        ...

    @property
    @abstractmethod
    def supported_asset_classes(self) -> frozenset[AssetClass]:
        """サポートする資産クラスを返す"""
        ...
```

### 11. AdapterRegistry

アダプターレジストリ（スレッドセーフ）。

```python
import threading

class AdapterRegistry:
    """スレッドセーフなアダプターレジストリ"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._adapters: dict[str, BaseAdapter] = {}

    def register(self, vendor: str, adapter: BaseAdapter) -> None:
        """アダプターを登録"""
        with self._lock:
            if vendor in self._adapters:
                raise ValueError(f"Adapter for '{vendor}' already registered")
            new_adapters = self._adapters.copy()
            new_adapters[vendor] = adapter
            self._adapters = new_adapters

    def get(self, vendor: str) -> BaseAdapter | None:
        """アダプターを取得（ロックフリー）"""
        return self._adapters.get(vendor)

    def list(self) -> list[str]:
        """登録済みベンダー名一覧"""
        return list(self._adapters.keys())
```

## Symbol Type Alias

Union 型エイリアス。

```python
Symbol = EquitySymbol | FutureSymbol | OptionSymbol
```

## Public API Functions

### parse_symbol

```python
def parse_symbol(raw: str) -> Symbol:
    """シンボル文字列をパースして Symbol オブジェクトを返す

    Args:
        raw: シンボル文字列（例: "XJPX:7203", "XJPX:NK:20250314:F"）

    Returns:
        パース結果の Symbol オブジェクト

    Raises:
        SymbolParseError: パース失敗時
        TypeError: raw が str でない場合
    """
    ...
```

### normalize_symbol

```python
def normalize_symbol(raw: str) -> str:
    """シンボル文字列を正規化

    - 全角→半角変換（NFKC正規化）
    - 大文字変換
    - 前後空白除去

    Args:
        raw: 正規化前のシンボル文字列

    Returns:
        正規化後のシンボル文字列
    """
    ...
```

## Validation Rules Summary

| フィールド | ルール | エラーコード |
|-----------|--------|-------------|
| exchange | 4文字英大文字 (MIC) | E007 |
| code | 1-10文字英数字 | E004 |
| expiry | 8桁数字 (YYYYMMDD) | E003 |
| expiry | 有効な日付 | E005 |
| option_type | C/P/O のみ | E006 |
| strike (C/P) | 正の整数、必須 | E002 |
| strike (Future) | 指定禁止 | E001 |

## Constants

```python
# ISO 10383 MIC コード長
MIC_LENGTH = 4

# コードの最小/最大長
MIN_CODE_LENGTH = 1
MAX_CODE_LENGTH = 10

# 限月の長さ
EXPIRY_LENGTH = 8

# 権利行使価格の最小値
MIN_STRIKE = 1

# シンボル文字列の最大長（DoS対策）
MAX_SYMBOL_LENGTH = 100
```
