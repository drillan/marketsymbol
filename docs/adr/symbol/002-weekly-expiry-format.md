# ADR-002: 限月フォーマットの統一

| フィールド | 値 |
|-----------|-----|
| Status | Accepted |
| Date | 2026-02-05 |
| Supersedes | ADR-001 の限月フォーマット部分 |

## Context

ADR-001 では限月フォーマットとして以下の3形式を定義した：

| 形式 | パターン | 例 | 用途 |
|------|---------|-----|------|
| 標準月次 | `YYYYMM` | 202503 | 標準月次限月 |
| 週次 | `YYYYMM-W` | 202501-2 | 週次限月（第N週） |
| 日次 | `YYYYMMDD` | 20250528 | 日次限月 |

### 問題点

#### 1. 週次限月の曖昧さ

日経225ミニオプションには**金曜限月**と**水曜限月**の2種類が存在する：

| 種類 | 説明 | 現行フォーマット |
|------|------|-----------------|
| 月次限月 | 第2金曜日SQ | `YYYYMM` |
| 週次金曜限月 | 毎週金曜日 | `YYYYMM-W` |
| 週次水曜限月 | 毎週水曜日 | `YYYYMMDD` |

`YYYYMM-W` 形式には以下の問題がある：

1. **同一週内の曖昧さ**: 2025年1月第2週には金曜（1/10）と水曜（1/8）の両方が存在。`202501-2` だけでは区別できない

2. **「第N週」の定義が不明確**:
   - 月の第N週なのか
   - SQ週（第2金曜を含む週）からの相対週なのか
   - 第1週の開始基準が曖昧

3. **逆算の必要性**: `202501-2` から実際の取引日を特定するには、カレンダー計算が必要

4. **暗黙ルールの問題**: 金曜は `YYYYMM-W`、水曜は `YYYYMMDD` と使い分ける慣習があるが、これは文書化されていない暗黙の規則

#### 2. 月次限月の曖昧さ

`YYYYMM` 形式にも問題がある：

1. **実際の満期日が不明**: 「202503」は2025年3月のいつを指すのか不明確（実際は第2金曜日 = 2025年3月14日）

2. **フォーマットの不統一**: 月次は6桁、週次/日次は8桁という分岐が必要

3. **カレンダー計算が必要**: `YYYYMM` から実際のSQ日を計算する処理が必要

## Decision Drivers

- 一意性：全ての限月が特定の日を指すこと
- シンプルさ：フォーマット判定ロジックが不要であること
- 拡張性：将来的に他の曜日や商品が追加されても対応可能
- 明確性：人間が満期日を直感的に理解できること

## Considered Options

### Option A: 全て YYYYMMDD に統一（採用）

全ての限月を具体的な日付形式で表現する。

```
# 月次限月（第2金曜日SQ）
XJPX:NK:20250314:F           # 2025年3月14日（第2金曜）
XJPX:N225O:20250314:C:42000  # 2025年3月14日 SQ

# 週次金曜限月
XJPX:N225MW:20250110:C:41000 # 2025年1月10日（金曜）

# 週次水曜限月
XJPX:N225MW:20250108:C:41000 # 2025年1月8日（水曜）
```

**メリット**:
- 全ての限月が一意に特定される
- フォーマット判定が不要（全て8桁）
- 満期日が明示的で曖昧さがない
- 将来的に他の曜日や商品が追加されても対応可能
- パース後のカレンダー計算が不要

**デメリット**:
- 既存の `YYYYMM` / `YYYYMM-W` 形式を使用するシステムとの乖離
- シンボル生成時にSQ日計算が必要
- 「2025年3月限」という業界慣習的な表現と乖離

### Option B: 月次は YYYYMM、週次/日次は YYYYMMDD

週次限月のみ統一し、月次は現状維持。

**メリット**:
- 月次限月の互換性維持
- 業界慣習との整合性

**デメリット**:
- フォーマット判定（6桁 vs 8桁）が必要
- 一貫性に欠ける

### Option C: 現状維持

3形式を維持。

**デメリット**:
- 週次限月の曖昧さが解決しない
- 暗黙ルールに依存

## Decision

**Option A: 全て YYYYMMDD に統一** を採用する。

### 変更後の限月フォーマット

| 形式 | パターン | 例 | 用途 |
|------|---------|-----|------|
| 統一形式 | `YYYYMMDD` | 20250314 | 全ての限月 |

### 正規表現

```
# 限月部分のパターン
^\d{8}$

# 8桁: 全ての限月 (YYYYMMDD)
```

### 実装例

```python
# 月次限月（SQ日を明示）
XJPX:NK:20250314:F           # 日経225先物 2025年3月限（3/14 SQ）
XJPX:NK:20250613:F           # 日経225先物 2025年6月限（6/13 SQ）
XJPX:N225O:20250314:C:42000  # 日経225オプション 2025年3月限

# 週次限月
XJPX:N225MW:20250110:C:41000 # 週次金曜（1/10）
XJPX:N225MW:20250108:C:41000 # 週次水曜（1/8）
XJPX:N225MW:20250528:C:41000 # 日次（5/28）
```

### 旧形式との関係

