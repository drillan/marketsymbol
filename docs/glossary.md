# 用語集

marketsymbol ドキュメント全体で使用される主要な用語を定義します。

```{glossary}
シンボル (Symbol)
    金融市場商品の標準化された識別子。`EquitySymbol`、`FutureSymbol`、`OptionSymbol` のいずれか。

マーケット (Market)
    金融商品が取引される取引所や取引場所。

商品 (Instrument)
    株式、先物、オプション、通貨などの取引可能な資産。

取引所コード (exchange)
    ISO 10383 MIC (Market Identifier Code)。4文字の英大文字で取引所を識別する。例: `XJPX`（日本取引所グループ）。

証券コード (code)
    個別の金融商品を識別するコード。株式では銘柄コード、デリバティブでは商品コード。1-10文字の英数字。

限月 (expiry)
    デリバティブ商品の満期日。`YYYYMMDD` 形式の8桁数字で表現。例: `20250314`。

オプション種別 (option_type)
    オプションの種類。コール (`C`)、プット (`P`)、またはシリーズ (`O`) のいずれか。

権利行使価格 (strike)
    オプションの権利行使価格。正の整数で表現。コール/プットオプションでは必須。

資産クラス (AssetClass)
    金融商品の大分類。`EQUITY`（株式）、`FUTURE`（先物）、`OPTION`（オプション）のいずれか。

アダプター (Adapter)
    ベンダー固有のシンボルフォーマットと統一シンボル間の変換を行うコンポーネント。

MIC
    Market Identifier Code。ISO 10383 で定義された取引所識別コード。

SQ
    Special Quotation。特別清算指数。オプション・先物の最終決済に使用される指数。
```
