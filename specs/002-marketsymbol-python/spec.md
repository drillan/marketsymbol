# Feature Specification: marketsymbol Python 実装

**Feature Branch**: `002-marketsymbol-python`
**Created**: 2026-02-05
**Status**: Draft
**Parent Spec**: [001-marketsymbol](../001-marketsymbol/spec.md)
**Input**: User description: "specs/001-marketsymbol/spec.md を親仕様とした、Python実装 002-marketsymbol-python の仕様を策定"

## Overview

本仕様は親仕様 [001-marketsymbol](../001-marketsymbol/spec.md) で定義された統一シンボルフォーマットの **Python 実装** を定義する。親仕様の全機能要件 (FR-001 〜 FR-024) を Python で実装し、Python エコシステム（型ヒント、パッケージ構成、テストフレームワーク）に適合させる。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - シンボル文字列のパースと構成要素取得 (Priority: P1)

Python 開発者が `marketsymbol` パッケージをインポートし、シンボル文字列（`"XJPX:7203"` や `"XJPX:NK:20250314:F"` など）を数行のコードでパースして構成要素（取引所、コード、限月、資産クラス等）を取得できる。

**Why this priority**: ライブラリの最も基本的な機能。これがなければ他の全機能が成り立たない。

**Independent Test**: `pip install marketsymbol` 後、Python REPL で `from marketsymbol import parse_symbol; s = parse_symbol("XJPX:7203")` を実行し、`s.exchange`, `s.code`, `s.asset_class` にアクセスできることで検証可能。

**Acceptance Scenarios**:

1. **Given** インストール済みの `marketsymbol` パッケージ, **When** `parse_symbol("XJPX:7203")` を実行, **Then** `exchange="XJPX"`, `code="7203"`, `asset_class=AssetClass.EQUITY` を持つオブジェクトが返される
2. **Given** インストール済みの `marketsymbol` パッケージ, **When** `parse_symbol("XJPX:NK:20250314:F")` を実行, **Then** `exchange="XJPX"`, `code="NK"`, `expiry="20250314"`, `asset_class=AssetClass.FUTURE` を持つオブジェクトが返される
3. **Given** インストール済みの `marketsymbol` パッケージ, **When** `parse_symbol("XJPX:N225O:20250314:C:42000")` を実行, **Then** `exchange="XJPX"`, `code="N225O"`, `expiry="20250314"`, `option_type=OptionType.CALL`, `strike=42000`, `asset_class=AssetClass.OPTION` を持つオブジェクトが返される
4. **Given** パース結果のシンボルオブジェクト, **When** `str()` で文字列に変換, **Then** 元のシンボル文字列と同一の正規化された文字列が返される

---

### User Story 2 - シンボルのバリデーションとエラーハンドリング (Priority: P1)

Python 開発者が不正なシンボル文字列を検出し、Python 標準の例外機構を通じて適切なエラーメッセージとエラーコードを取得できる。try-except で捕捉し、エラー種別に応じた処理が可能。

**Why this priority**: データ品質保証の基盤。不正データの早期検出がシステム信頼性に直結。パース機能と同等に重要。

**Independent Test**: 不正なシンボル文字列を `parse_symbol()` に渡し、`SymbolParseError` 例外が発生することで検証可能。

**Acceptance Scenarios**:

1. **Given** 無効な取引所コード "XXXX:7203", **When** `parse_symbol()` を実行, **Then** `SymbolParseError` が発生し、`error_code="E007"`, `message` に「不明な取引所コードです」を含む
2. **Given** 先物に権利行使価格を指定 "XJPX:NK:20250314:F:42000", **When** `parse_symbol()` を実行, **Then** `SymbolParseError` が発生し、`error_code="E001"` が設定される
3. **Given** オプションに権利行使価格なし "XJPX:N225O:20250314:C", **When** `parse_symbol()` を実行, **Then** `SymbolParseError` が発生し、`error_code="E002"` が設定される
4. **Given** 無効な日付の限月 "XJPX:NK:20250332:F", **When** `parse_symbol()` を実行, **Then** `SymbolParseError` が発生し、`error_code="E005"` が設定される
5. **Given** `SymbolParseError` 例外, **When** `str()` で文字列化, **Then** エラーコードとメッセージを含む人間可読な文字列が返される

