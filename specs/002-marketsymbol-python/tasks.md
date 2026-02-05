# Tasks: marketsymbol Python 実装

**Input**: Design documents from `/specs/002-marketsymbol-python/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: TDD 必須（Constitution で定義）。各実装タスクの前にテストを作成。

**Organization**: タスクはユーザーストーリー単位で構成。各ストーリーは独立してテスト・検証可能。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 対象ユーザーストーリー（US1, US2, US3 等）
- 説明には正確なファイルパスを含む

## Path Conventions

プロジェクト構成（plan.md より）:

```
python/
├── src/marketsymbol/     # ソースコード
└── tests/                # テストコード
```

---

## Phase 1: Setup (プロジェクト基盤)

**Purpose**: プロジェクト初期化と基本構造の確立

- [ ] T001 pyproject.toml に開発依存関係（pytest, mypy, ruff）を追加 in python/pyproject.toml
- [ ] T002 [P] py.typed マーカーファイルを作成 in python/src/marketsymbol/py.typed
- [ ] T003 [P] pytest 設定ファイルを作成 in python/pyproject.toml
- [ ] T004 [P] mypy 設定（strict モード）を追加 in python/pyproject.toml
- [ ] T005 [P] ruff 設定を追加 in python/pyproject.toml
- [ ] T006 tests/conftest.py を作成（共通フィクスチャ） in python/tests/conftest.py

---

## Phase 2: Foundational (全ストーリー共通基盤)

**Purpose**: 全ユーザーストーリーが依存する基盤コンポーネント

**⚠️ CRITICAL**: このフェーズが完了するまでユーザーストーリーの実装は開始不可

### 定数定義

- [ ] T007 constants.py を作成（MIC_LENGTH, MAX_SYMBOL_LENGTH 等） in python/src/marketsymbol/constants.py

### 列挙型

- [ ] T008 [P] test_enums.py を作成（AssetClass, OptionType テスト） in python/tests/test_enums.py
- [ ] T009 [P] enums.py を作成（AssetClass, OptionType 列挙型） in python/src/marketsymbol/enums.py

### エラー/例外

- [ ] T010 [P] test_errors.py を作成（ErrorCode, SymbolError, SymbolParseError, SymbolValidationError テスト） in python/tests/test_errors.py
- [ ] T011 [P] errors.py を作成（ErrorCode, SymbolError, SymbolParseError, SymbolValidationError） in python/src/marketsymbol/errors.py

**Checkpoint**: 基盤コンポーネント完了 - ユーザーストーリー実装開始可能

---

## Phase 3: User Story 1+2+3 - パース・バリデーション・正規化 (Priority: P1) 🎯 MVP

**Goal**: シンボル文字列をパースして構成要素を取得し、不正入力を検出し、入力を正規化できる

**Rationale**: US1, US2, US3 は密接に連携するため、一体として実装（正規化 → パース → バリデーションのパイプライン）

**Independent Test**: Python REPL で以下を実行し、期待通り動作することを確認:
```python
from marketsymbol import parse_symbol, normalize_symbol, SymbolParseError

# US1: パース
s = parse_symbol("XJPX:7203")
assert s.exchange == "XJPX"
assert s.code == "7203"

# US2: バリデーション
try:
    parse_symbol("XXXX:7203")
except SymbolParseError as e:
    assert e.error_code.value == "E007"

