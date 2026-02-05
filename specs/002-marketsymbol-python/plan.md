# Implementation Plan: marketsymbol Python 実装

**Branch**: `002-marketsymbol-python` | **Date**: 2026-02-05 | **Spec**: [002-marketsymbol-python/spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-marketsymbol-python/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

親仕様 001-marketsymbol で定義された統一シンボルフォーマット（株式・先物・オプション）の Python 実装を提供する。`parse_symbol()` によるパース、`normalize_symbol()` による正規化、型安全な Symbol クラス群、および拡張可能なアダプター基盤を実装する。Python 3.13+ をターゲットとし、dataclass ベースの不変シンボルオブジェクトと mypy --strict 対応の型ヒントを全面採用する。

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: 標準ライブラリのみ（外部依存なし）
**Storage**: N/A（インメモリ処理のみ）
**Testing**: pytest
**Target Platform**: Python 3.13+ が動作する全プラットフォーム
**Project Type**: single（ライブラリプロジェクト）
**Performance Goals**: シンボルパース・バリデーション処理が 1 ミリ秒以内に完了
**Constraints**: 外部依存最小限、mypy --strict 完全準拠
**Scale/Scope**: 単一 Python ライブラリ、6 ユーザーストーリー、19 の機能要件

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Check

| 原則 | 判定 | 根拠 |
|------|------|------|
| I. 独立性優先 | ✅ PASS | 外部依存なし（標準ライブラリのみ）。marketsched はオプショナル依存。 |
| II. 双方向マッピング | ✅ PASS | BaseAdapter で `to_symbol()` / `from_symbol()` を定義 |
| III. シンプルさ優先 | ✅ PASS | 80% ユースケースに最適化。過度な抽象化を避ける |
| IV. 標準準拠 | ✅ PASS | ISO 10383 MIC、PEP 561 に準拠 |
| V. 軽量コア | ✅ PASS | 個別ベンダーアダプターはスコープ外、コアは最小限 |
| 命名の揺れ禁止 | ✅ PASS | 命名規則を constitution に従い統一 |
| 暗黙的フォールバック禁止 | ✅ PASS | エラーは明示的に例外で報告 |
| ハードコード禁止 | ✅ PASS | マジックナンバーに名前を付ける |
| TDD 必須 | ✅ PASS | パーサー、バリデーション、正規化、アダプター基盤は TDD で実装 |

**Gate Result**: ✅ PASS - Phase 0 に進む

### Post-Phase 1 Check

| 原則 | 判定 | 根拠 |
|------|------|------|
| I. 独立性優先 | ✅ PASS | 設計で外部依存なし維持。marketsched はオプショナル。 |
| II. 双方向マッピング | ✅ PASS | BaseAdapter に `to_symbol()` / `from_symbol()` を定義済み |
| III. シンプルさ優先 | ✅ PASS | 3つの具象クラス + 2つの Enum のみ。過度な抽象化なし |
| IV. 標準準拠 | ✅ PASS | ISO 10383 MIC 検証、PEP 561 マーカー含む |
| V. 軽量コア | ✅ PASS | 7ファイルでコア機能を実装。ベンダーアダプターは含まない |
| 命名の揺れ禁止 | ✅ PASS | constitution の命名規則に完全準拠 (exchange, code, expiry, option_type, strike) |
| 暗黙的フォールバック禁止 | ✅ PASS | 全エラーは SymbolParseError / SymbolValidationError で明示的に報告 |
| ハードコード禁止 | ✅ PASS | constants.py で MIC_LENGTH, MAX_SYMBOL_LENGTH 等を定数化 |
| TDD 必須 | ✅ PASS | 実装対象すべてに対応するテストファイルを設計 |

**Gate Result**: ✅ PASS - Phase 2 (Tasks) に進む

## Project Structure

### Documentation (this feature)

```text
specs/002-marketsymbol-python/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command) - N/A for library
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
python/
├── src/
│   └── marketsymbol/
│       ├── __init__.py       # Public API exports
│       ├── py.typed          # PEP 561 marker
│       ├── symbol.py         # Symbol, EquitySymbol, FutureSymbol, OptionSymbol
│       ├── parser.py         # parse_symbol(), normalize_symbol()
│       ├── validator.py      # バリデーションロジック
│       ├── errors.py         # SymbolParseError, SymbolValidationError
│       ├── enums.py          # AssetClass, OptionType 列挙型
│       ├── adapter.py        # BaseAdapter, AdapterRegistry
│       └── constants.py      # MIC_LENGTH, エラーコード定数
├── tests/
│   ├── test_symbol.py
│   ├── test_parser.py
│   ├── test_validator.py
│   ├── test_adapter.py
│   └── conftest.py
└── pyproject.toml
```

**Structure Decision**: 仕様で定義された `src/marketsymbol/` レイアウトを採用。単一ライブラリプロジェクトのため Option 1 (Single project) に従う。`enums.py` と `constants.py` を追加し、関心の分離を明確化。

## Complexity Tracking

> 憲法違反なし。追加の正当化は不要。

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
