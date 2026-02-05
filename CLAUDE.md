# CLAUDE.md

## Documentation

ドキュメントのルールは `.claude/docs.md` に従ってください。

### ドキュメントビルド

```bash
make -C docs html  # Sphinx HTML ドキュメント生成
```

出力先: `docs/_build/html/`

## Constitution

プロジェクトの詳細な原則は `.specify/memory/constitution.md` を参照してください。

## Python使用ルール

- システムの`python3`コマンドを直接使用しないこと
- このプロジェクトでは`--directory`オプションを付けてuvを使用する:
  ```bash
  # プロジェクトルートにいる場合（推奨）
  uv --directory ./python run python
  uv --directory ./python run pytest

  # カレントディレクトリが異なる場合
  uv --directory $PROJECT_ROOT/python run python
  uv --directory $PROJECT_ROOT/python run pytest
  ```
- 可能な限りプロジェクトルートで作業し、相対パス（`./python`）を使用すること

## Coding Rules

### 命名規則

- 同一概念には同一名称を使用（`qty` と `quantity` の混在禁止）
- 業界標準名を採用（下表参照）

| 概念 | 標準名 |
|------|--------|
| 取引所コード | `exchange` |
| 証券/商品コード | `code` |
| 限月 | `expiry` |
| オプション種別 | `option_type` |
| 権利行使価格 | `strike` |
| 資産クラス | `asset_class` |

新規フィールド追加時は [ADR](docs/adr/index.md) で決定プロセスを踏む。

### 禁止事項

1. **暗黙的フォールバック禁止**: エラーを握りつぶしてデフォルト値で処理しない
   ```python
   # NG
   except: return Symbol(exchange="UNKNOWN", code=raw)
   # OK
   except ParseError as e: raise SymbolParseError(...) from e
   ```

2. **ハードコード禁止**: マジックナンバーには名前を付ける
   ```python
   # NG
   return len(code) == 4
   # OK
   MIC_LENGTH = 4  # ISO 10383 MIC code length
   return len(code) == MIC_LENGTH
   ```

3. **一時ファイルの配置**: 一時的なスクリプト、デバッグ出力、手動テスト用の一時ファイルはプロジェクトルートや新規ディレクトリを作成せず、`ai_working/` に配置する（`ai_working/` は `.gitignore` に含まれているためコミットされない）
   ```
   # NG
   <project-root>/test_script.py
   <project-root>/debug/output.txt

   # OK
   <project-root>/ai_working/test_script.py
   <project-root>/ai_working/output.txt
   ```

### Quality Standards

- 型ヒント / 型注釈は必須
- JSON Schema のフィールドには必ず `description` を記述
- 自動生成コードは手動編集しない

### Quality Checks

コミット前に以下のチェックがすべて通ることを確認すること：

```bash
uv --directory ./python run ruff check .      # リンター
uv --directory ./python run ruff format --check .  # フォーマッター
uv --directory ./python run mypy src          # 型チェック
uv --directory ./python run pytest            # テスト
```

### 判断の優先順位

1. 正確性 → 2. シンプルさ → 3. 互換性 → 4. 独立性 → 5. 拡張性

## Development Workflow

TDD サイクル（Red → Green → Refactor）に従う。シンボルパーサー、バリデーション、正規化関数、アダプター基盤は TDD 必須。

## Active Technologies

- Python 3.13, Rust (latest stable)