---

### User Story 3 - シンボルの正規化 (Priority: P1)

Python 開発者が小文字や全角文字を含むシンボル文字列を正規化（大文字変換、半角変換、空白除去）できる。正規化は自動的にパース時に適用されるか、明示的に `normalize_symbol()` 関数で実行できる。

**Why this priority**: データ品質の標準化に必須。パース機能の前処理として必要。

**Independent Test**: 小文字・全角を含むシンボルを正規化し、期待する半角大文字の文字列が返されることで検証可能。

**Acceptance Scenarios**:

1. **Given** 小文字を含むシンボル "xjpx:7203", **When** `normalize_symbol()` を実行, **Then** `"XJPX:7203"` が返される
2. **Given** 全角文字を含むシンボル "ＸＪＰＸ：７２０３", **When** `normalize_symbol()` を実行, **Then** `"XJPX:7203"` が返される
3. **Given** 前後に空白を含むシンボル "  XJPX:7203  ", **When** `normalize_symbol()` を実行, **Then** `"XJPX:7203"` が返される
4. **Given** 正規化が必要なシンボル, **When** `parse_symbol()` で直接パース, **Then** 自動的に正規化されてからパースされる

---

### User Story 4 - シンボルオブジェクトの生成 (Priority: P2)

Python 開発者がシンボル文字列をパースせずに、構成要素（取引所、コード、限月等）を指定してシンボルオブジェクトを直接生成できる。ファクトリ関数またはクラスコンストラクタで作成可能。

**Why this priority**: プログラム内でシンボルを動的に生成する際に必要。パースとバリデーションの基盤の上に構築。

**Independent Test**: `EquitySymbol(exchange="XJPX", code="7203")` でオブジェクトを生成し、`str()` で `"XJPX:7203"` が返されることで検証可能。

**Acceptance Scenarios**:

1. **Given** 取引所="XJPX", コード="7203", **When** `EquitySymbol(exchange="XJPX", code="7203")` を実行, **Then** 株式シンボルオブジェクトが生成され、`str()` で `"XJPX:7203"` が返される
2. **Given** 取引所="XJPX", コード="NK", 限月="20250314", **When** `FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")` を実行, **Then** 先物シンボルオブジェクトが生成され、`str()` で `"XJPX:NK:20250314:F"` が返される
3. **Given** 取引所="XJPX", コード="N225O", 限月="20250314", オプション種別=CALL, 権利行使価格=42000, **When** `OptionSymbol(...)` を実行, **Then** オプションシンボルオブジェクトが生成され、`str()` で `"XJPX:N225O:20250314:C:42000"` が返される
4. **Given** 無効なパラメータ（負の権利行使価格など）, **When** シンボルオブジェクトを生成, **Then** `SymbolValidationError` が発生する

---

### User Story 5 - ベンダーアダプターの実装と登録 (Priority: P2)

Python 開発者が `BaseAdapter` クラスを継承してカスタムアダプターを実装し、`AdapterRegistry` に登録できる。アダプターはベンダー固有シンボルと統一シンボル間の双方向変換を提供する。

**Why this priority**: 複数ベンダー対応がシステムの拡張性と実用性を決定。コア機能の上に構築。

**Independent Test**: `BaseAdapter` を継承したクラスを作成し、`to_symbol()` と `from_symbol()` メソッドを実装して双方向変換できることで検証可能。

**Acceptance Scenarios**:

1. **Given** `BaseAdapter` を継承したカスタムアダプター, **When** `registry.register("vendor_a", adapter)` を実行, **Then** アダプターが登録され、`registry.get("vendor_a")` で取得可能
2. **Given** 登録済みのベンダーAアダプター, **When** `adapter.to_symbol("7203.T")` を実行, **Then** 統一シンボル `EquitySymbol(exchange="XJPX", code="7203")` が返される
3. **Given** 登録済みのベンダーAアダプター, **When** `adapter.from_symbol(EquitySymbol(exchange="XJPX", code="7203"))` を実行, **Then** ベンダー固有形式 `"7203.T"` が返される
4. **Given** 未登録のベンダー名, **When** `registry.get("unknown")` を実行, **Then** `AdapterNotFoundError` が発生する
5. **Given** 複数のアダプターが登録済み, **When** `registry.list()` を実行, **Then** 登録済みベンダー名のリストが返される

