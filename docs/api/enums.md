# 列挙型

シンボル関連の列挙型定義。

## AssetClass

資産クラスを表す列挙型。

```{eval-rst}
.. autoclass:: marketsymbol.AssetClass
   :members:
   :undoc-members:
```

### 値

| 値 | 説明 |
|----|------|
| `EQUITY` | 株式・ETF |
| `FUTURE` | 先物 |
| `OPTION` | オプション |

## OptionType

オプション種別を表す列挙型。

```{eval-rst}
.. autoclass:: marketsymbol.OptionType
   :members:
   :undoc-members:
```

### 値

| 値 | 説明 |
|----|------|
| `CALL` | コールオプション |
| `PUT` | プットオプション |
| `SERIES` | シリーズ（権利行使価格なし） |
