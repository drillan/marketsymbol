<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.1 → 1.0.2

Modified Principles:
- Scope Definition: 限月フォーマットを spec.md と整合（週次限月の説明追加）

Added Sections:
- なし

Removed Sections:
- なし

Templates Requiring Updates:
- .specify/templates/plan-template.md ✅ (Constitution Check セクションは動的に評価)
- .specify/templates/spec-template.md ✅ (変更不要)
- .specify/templates/tasks-template.md ✅ (変更不要)

Follow-up TODOs:
- なし
==================
-->

# marketsymbol Constitution

プロジェクトの基本原則を定義する。すべての設計判断はこの原則に基づいて行う。

## Mission

> 金融市場商品を、データソースに依存しない統一的なシンボルで識別・管理できるようにする

## Core Principles

### I. 独立性優先

marketsymbol は完全に独立して動作する。外部プロジェクト（market-hub, marketschema）への依存は不要。

- market-hub がインストールされている場合のみ、追加の統合管理機能が利用可能
- marketschema との連携はオプショナル機能として提供
- 単体で完全なシンボル管理機能を提供する

**Rationale**: 外部依存を最小化することで、採用障壁を下げ、メンテナンス性を向上させる。

### II. 双方向マッピング

ベンダー固有シンボルと統一シンボルの双方向変換を提供する。

- **正規化**: ベンダー固有シンボル → 統一シンボル
- **逆引き**: 統一シンボル → ベンダー固有シンボル
- アダプターパターンによる拡張可能な設計

**Rationale**: データ取得（受信）と注文発注（送信）の両方のユースケースに対応する。

### III. シンプルさ優先

80% のユースケースに最適化する。

- 複雑な要件は、ユーザーによるオーバーライドで対応
- 過度な抽象化・汎用化を避ける
- 「動くコード」を「美しいコード」より優先する
- YAGNI: 必要になるまで作らない

**Rationale**: シンプルなAPIは学習コストを下げ、採用障壁を低くする。

### IV. 標準準拠

業界標準に準拠した設計を採用する。

- 取引所コードは ISO 10383 (MIC) に準拠
- JSON Schema による型定義（marketschema との統一フォーマット）

**Rationale**: 標準準拠により、他システムとの統合が容易になる。

### V. 軽量コア

コアは最小限に留め、データソース固有の実装は外部に委譲する。

- **コアに含めるもの**:
  - シンボルフォーマット定義
  - パース・バリデーション機能
  - 基底アダプタークラス
  - アダプターレジストリ

- **コアに含めないもの**:
  - 個別ベンダー向けアダプター実装
  - マッピングデータ（各クライアントが自己管理）
  - データソース接続・認証処理

**Rationale**: コアを小さく保ちながらも、実用的なシンボル管理を支援する。

## Scope Definition

### In Scope

| カテゴリ | 内容 |
|---------|------|
| シンボルフォーマット | 株式、先物、オプションの統一形式 |
| パース・バリデーション | シンボル文字列の解析と検証 |
| 正規化 | 大文字変換、全角→半角変換、空白除去 |
| アダプター基盤 | BaseAdapter、AdapterRegistry |
| 限月フォーマット | 月次(`YYYYMM`)、週次(`YYYYMM-W`、Wは1-5)、日次(`YYYYMMDD`) |
| 対象市場 | 日本市場(XJPX)、米国市場(XNYS等)、ISO 10383準拠の全取引所 |

### Out of Scope

| カテゴリ | 理由 |
|---------|------|
| 個別ベンダーアダプター実装 | 各クライアントライブラリで実装 |
| マッピングデータ管理 | 各クライアントが自己管理 |
| 暗号資産・FX・債券フォーマット | 将来拡張（本バージョンのスコープ外） |
| 価格・数量データ | marketschema の担当領域 |
| データソース接続・認証 | 各クライアントライブラリで実装 |

## Compatibility Policy

セマンティックバージョニング（SemVer）を採用する。

### Version Number Semantics

| バージョン | 変更内容 |
|-----------|---------|
| MAJOR (x.0.0) | 破壊的変更（後方互換性なし） |
| MINOR (0.x.0) | 機能追加（後方互換性あり） |
| PATCH (0.0.x) | バグ修正（後方互換性あり） |

### Breaking Change Rules

- 破壊的変更はメジャーバージョンでのみ行う
- 非推奨化（deprecation）から削除まで最低1メジャーバージョンの猶予を設ける
- 破壊的変更は CHANGELOG に明記する

### Backward Compatible Changes

以下はマイナーバージョンで行える：

- 新しいオプショナルフィールドの追加
- 新しい資産クラスのサポート追加
- 新しいバリデーションルールの追加（既存を壊さない範囲で）
- 新しいアダプターメソッドの追加

## Defaults and Extensibility

「合理的なデフォルト」を提供しつつ、ユーザーによるオーバーライドを可能にする。

| 項目 | デフォルト | オーバーライド方法 |
|------|-----------|-------------------|
| 取引所コード（日本） | `XJPX`（統一） | アダプターでセグメントMIC使用可 |
| 未知シンボル | パススルー（警告付き） | Strict モードで例外に変更可 |
| 大文字変換 | 有効 | 正規化オプションで無効化可 |
| 全角→半角変換 | 有効 | 正規化オプションで無効化可 |
| 設定ディレクトリ | `~/.config/marketsymbol/` | 環境変数で変更可 |

## Development Workflow

Kent Beck の TDD（テスト駆動開発）サイクルに従う。