---

### User Story 6 - 型安全な API (Priority: P1)

Python 開発者が型ヒント（Type Hints）を活用して IDE の補完やmypy による静的型チェックを受けられる。全ての公開 API が適切な型注釈を持つ。

**Why this priority**: Python 3.13 以上を対象とする本ライブラリでは型安全性がベストプラクティス。開発体験に直結。

**Independent Test**: mypy で `marketsymbol` パッケージをチェックし、エラーなしでパスすることで検証可能。

**Acceptance Scenarios**:

1. **Given** `marketsymbol` パッケージ, **When** `mypy --strict src/marketsymbol` を実行, **Then** エラーなしで完了する
2. **Given** VSCode + Pylance 環境, **When** `parse_symbol()` の戻り値にアクセス, **Then** IDE が `exchange`, `code`, `asset_class` 等のプロパティを補完候補として表示する
3. **Given** `Union[EquitySymbol, FutureSymbol, OptionSymbol]` 型の変数, **When** `match` 文でパターンマッチ, **Then** 各ブランチで適切な型が推論される

---

### Edge Cases

- 空文字列のシンボルが `parse_symbol()` に渡された場合：`SymbolParseError` を発生させる
- `None` が `parse_symbol()` に渡された場合：`TypeError` を発生させる
- 非常に長い文字列（1000文字以上）が渡された場合：適切なエラーを返す（DoS 対策）
- シンボルオブジェクトの `__eq__` でオブジェクト同士を比較可能（同一シンボルは等価）
- シンボルオブジェクトは不変（immutable）であり、作成後に変更できない
- シンボルオブジェクトは辞書のキーやセットの要素として使用可能（hashable）
- スレッドセーフ：`AdapterRegistry` は複数スレッドからの同時アクセスに対応
- pickle 対応：シンボルオブジェクトはシリアライズ・デシリアライズ可能

## Requirements *(mandatory)*

### Functional Requirements

*親仕様 001-marketsymbol の FR-001〜FR-026 を Python で実装。以下は Python 固有の実装要件。*

#### パッケージ構成

- **FR-PY-001**: パッケージは `marketsymbol` という名前で `pip install marketsymbol` でインストール可能であること
- **FR-PY-002**: パッケージは Python 3.13 以上をサポートすること
- **FR-PY-003**: パッケージは `src/marketsymbol/` レイアウトを採用すること
- **FR-PY-004**: パッケージは `pyproject.toml` で依存関係とメタデータを管理すること

#### 公開 API

- **FR-PY-005**: `parse_symbol(s: str) -> Symbol` 関数を提供すること（シンボル文字列をパース）
- **FR-PY-006**: `normalize_symbol(s: str) -> str` 関数を提供すること（正規化のみ）
- **FR-PY-007**: `EquitySymbol`, `FutureSymbol`, `OptionSymbol` クラスを提供すること
- **FR-PY-008**: `AssetClass` 列挙型（`EQUITY`, `FUTURE`, `OPTION`）を提供すること
- **FR-PY-009**: `OptionType` 列挙型（`CALL`, `PUT`, `SERIES`）を提供すること
- **FR-PY-010**: `SymbolParseError`, `SymbolValidationError` 例外クラスを提供すること
- **FR-PY-011**: 例外クラスは `error_code` 属性でエラーコード（E001〜E007）を保持すること

#### アダプター

- **FR-PY-012**: `BaseAdapter` 抽象基底クラスを提供すること
- **FR-PY-013**: `AdapterRegistry` クラスを提供すること
- **FR-PY-014**: `BaseAdapter` は `to_symbol(vendor_symbol: str) -> Symbol` 抽象メソッドを定義すること
- **FR-PY-015**: `BaseAdapter` は `from_symbol(symbol: Symbol) -> str` 抽象メソッドを定義すること
- **FR-PY-016**: `BaseAdapter` は `supported_asset_classes` プロパティでサポートする資産クラスを宣言すること

#### 型安全性

- **FR-PY-017**: 全ての公開 API に型ヒントを付与すること
- **FR-PY-018**: `mypy --strict` でエラーなしとなること
- **FR-PY-019**: `py.typed` マーカーファイルを含め PEP 561 に準拠すること

