# ADR-001: シンボル仕様

| フィールド | 値 |
|-----------|-----|
| Status | Draft |
| Date | 2026-02-05 |
| Issue | [#1](https://github.com/drillan/marketsymbol/issues/1) |

## Context

marketsymbol プロジェクトでは、金融市場の商品（株式、先物、オプション、通貨など）を
一意に識別するための標準化されたシンボルフォーマットを定義する必要がある。

### 背景

- market-hub エコシステムには銘柄コード定義ライブラリが存在しない
- 複数のデータソース（JPX、Yahoo Finance、Bloomberg、証券会社API等）が異なるシンボル体系を使用
- marketschema の `Symbol` 型は単純な文字列で、フォーマット仕様がない
- derivatives-reaper には統一デリバティブコード仕様が存在する（参考実装）

### 目的

1. 複数ベンダーのシンボルを統一コードにマッピング
2. marketschema との連携（`symbol` フィールドで統一シンボルを使用）
3. 人間と機械の両方にとって扱いやすいフォーマット

### 設計原則

**marketsymbol は完全に独立して動作する**。market-hub への依存は不要。
market-hub がインストールされている場合、追加の統合管理機能が利用可能になる。

## Decision Drivers

- 複数の市場・取引所に対応する必要性
- 既存のシンボル体系との互換性
- 機械処理の容易さ
- 人間にとっての可読性
- derivatives-reaper 統一デリバティブコードとの一貫性
- Python / Rust 両対応
- **独立動作**: market-hub への依存なしで完全動作

## Considered Options

### 1. シンボルフォーマット

#### Option 1-A: 統一フォーマット（推奨）

全資産クラスで先頭に取引所コード（ISO 10383 MIC）を配置する。

**株式・ETF**:
```
[取引所]:[証券コード]
```

例：
- `XJPX:7203` - トヨタ自動車
- `XJPX:1306` - TOPIX連動型上場投資信託
- `XNYS:AAPL` - Apple（NYSE）

**デリバティブ（先物・オプション）**:
```
[取引所]:[商品コード]:[限月]:[種別][:権利行使価格]
```

例：
- `XJPX:NK:202503:F` - 日経225先物 2025年3月限
- `XJPX:NKM:202503:F` - 日経225mini先物 2025年3月限
- `XJPX:N225O:202503:C:42000` - 日経225オプション Call 42,000円
- `XJPX:N225MW:202501-2:P:39000` - 日経225ミニオプション 第2週限 Put 39,000円

**商品コード一覧**（derivatives-reaper準拠）:

| コード | 商品名 |
|--------|--------|
| NK | 日経225先物 |
| NKM | 日経225mini先物 |
| NKMI | 日経225マイクロ先物 |
| TP | TOPIX先物 |
| TPM | ミニTOPIX先物 |
| N225O | 日経225オプション |
| N225MW | 日経225ミニオプション |
| TPXO | TOPIXオプション |

**限月フォーマット**:

| 形式 | 例 | 用途 |
|------|-----|------|
| `YYYYMM` | 202503 | 標準月次限月 |
| `YYYYMM-W` | 202501-2 | 週次限月（第N週） |
| `YYYYMMDD` | 20250528 | 日次限月 |

**種別コード**:

| コード | 種別 |
|--------|------|
| F | 先物（Future） |
| C | コールオプション |
| P | プットオプション |
| O | オプション（Call/Put区別なし） |

#### Option 1-B: URN形式

```
urn:marketsymbol:[asset_class]:[exchange]:[code]
```

例：
- `urn:marketsymbol:equity:XJPX:7203`
- `urn:marketsymbol:future:XJPX:NK:202503`

#### Option 1-C: JSON構造体

```json
{"exchange": "XJPX", "code": "7203", "asset_class": "equity"}
```

### 2. マッピングの方向性

#### Option 2-A: 双方向マッピング（推奨）

- ベンダー固有 → 統一コード（正規化）
- 統一コード → ベンダー固有（逆引き）

```python
# 正規化
unified = normalize("7203.T", source="yahoo")  # -> "XJPX:7203"

# 逆引き
vendor = denormalize("XJPX:7203", target="yahoo")  # -> "7203.T"
```

#### Option 2-B: 単方向マッピング（正規化のみ）

逆引きが必要な場合は呼び出し側で管理。

### 3. マッピングデータの管理方法

#### Option 3-A: 静的定義（コード内）

```python
MAPPING = {
    "yahoo": {"7203.T": "XJPX:7203"},
    "bloomberg": {"7203 JP": "XJPX:7203"},
}
```

- メリット: 依存なし、シンプル
- デメリット: 編集にPython知識が必要、テスト必須

#### Option 3-B: JSON Schema + DuckDB + Parquet（推奨）

**アーキテクチャ**:

```
┌─────────────────────────────────────────────────────────────┐
│                      marketsymbol                            │
│                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  CRUD    │    │   DuckDB     │    │   Parquet    │       │
│  │  操作    │───▶│ (Interface)  │───▶│ (永続化)     │       │
│  │          │    │              │    │              │       │
│  └──────────┘    └──────────────┘    └──────────────┘       │
│       │                 │                    │              │
│       │                 ▼                    ▼              │
│       │          ┌──────────────┐    ┌──────────────┐       │
│       │          │ Transaction  │    │   配布用     │       │
│       │          │ (ACID保証)   │    │  (軽量)      │       │
│       │          └──────────────┘    └──────────────┘       │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────────────────┐       │
│  │              JSON Schema (型定義)                 │       │
│  │           marketschema と統一フォーマット          │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**役割分担**:

| コンポーネント | 役割 |
|--------------|------|
| JSON Schema | 型定義（marketschemaと統一） |
| DuckDB | CRUD操作インターフェース、トランザクション |
| Parquet | 永続化、配布、高速クエリ |

**スキーマ定義**: JSON Schema（marketschemaと統一）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SymbolMapping",
  "type": "object",
  "properties": {
    "unified_symbol": {"type": "string", "description": "統一シンボル"},
    "source": {"type": "string", "description": "データソース識別子"},
    "vendor_symbol": {"type": "string", "description": "ベンダー固有シンボル"},
    "name": {"type": "string", "description": "銘柄名"},
    "isin": {"type": ["string", "null"], "description": "ISIN コード"}
  },
  "required": ["unified_symbol", "source", "vendor_symbol"]
}
```

**DuckDB テーブル定義**:

```sql
CREATE TABLE symbols (
    unified_symbol VARCHAR NOT NULL,
    source VARCHAR NOT NULL,
    vendor_symbol VARCHAR NOT NULL,
    name VARCHAR,
    isin VARCHAR,
    PRIMARY KEY (unified_symbol, source)
);

-- インデックス（逆引き用）
CREATE INDEX idx_vendor ON symbols (source, vendor_symbol);
```

**メリット**:

- CRUD操作が可能（Parquet単体では不可）
- SQLによる柔軟なクエリ
- DuckDBがParquetを直接読み書き可能
- トランザクション（ACID）保証
- 高圧縮（Zstd）、高速クエリ（列指向、SIMD最適化）
- Python（duckdb）と Rust（duckdb-rs）両対応
- JSON Schema による型検証（marketschemaと統一）
- Parquet配布で軽量（DuckDB依存なしで読み込み可能）

**デメリット**:

- DuckDB依存（ただしParquet配布時は不要）
- インメモリ使用時のメモリ消費

#### Option 3-C: フルデータベース（PostgreSQL等）

動的更新が必要な大規模環境向け。

- メリット: リアルタイム更新、複雑なクエリ、レプリケーション
- デメリット: インフラ依存、接続管理、運用コスト

### 4. 未知シンボルの扱い

#### Option 4-A: エラーにする（Strict）

```python
normalize("UNKNOWN", source="yahoo")  # raises UnknownSymbolError
```

#### Option 4-B: パススルー（Permissive）（推奨）

```python
normalize("UNKNOWN", source="yahoo")  # -> "UNKNOWN" (そのまま返す)
```

#### Option 4-C: 警告付きパススルー

```python
normalize("UNKNOWN", source="yahoo")  # -> "UNKNOWN" + warning logged
```

### 5. 設定・データディレクトリ

#### Option 5-A: 独立ディレクトリ + market-hub オプショナル統合（推奨）

**marketsymbol 単独使用時**:

```
~/.config/marketsymbol/
└── config.toml                    # 設定ファイル

~/.local/share/marketsymbol/
├── symbols.duckdb                 # DuckDB（CRUD操作用）
└── symbols.parquet                # Parquet（読み取り専用）
```

**market-hub 統合管理時**（オプショナル）:

```
~/.config/market-hub/
├── config.toml                    # 共通設定
└── marketsymbol.toml              # オーバーライド設定

~/.local/share/market-hub/
└── marketsymbol/
    ├── symbols.duckdb
    └── symbols.parquet
```

**設定読み込みの優先順位**（低 → 高）:

1. `~/.config/marketsymbol/config.toml` （独自設定）
2. `~/.config/market-hub/config.toml` （共通設定、存在時のみ）
3. `~/.config/market-hub/marketsymbol.toml` （オーバーライド、存在時のみ）
4. `./marketsymbol.toml` （カレントディレクトリ）
5. 環境変数 (`MARKETSYMBOL_*`)

**データディレクトリの決定ロジック**:

```python
def get_data_dir() -> Path:
    """データディレクトリを取得"""
    # 1. 環境変数で明示指定
    if env := os.environ.get("MARKETSYMBOL_DATA_DIR"):
        return Path(env)

    # 2. market-hub ディレクトリが存在すれば使用
    hub_data = Path.home() / ".local" / "share" / "market-hub" / "marketsymbol"
    if hub_data.exists():
        return hub_data

    # 3. 独自ディレクトリ
    return Path.home() / ".local" / "share" / "marketsymbol"
```

### 6. 取引所コードの扱い（日本市場）

#### Option 6-A: XJPX統一（推奨）

日本市場は東証（XTKS）、名証（XNGO）、福証（XFKA）、札証（XSAP）に重複上場が存在するが、
流動性は東証が圧倒的（99%以上）であるため、日本市場は `XJPX`（Japan Exchange Group）で統一する。

```
XJPX:7203            # トヨタ自動車（東証として扱う）
XJPX:NK:202503:F     # 日経225先物
```

- メリット: シンプル、実用的
- デメリット: 名証/福証/札証の価格を区別できない

#### Option 6-B: セグメントMIC使用

取引所ごとにセグメントMICを使用。

```
XTKS:7203            # トヨタ自動車（東証）
XNGO:7203            # トヨタ自動車（名証）
XOSE:NK:202503:F     # 日経225先物（大証）
```

- メリット: 厳密
- デメリット: 複雑、ユースケースが限定的

#### Option 6-C: 短縮形

```
JPX:7203
JPX:NK:202503:F
```

- メリット: 可読性
- デメリット: ISO非準拠

### 7. derivatives-reaper との互換性

#### Option 7-A: マッピング変換（推奨）

derivatives-reaper の統一デリバティブコード（取引所コードなし）と marketsymbol の統一シンボル（取引所コードあり）は相互変換可能。

```python
# derivatives-reaper → marketsymbol
"NK:202503:F" → "XJPX:NK:202503:F"

# marketsymbol → derivatives-reaper
"XJPX:NK:202503:F" → "NK:202503:F"
```

変換関数:
```python
def to_marketsymbol(deriv_code: str, exchange: str = "XJPX") -> str:
    """derivatives-reaper形式 → marketsymbol形式"""
    return f"{exchange}:{deriv_code}"

def to_derivatives_reaper(symbol: str) -> str:
    """marketsymbol形式 → derivatives-reaper形式"""
    parts = symbol.split(":", 1)
    return parts[1] if len(parts) > 1 else symbol
```

### 8. マッピングデータの登録責務

#### Option 8-A: 各クライアントが自己管理（推奨）

各クライアントライブラリ（jpx-client, sbi-client 等）が、自分のデータソースのマッピングを登録する責務を持つ。

```python
# jpx_client/__init__.py
from marketsymbol import SymbolRegistry

def _register_jpx_mappings():
    """jpx-client 初期化時にマッピングを登録"""
    registry = SymbolRegistry()
    registry.register_batch("jpx", [
        {"unified": "XJPX:7203", "vendor": "7203", "name": "トヨタ自動車"},
        {"unified": "XJPX:NK:202503:F", "vendor": "NK225F_202503", "name": "日経225先物"},
        # ...
    ])

# 初回インポート時に登録
_register_jpx_mappings()
```

**メリット**:

- 各クライアントは自分のドメイン知識を持つ
- リリースサイクルが独立
- marketsymbol は軽量なまま維持
- 新しいベンダー追加時に marketsymbol の変更不要

#### Option 8-B: marketsymbol が一元管理

marketsymbol がすべてのマッピングデータを保持。

- デメリット: marketsymbol が肥大化、リリースサイクルが結合

## Decision

| 項目 | 選択 | 理由 |
|------|------|------|
| シンボルフォーマット | 1-A | 全資産クラスで先頭に取引所コード、derivatives-reaper商品コード採用 |
| マッピング方向 | 2-A | API呼び出し時に逆引きが必要 |
| データ管理 | 3-B | JSON Schema + DuckDB + Parquet: CRUD対応、型安全、高速、Python/Rust両対応 |
| 未知シンボル | 4-B または 4-C | 厳格すぎると使いにくい |
| ディレクトリ | 5-A | 独立動作 + market-hub オプショナル統合 |
| 取引所コード（日本） | 6-A | XJPX統一: 東証のみ対応、シンプル、実用的 |
| derivatives-reaper互換 | 7-A | マッピング変換関数で相互変換 |
| 登録責務 | 8-A | 各クライアントが自己管理 |

### 確定したシンボルフォーマット

| 資産クラス | フォーマット | 例 |
|-----------|-------------|-----|
| 株式 | `XJPX:[証券コード]` | `XJPX:7203` |
| ETF | `XJPX:[証券コード]` | `XJPX:1306` |
| 先物 | `XJPX:[商品]:[限月]:F` | `XJPX:NK:202503:F` |
| オプション | `XJPX:[商品]:[限月]:[C/P]:[行使価格]` | `XJPX:N225O:202503:C:42000` |
| 米国株 | `XNYS:[ティッカー]` | `XNYS:AAPL` |

## Consequences

### Positive

- 複数データソースを統一的に扱える
- marketschema との自然な連携（JSON Schema統一）
- derivatives-reaper との互換性
- Python / Rust 両方で高速なマッピング検索が可能
- Parquet の圧縮により配布サイズが小さい
- DuckDB による CRUD 操作とトランザクション保証
- Parquet 配布時は DuckDB 依存なしで読み込み可能
- **独立動作**: market-hub への依存なしで完全動作
- **オプショナル統合**: market-hub があれば追加機能が利用可能

### Negative

- マッピングデータの継続的なメンテナンスが必要
- 新規銘柄・上場廃止への追従コスト
- 開発時は DuckDB 依存
- 各クライアントに登録ロジックの実装が必要

### Neutral

- 取引所コードは ISO 10383 (MIC) に準拠
- 開発環境（DuckDB）と配布形式（Parquet）の分離
- 設定ディレクトリは `~/.config/marketsymbol/`（独立）または `~/.config/market-hub/`（統合）

## References

- [Issue #1: marketsymbol 初期設計・実装](https://github.com/drillan/marketsymbol/issues/1)
- [derivatives-reaper 統一デリバティブ管理コード仕様](https://github.com/drillan/derivatives-reaper/blob/main/docs/unified-derivative-code.md)
- [marketschema](https://github.com/drillan/marketschema)
- [markethub ADR-001: 共通設定管理](https://github.com/drillan/markethub/blob/main/docs/adr/001-config-management.md)
- [ISO 10383 Market Identifier Codes (MIC)](https://www.iso20022.org/market-identifier-codes)
- [Apache Parquet](https://parquet.apache.org/)
- [DuckDB](https://duckdb.org/)
- [DuckDB Python API](https://duckdb.org/docs/api/python/overview)
- [duckdb-rs (Rust)](https://docs.rs/duckdb/latest/duckdb/)
