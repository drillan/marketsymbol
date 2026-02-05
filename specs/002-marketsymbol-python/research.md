# Research: marketsymbol Python 実装

**Date**: 2026-02-05
**Phase**: Phase 0 - Research
**Status**: Complete

## 調査事項と結論

### 1. 不変・ハッシュ可能な dataclass 設計

**Decision**: `@dataclass(frozen=True, slots=True)` を採用

**Rationale**:
- `frozen=True` により不変性を保証（`FrozenInstanceError` で変更を防止）
- `slots=True` によりメモリ効率と属性アクセス速度を向上
- `eq=True`（デフォルト）と `frozen=True` の組み合わせで自動的に `__hash__()` が生成
- Python 3.13 では `copy.replace()` で部分コピーが容易に

**Alternatives considered**:
- `frozen=True` のみ → メモリ効率が低い
- `unsafe_hash=True` → ハッシュ値が変わるリスク

**継承の注意点**:
- 基底クラスが frozen なら派生クラスも frozen にする（混在は TypeError）
- フィールド順序規則に従う（デフォルト値なしフィールドは前に）

**Code pattern**:
```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class BaseSymbol:
    exchange: str
    code: str

@dataclass(frozen=True, slots=True)
class FutureSymbol(BaseSymbol):
    expiry: str
```

### 2. スレッドセーフな AdapterRegistry

**Decision**: Copy-on-Write パターン（書き込み時のみロック、読み取りはロックフリー）

**Rationale**:
- 読み取り頻度が高く、登録は初期化時がほとんどというユースケースに最適
- Python の GIL により `dict` の参照置換はアトミック
- 複雑な RWLock 不要、標準ライブラリのみで実現

**Alternatives considered**:
- 全操作に `Lock` → 読み取り頻度が高いため不要なオーバーヘッド
- サードパーティ RWLock → 依存関係増加

**Code pattern**:
```python
import threading

class AdapterRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._adapters: dict[str, BaseAdapter] = {}

    def register(self, vendor: str, adapter: BaseAdapter) -> None:
        with self._lock:
            new_adapters = self._adapters.copy()
            new_adapters[vendor] = adapter
            self._adapters = new_adapters

    def get(self, vendor: str) -> BaseAdapter | None:
        # Lock-free: dict read is atomic under GIL
        return self._adapters.get(vendor)
```

### 3. カスタム例外クラス設計

**Decision**: 共通基底クラス `SymbolError` + Enum でエラーコード定義

**Rationale**:
- `except SymbolError` で両例外を一括キャッチ可能
- 共通の `error_code` 属性と `__str__` 実装を DRY に保てる
- Enum でエラーコードを型安全に管理

**Alternatives considered**:
- 親クラスなしで個別実装 → コード重複、一括キャッチ不可
- `@property` で error_code → オーバーヘッドがあり不要

**エラーコード体系（仕様より）**:
| コード | 説明 | 例外クラス |
|--------|------|-----------|
| E001 | 先物に権利行使価格を指定 | SymbolParseError |
| E002 | オプション（C/P）に権利行使価格なし | SymbolParseError |
| E003 | 無効な限月形式 | SymbolParseError |
| E004 | 無効なセグメント数 | SymbolParseError |
| E005 | 無効な日付 | SymbolParseError |
| E006 | 無効なオプション種別 | SymbolParseError |
| E007 | 不明な取引所コード | SymbolParseError |

**注**: `parse_symbol()` で発生するエラーは全て `SymbolParseError`。`SymbolValidationError` はシンボルオブジェクト直接生成時（`EquitySymbol()` 等）のバリデーション失敗に使用。

