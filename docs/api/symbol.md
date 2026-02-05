# シンボルクラス

金融商品を表現するシンボルクラス群。

## Symbol 型エイリアス

`Symbol` は `EquitySymbol | FutureSymbol | OptionSymbol` の型エイリアスです。

```{eval-rst}
.. py:data:: marketsymbol.Symbol

   シンボルクラスの Union 型。

   :type: type[EquitySymbol] | type[FutureSymbol] | type[OptionSymbol]
```

## EquitySymbol

株式・ETF シンボルを表現するクラス。

```{eval-rst}
.. autoclass:: marketsymbol.EquitySymbol
   :members:
   :special-members: __str__
   :undoc-members:
```

## FutureSymbol

先物シンボルを表現するクラス。

```{eval-rst}
.. autoclass:: marketsymbol.FutureSymbol
   :members:
   :special-members: __str__
   :undoc-members:
```

## OptionSymbol

オプションシンボルを表現するクラス。

```{eval-rst}
.. autoclass:: marketsymbol.OptionSymbol
   :members:
   :special-members: __str__
   :undoc-members:
```