| 項目 | 旧形式 | marketsymbol | 備考 |
|------|--------|--------------|------|
| 月次限月 | `YYYYMM` | `YYYYMMDD` | **意図的な改善** |
| 週次金曜 | `YYYYMM-W` | `YYYYMMDD` | **意図的な改善** |
| 週次水曜 | `YYYYMMDD` | `YYYYMMDD` | 同一 |
| 日次 | `YYYYMMDD` | `YYYYMMDD` | 同一 |

marketsymbol は `YYYYMM` / `YYYYMM-W` 形式を**非推奨**とし、全て `YYYYMMDD` 形式に統一する。

### SQ日の取得

**SQ日（特別清算指数算出日）の取得は外部ライブラリ `marketsched` に委譲する。**

理由：
- SQ日はJPXの公式情報（https://www.jpx.co.jp/markets/derivatives/special-quotation/index.html）を一次情報とすべき
- 単純な「第2金曜日」計算では祝日による変更に対応できない
- カレンダー計算ロジックの重複を避け、責務を分離

```python
# marketsched を使用した SQ日取得（概念的なAPI）
from marketsched import get_sq_date

sq_date = get_sq_date(year=2025, month=3)  # -> date(2025, 3, 14)
```

### 変換関数（参考）

旧形式との相互変換が必要な場合の参考実装：

```python
from datetime import date
from marketsched import get_sq_date  # 外部ライブラリから取得

def convert_legacy_expiry(expiry: str) -> str:
    """旧限月形式を marketsymbol 形式に変換

    Args:
        expiry: "202503" or "202501-2" or "20250528"

    Returns:
        "20250314" or "20250110" or "20250528"

    Raises:
        ImportError: marketsched がインストールされていない場合
    """
    if len(expiry) == 6:
        # YYYYMM 形式 → SQ日に変換（marketsched から取得）
        year = int(expiry[:4])
        month = int(expiry[4:6])
        sq_date = get_sq_date(year, month)
        return sq_date.strftime("%Y%m%d")
    elif "-" in expiry:
        # YYYYMM-W 形式 → marketsched から週次限月日を取得
        parts = expiry.split("-")
        year = int(parts[0][:4])
        month = int(parts[0][4:6])
        week = int(parts[1])
        # marketsched の週次限月取得APIを使用
        from marketsched import get_weekly_expiry
        target_date = get_weekly_expiry(year, month, week)
        return target_date.strftime("%Y%m%d")
    else:
        # YYYYMMDD はそのまま
        return expiry

def convert_to_monthly_legacy(expiry: str) -> str:
    """marketsymbol 月次限月を旧形式に変換

    Args:
        expiry: "20250314" (SQ日)

    Returns:
        "202503"
    """
    # 日付から年月を抽出
    return expiry[:6]
```

### ユーティリティ関数

シンボル生成時に使用するSQ日取得ユーティリティ：

```python
def create_monthly_future(exchange: str, product: str, year: int, month: int) -> str:
    """月次先物シンボルを生成

    Args:
        exchange: 取引所コード (例: "XJPX")
        product: 商品コード (例: "NK")
        year: 年
        month: 月

    Returns:
        統一シンボル (例: "XJPX:NK:20250314:F")

    Raises:
        ImportError: marketsched がインストールされていない場合
    """
    from marketsched import get_sq_date
    sq_date = get_sq_date(year, month)
    expiry = sq_date.strftime("%Y%m%d")
    return f"{exchange}:{product}:{expiry}:F"

def create_monthly_option(
    exchange: str,
    product: str,
    year: int,
    month: int,
    option_type: str,
    strike: int,
) -> str:
    """月次オプションシンボルを生成

    Args:
        exchange: 取引所コード
        product: 商品コード
        year: 年
        month: 月
        option_type: "C" or "P"
        strike: 権利行使価格

    Returns:
        統一シンボル

    Raises:
        ImportError: marketsched がインストールされていない場合
    """
    from marketsched import get_sq_date
    sq_date = get_sq_date(year, month)
    expiry = sq_date.strftime("%Y%m%d")
    return f"{exchange}:{product}:{expiry}:{option_type}:{strike}"
```

## Consequences

### Positive

- 全ての限月が一意に識別可能
- フォーマット判定が不要（全て8桁）
- 満期日が明示的で曖昧さがない
- 曜日に依存しない拡張性
- パース後のカレンダー計算が不要
- 「第N週」の定義問題を回避

### Negative

- 既存の `YYYYMM` / `YYYYMM-W` 形式を使用するシステムとの互換性がない
- 「2025年3月限」「第2週限」という表現を使う人にとっては直感的でない
- 既存データは変換が必要
- SQ日取得に外部ライブラリ `marketsched` が必要（オプショナル依存）

### Neutral

- 変換関数を提供することで旧形式との相互運用は可能
- ADR-001 の限月フォーマット部分を本ADRで上書き
- SQ日取得は `marketsched` に委譲（責務分離）

## Dependencies

- **marketsched**: SQ日（特別清算指数算出日）の取得に使用。オプショナル依存として、インストールされていない場合はSQ日関連機能が無効化される

## References

- [ADR-001: シンボル仕様](./001-symbol-specification.md)
- [日経225ミニオプション - JPX](https://www.jpx.co.jp/derivatives/products/domestic/225mini-options/)
- [JPX SQ日一覧](https://www.jpx.co.jp/markets/derivatives/special-quotation/index.html)