**Code pattern**:
```python
from enum import Enum

class ErrorCode(Enum):
    FUTURE_WITH_STRIKE = "E001"
    OPTION_WITHOUT_STRIKE = "E002"
    INVALID_EXPIRY_FORMAT = "E003"
    INVALID_SEGMENT_COUNT = "E004"
    INVALID_DATE = "E005"
    INVALID_OPTION_TYPE = "E006"
    UNKNOWN_EXCHANGE = "E007"

class SymbolError(Exception):
    def __init__(self, message: str, error_code: ErrorCode) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"[{self.error_code.value}] {self.message}"

class SymbolParseError(SymbolError):
    pass

class SymbolValidationError(SymbolError):
    pass
```

### 4. Union 型とパターンマッチング

**Decision**: Union 型エイリアス + match 文でパターンマッチング

**Rationale**:
- dataclass は自動的に `__match_args__` を生成
- 型チェッカーが Union 型の網羅性を検証可能
- Python 3.10+ の構造的パターンマッチングと相性良好

**Code pattern**:
```python
Symbol = EquitySymbol | FutureSymbol | OptionSymbol

def describe(symbol: Symbol) -> str:
    match symbol:
        case EquitySymbol(exchange, code):
            return f"Equity: {exchange}:{code}"
        case FutureSymbol(exchange, code, expiry):
            return f"Future: {exchange}:{code}:{expiry}:F"
        case OptionSymbol(exchange, code, expiry, option_type, strike):
            return f"Option: {exchange}:{code}:{expiry}:{option_type}:{strike}"
```

### 5. 正規化処理

**Decision**: `unicodedata.normalize("NFKC", s)` + `str.upper()` + `str.strip()`

**Rationale**:
- NFKC 正規化で全角→半角変換（「：」→「:」、「７２０３」→「7203」）
- 大文字変換と空白除去は標準メソッドで十分
- 追加依存なし

**Code pattern**:
```python
import unicodedata

def normalize_symbol(s: str) -> str:
    normalized = unicodedata.normalize("NFKC", s)
    return normalized.upper().strip()
```

### 6. パース戦略

**Decision**: 正規表現ベースのパーサー + セグメント数による資産クラス判定

**Rationale**:
- シンボルフォーマットは明確なパターン（コロン区切り）
- セグメント数で資産クラスを特定:
  - 2セグメント: Equity (`XJPX:7203`)
  - 4セグメント + F: Future (`XJPX:NK:20250314:F`)
  - 4セグメント + O: Option Series (`XJPX:N225O:20250314:O`)
  - 5セグメント + C/P: Option with Strike (`XJPX:N225O:20250314:C:42000`)

**Code pattern**:
```python
import re

SYMBOL_PATTERN = re.compile(r"^([A-Z]{4}):([A-Z0-9]+)(?::(\d{8}):([FCPO])(?::(\d+))?)?$")

def parse_symbol(raw: str) -> Symbol:
    normalized = normalize_symbol(raw)
    match = SYMBOL_PATTERN.match(normalized)
    if not match:
        raise SymbolParseError("Invalid symbol format", ErrorCode.INVALID_SEGMENT_COUNT)
    # ... 資産クラス判定とオブジェクト生成
```

### 7. pickle 対応

**Decision**: `frozen=True, slots=True` で自動対応（Python 3.10+ で修正済み）

**Rationale**:
- Python 3.10 以降、`slots=True` パラメータ使用時の pickle 互換性問題は解決済み
- テストで pickle ラウンドトリップを検証

**注意点**:
- カスタム `__getstate__` / `__setstate__` は frozen + slots 時に無視される

## 次のフェーズへの入力

Phase 1（設計）では以下を踏まえて data-model.md と contracts/ を作成:

1. Symbol 階層: `EquitySymbol`, `FutureSymbol`, `OptionSymbol` の frozen dataclass
2. Enum: `AssetClass`, `OptionType`, `ErrorCode`
3. 例外: `SymbolError` → `SymbolParseError`, `SymbolValidationError`
4. レジストリ: Copy-on-Write パターンの `AdapterRegistry`
5. パーサー: 正規表現ベース + normalize → parse → validate のパイプライン