# US3: 正規化
assert normalize_symbol("ｘｊｐｘ：７２０３") == "XJPX:7203"
```

### Symbol クラス実装

- [ ] T012 [P] [US1] test_symbol.py を作成（EquitySymbol, FutureSymbol, OptionSymbol テスト - 生成、str()、等価性、ハッシュ、pickle） in python/tests/test_symbol.py
- [ ] T013 [US1] symbol.py を作成（EquitySymbol, FutureSymbol, OptionSymbol dataclass、Symbol 型エイリアス） in python/src/marketsymbol/symbol.py

### 正規化実装

- [ ] T014 [P] [US3] test_parser.py に正規化テストを作成（小文字、全角、空白除去） in python/tests/test_parser.py
- [ ] T015 [US3] parser.py に normalize_symbol() を実装 in python/src/marketsymbol/parser.py

### バリデーション実装

- [ ] T016 [P] [US2] test_validator.py を作成（exchange, code, expiry, option_type, strike のバリデーションテスト） in python/tests/test_validator.py
- [ ] T017 [US2] validator.py を作成（各フィールドのバリデーション関数、エラーコード E001-E007） in python/src/marketsymbol/validator.py

### パース実装

- [ ] T018 [P] [US1] test_parser.py にパーステストを追加（Equity, Future, Option パース、エッジケース） in python/tests/test_parser.py
- [ ] T019 [US1] parser.py に parse_symbol() を実装（正規化 → セグメント分割 → バリデーション → Symbol 生成） in python/src/marketsymbol/parser.py

### 公開 API

- [ ] T020 [US1] __init__.py に公開 API をエクスポート（parse_symbol, normalize_symbol, Symbol クラス群, 例外, Enum） in python/src/marketsymbol/__init__.py

**Checkpoint**: MVP 完了 - パース・バリデーション・正規化が動作し、独立してテスト可能

---

## Phase 4: User Story 4 - シンボルオブジェクトの直接生成 (Priority: P2)

**Goal**: パースせずに構成要素を指定してシンボルオブジェクトを生成できる

**Independent Test**:
```python
from marketsymbol import EquitySymbol, FutureSymbol, OptionSymbol, OptionType

stock = EquitySymbol(exchange="XJPX", code="7203")
assert str(stock) == "XJPX:7203"

future = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
assert str(future) == "XJPX:NK:20250314:F"
```

### 直接生成時のバリデーション

- [ ] T021 [P] [US4] test_symbol.py に直接生成時のバリデーションテストを追加（無効パラメータでエラー） in python/tests/test_symbol.py
- [ ] T022 [US4] symbol.py に __post_init__ バリデーションを追加（validator.py を利用） in python/src/marketsymbol/symbol.py

**Checkpoint**: 直接生成が動作し、独立してテスト可能

---

## Phase 5: User Story 5 - ベンダーアダプター (Priority: P2)

**Goal**: BaseAdapter を継承してカスタムアダプターを実装し、AdapterRegistry に登録・取得できる

**Independent Test**:
```python
from marketsymbol import BaseAdapter, AdapterRegistry, EquitySymbol, AssetClass

class TestAdapter(BaseAdapter):
    @property
    def supported_asset_classes(self):
        return frozenset({AssetClass.EQUITY})
    def to_symbol(self, vendor_symbol):
        code, _ = vendor_symbol.split(".")
        return EquitySymbol(exchange="XJPX", code=code)
    def from_symbol(self, symbol):
        return f"{symbol.code}.T"