```
    ┌─────────────────────────────────────┐
    │                                     │
    ▼                                     │
┌───────┐     ┌───────┐     ┌──────────┐  │
│  Red  │────▶│ Green │────▶│ Refactor │──┘
└───────┘     └───────┘     └──────────┘
```

### Red（レッド）

失敗するテストを先に書く。

- 実装前にテストを書くことで、仕様を明確にする
- テストが失敗することを確認してから次へ進む

### Green（グリーン）

テストを通す最小限のコードを書く。

- 「動くコード」を最優先
- 完璧を目指さない。まず通すことに集中

### Refactor（リファクタ）

テストが通る状態を維持しながら、コードを改善する。

- 重複を排除
- 可読性を向上
- テストが壊れたら即座に修正

### TDD Application Scope

| 対象 | TDD適用 |
|------|---------|
| シンボルパーサー | 必須 |
| バリデーション | 必須 |
| 正規化関数 | 必須 |
| アダプター基盤 | 必須 |
| ユーティリティ関数 | 推奨 |

## Prohibited Practices

### 命名の揺れの禁止（Naming Consistency）

同一の概念に対して異なる名前を付けてはならない。

```python
# NG: 同じデータに異なる名前
class Symbol:
    exchange: str      # ある場所では exchange
    mic: str           # 別の場所では mic
    market: str        # さらに別の場所では market

# OK: 統一された命名
class Symbol:
    exchange: str      # 取引所コードは常に exchange
```

**原則:**

- プロジェクト全体で同一概念には同一名称を使用する
- 命名規則は用語集（Glossary）で定義する
- 新しいフィールドを追加する前に、既存の命名を確認する

**確立された命名:**

| 概念 | 標準名 | 根拠 |
|------|--------|------|
| 取引所コード | `exchange` | ISO 10383 MIC を表す |
| 証券/商品コード | `code` | シンボルの識別部分 |
| 限月 | `expiry` | 先物・オプションの満期 |
| オプション種別 | `option_type` | C/P/O の区別 |
| 権利行使価格 | `strike` | 業界標準名 |
| 資産クラス | `asset_class` | equity/future/option |

### 暗黙的フォールバックの禁止

エラーを握りつぶしてデフォルト値で処理してはならない。

```python
# NG: 暗黙的フォールバック
def parse_symbol(raw: str) -> Symbol:
    try:
        return _parse(raw)
    except:
        return Symbol(exchange="UNKNOWN", code=raw)  # エラーを隠蔽

# OK: 明示的なエラー
def parse_symbol(raw: str) -> Symbol:
    try:
        return _parse(raw)
    except ParseError as e:
        raise SymbolParseError(f"Cannot parse symbol: {raw!r}") from e

# OK: 明示的なオプション
def parse_symbol_or_none(raw: str) -> Symbol | None:
    """None を返す可能性があることが明示されている"""
    try:
        return _parse(raw)
    except ParseError:
        return None
```

**原則:**

- 失敗は明示的に報告する
- デフォルト値を返す設計の場合は、関数名・型で明示する
- 例外をキャッチする場合は、具体的な例外型を指定する

### ハードコードの禁止

マジックナンバーや固定値をコードに埋め込んではならない。

```python
# NG: ハードコード
def validate_exchange(code: str) -> bool:
    return len(code) == 4  # なぜ 4 なのか不明

# OK: 定数として定義
MIC_LENGTH = 4  # ISO 10383 MIC code length

def validate_exchange(code: str) -> bool:
    return len(code) == MIC_LENGTH
```

**原則:**

- 数値・文字列リテラルには名前を付ける
- 設定値は引数または設定ファイルで外部化する
- 例外: `0`, `1`, `""`, `None` など自明なリテラルは許容

## Quality Standards

### Symbol Format

- 全資産クラスで先頭に取引所コード（ISO 10383 MIC）を配置
- コロン `:` を区切り文字として使用
- 大文字英数字とハイフンのみ使用

### Code

- 各言語のイディオム・規約に従う
- 型ヒント / 型注釈を必須とする
- エラーコードとメッセージを明確に定義

### Adapter

- BaseAdapter を継承して実装
- サポートする資産クラスを明示的に宣言
- 変換失敗は明確なエラーで報告

### Validation

- 形式エラー（セグメント数、文字種）を検出
- 論理エラー（無効な限月、矛盾する組み合わせ）を検出
- エラーコード（E001-E007）を伴う明確なメッセージを返す

## Priority of Principles

設計判断で迷った場合、以下の優先順位に従う：

1. **正確性** - シンボルが正しくパース・変換されること
2. **シンプルさ** - 理解しやすく、使いやすいこと
3. **互換性** - 既存コードを壊さないこと
4. **独立性** - 外部依存を最小化すること
5. **拡張性** - 新しいベンダー・資産クラスに対応できること

## Governance

### Amendment Procedure

1. 変更提案は Issue または PR で提出する
2. 変更理由と影響範囲を明記する
3. レビューを経て承認後、憲法を更新する
4. 更新後は依存ドキュメント（テンプレート等）も同期する

### Versioning Policy

憲法のバージョニングは SemVer に従う：

- **MAJOR**: 原則の削除、非互換な再定義
- **MINOR**: 新しい原則・セクションの追加、大幅な拡張
- **PATCH**: 文言修正、タイポ修正、非意味的な改善

### Compliance Review

- すべての PR/レビューは憲法への準拠を確認する
- 複雑さを追加する場合は正当化が必要
- 原則に違反する場合は、明示的な例外として文書化する

**Version**: 1.0.2 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-05