### Key Entities

- **Symbol**: シンボルオブジェクトの基底クラスまたはプロトコル。`exchange`, `code`, `asset_class` 属性を持つ
- **EquitySymbol**: 株式・ETF シンボル。`exchange`, `code` 属性を持つ
- **FutureSymbol**: 先物シンボル。`exchange`, `code`, `expiry` 属性を持つ
- **OptionSymbol**: オプションシンボル。`exchange`, `code`, `expiry`, `option_type`, `strike` 属性を持つ
- **AssetClass**: 資産クラス列挙型（`EQUITY`, `FUTURE`, `OPTION`）
- **OptionType**: オプション種別列挙型（`CALL`, `PUT`, `SERIES`）
- **BaseAdapter**: アダプター抽象基底クラス。双方向変換メソッドを定義
- **AdapterRegistry**: アダプターの登録・検索を管理するレジストリ
- **SymbolParseError**: パース失敗時の例外。`error_code` 属性を持つ
- **SymbolValidationError**: バリデーション失敗時の例外。`error_code` 属性を持つ

## Technical Constraints

### Python バージョン

- Python 3.13 以上必須

### 依存関係

- 外部依存は最小限に抑える（標準ライブラリのみを推奨）
- marketsched はオプショナル依存（SQ 日取得機能のみで使用）

### 開発ツール

- パッケージ管理: uv
- テストフレームワーク: pytest
- 型チェック: mypy (strict モード)
- リンター: ruff
- フォーマッター: ruff format

### プロジェクト構成

```
marketsymbol/
└── python/
    ├── src/
    │   └── marketsymbol/
    │       ├── __init__.py
    │       ├── py.typed
    │       ├── symbol.py        # Symbol クラス群
    │       ├── parser.py        # parse_symbol, normalize_symbol
    │       ├── validator.py     # バリデーションロジック
    │       ├── errors.py        # 例外クラス
    │       └── adapter.py       # BaseAdapter, AdapterRegistry
    ├── tests/
    │   ├── test_symbol.py
    │   ├── test_parser.py
    │   ├── test_validator.py
    │   └── test_adapter.py
    └── pyproject.toml
```

## Assumptions

- 親仕様 001-marketsymbol の全ての前提・仮定を継承する
- Python 開発者は型ヒントとモダン Python（3.13+）に馴染みがあると想定
- シンボルオブジェクトは dataclass または同等の機構で実装（不変性を保証）
- スレッドセーフ性はグローバルな AdapterRegistry のみ考慮（シンボルオブジェクトは不変なので自動的にスレッドセーフ）

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-PY-001**: 開発者は 5 行以内のコードでシンボル文字列をパースし、構成要素にアクセスできる
- **SC-PY-002**: 親仕様で定義された全てのテストケースが pytest でパスする
- **SC-PY-003**: `mypy --strict src/marketsymbol` がエラーなしで完了する
- **SC-PY-004**: `ruff check` と `ruff format --check` がエラーなしで完了する
- **SC-PY-005**: テストカバレッジが 90% 以上である
- **SC-PY-006**: 新規アダプターの実装が 30 行以内のコードで完了できる
- **SC-PY-007**: シンボルのパース・バリデーション処理が 1 ミリ秒以内に完了する（単一シンボル）
- **SC-PY-008**: PyPI への公開が可能な状態（メタデータ、README、LICENSE 完備）

## Dependencies

- **Python 3.13+**: 必須
- **marketsched** (オプション): SQ 日取得。未インストール時は SQ 日関連機能が無効化
- **pytest** (開発): テスト実行
- **mypy** (開発): 型チェック
- **ruff** (開発): リント・フォーマット

## References

- [親仕様: 001-marketsymbol](../001-marketsymbol/spec.md)
- [ADR-001: シンボル仕様](../../docs/adr/symbol/001-symbol-specification.md)
- [ADR-002: 限月フォーマットの統一](../../docs/adr/symbol/002-weekly-expiry-format.md)
- [PEP 561 – Distributing and Packaging Type Information](https://peps.python.org/pep-0561/)
- [marketschema Python 実装](https://github.com/drillan/marketschema) - 参考実装