registry = AdapterRegistry()
registry.register("test", TestAdapter())
adapter = registry.get("test")
assert adapter is not None
```

### アダプター基盤

- [ ] T023 [P] [US5] test_adapter.py を作成（BaseAdapter 継承テスト、AdapterRegistry 登録・取得・一覧テスト、スレッドセーフテスト） in python/tests/test_adapter.py
- [ ] T024 [US5] adapter.py を作成（BaseAdapter ABC、AdapterRegistry スレッドセーフ実装） in python/src/marketsymbol/adapter.py
- [ ] T025 [US5] __init__.py にアダプター API をエクスポート追加 in python/src/marketsymbol/__init__.py

**Checkpoint**: アダプター基盤が動作し、独立してテスト可能

---

## Phase 6: User Story 6 - 型安全な API (Priority: P1)

**Goal**: mypy --strict でエラーなし、IDE 補完が効く

**Independent Test**:
```bash
uv --directory ./python run mypy --strict src/marketsymbol
# エラーなしで完了
```

### 型安全性確保

- [ ] T026 [US6] 全ソースファイルに完全な型ヒントを付与（mypy --strict 対応） in python/src/marketsymbol/*.py
- [ ] T027 [US6] mypy --strict を実行してエラーを修正 in python/src/marketsymbol/
- [ ] T028 [US6] パターンマッチング対応を検証（__match_args__ が自動生成されることを確認）

**Checkpoint**: 型安全性が確保され、mypy --strict がパス

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 品質向上と横断的関心事

### Edge Cases

- [ ] T029 [P] test_parser.py にエッジケーステストを追加（空文字、None、長文字列） in python/tests/test_parser.py
- [ ] T030 parser.py にエッジケース処理を実装（TypeError for None, MAX_SYMBOL_LENGTH チェック） in python/src/marketsymbol/parser.py

### 品質チェック

- [ ] T031 ruff check を実行してエラーを修正
- [ ] T032 ruff format --check を実行してフォーマットを確認
- [ ] T033 pytest --cov でカバレッジ 90% 以上を確認

### パフォーマンス検証

- [ ] T036 [P] test_performance.py を作成（parse_symbol が 1ms 以内で完了することを検証、SC-PY-007 対応） in python/tests/test_performance.py

### ドキュメント

- [ ] T034 [P] python/README.md を作成（quickstart.md を参考にクイックスタートガイド）
- [ ] T035 [P] docstring を追加（全公開 API に Google スタイル docstring）

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし - 即座に開始可能
- **Foundational (Phase 2)**: Setup 完了後 - 全ユーザーストーリーをブロック
- **US1+2+3 (Phase 3)**: Foundational 完了後 - MVP
- **US4 (Phase 4)**: Phase 3 完了後 - Symbol クラスのバリデーション強化
- **US5 (Phase 5)**: Foundational 完了後 - Phase 3 と並列実行可能
- **US6 (Phase 6)**: Phase 3〜5 完了後 - 型チェック
- **Polish (Phase 7)**: Phase 6 完了後

### User Story Dependencies

```
Foundational (Phase 2)
        │
        ├──────────────────────────┐
        │                          │
        ▼                          ▼
US1+2+3 (Phase 3) ──┐        US5 (Phase 5)
        │           │              │
        ▼           │              │
  US4 (Phase 4)     │              │
        │           │              │
        └───────────┴──────────────┘
                    │
                    ▼
             US6 (Phase 6)
                    │
                    ▼
            Polish (Phase 7)
```

### Parallel Opportunities

- T002, T003, T004, T005 は並列実行可能（異なるファイル/設定セクション）
- T008, T010 は並列実行可能（テストファイル）
- T009, T011 は並列実行可能（ソースファイル）
- T012, T014, T016, T018 は並列実行可能（テストファイル）
- Phase 3 と Phase 5 は Foundational 完了後に並列実行可能

---

## Parallel Example: Phase 2 (Foundational)

```bash
# テストファイルを並列作成:
Task: "test_enums.py を作成" (T008)
Task: "test_errors.py を作成" (T010)

# ソースファイルを並列作成:
Task: "enums.py を作成" (T009)
Task: "errors.py を作成" (T011)
```

## Parallel Example: Phase 3 (MVP)

```bash
# テストファイルを並列作成:
Task: "test_symbol.py を作成" (T012)
Task: "test_parser.py に正規化テストを作成" (T014)
Task: "test_validator.py を作成" (T016)
Task: "test_parser.py にパーステストを追加" (T018)
```

---

## Implementation Strategy

### MVP First (Phase 1〜3)

1. Phase 1: Setup 完了
2. Phase 2: Foundational 完了
3. Phase 3: US1+2+3 完了（パース・バリデーション・正規化）
4. **STOP and VALIDATE**: quickstart.md のコード例を実行して検証
5. この時点で基本機能が動作する MVP

### Incremental Delivery

1. MVP (Phase 1〜3) → パース・バリデーション・正規化が動作
2. +US4 (Phase 4) → 直接生成が動作
3. +US5 (Phase 5) → アダプター基盤が動作
4. +US6 (Phase 6) → 型安全性が確保
5. +Polish (Phase 7) → 品質基準を満たす

---

## Notes

- [P] タスク = 異なるファイル、依存関係なし
- [Story] ラベル = 特定ユーザーストーリーへのトレーサビリティ
- 各ユーザーストーリーは独立して完了・テスト可能
- TDD: テストを先に書き、失敗を確認してから実装
- 各タスクまたは論理グループ完了後にコミット
- 任意のチェックポイントで停止して独立検証可能
