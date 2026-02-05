"""Symbol クラスのテスト.

EquitySymbol, FutureSymbol, OptionSymbol の生成、str()、等価性、
ハッシュ、pickle をテストする。
"""

import pickle

import pytest

from marketsymbol.enums import AssetClass, OptionType
from marketsymbol.errors import ErrorCode, SymbolValidationError
from marketsymbol.symbol import (
    EquitySymbol,
    FutureSymbol,
    OptionSymbol,
    Symbol,
)


class TestEquitySymbol:
    """EquitySymbol のテスト."""

    def test_create_equity_symbol(self) -> None:
        """EquitySymbol を生成できる."""
        symbol = EquitySymbol(exchange="XJPX", code="7203")
        assert symbol.exchange == "XJPX"
        assert symbol.code == "7203"

    def test_asset_class_is_equity(self) -> None:
        """asset_class プロパティは EQUITY を返す."""
        symbol = EquitySymbol(exchange="XJPX", code="7203")
        assert symbol.asset_class == AssetClass.EQUITY

    def test_str_format(self) -> None:
        """__str__ は 'exchange:code' 形式を返す."""
        symbol = EquitySymbol(exchange="XJPX", code="7203")
        assert str(symbol) == "XJPX:7203"

    def test_equality(self) -> None:
        """同じ値を持つ EquitySymbol は等価."""
        symbol1 = EquitySymbol(exchange="XJPX", code="7203")
        symbol2 = EquitySymbol(exchange="XJPX", code="7203")
        assert symbol1 == symbol2

    def test_inequality_different_exchange(self) -> None:
        """異なる exchange を持つ EquitySymbol は等価でない."""
        symbol1 = EquitySymbol(exchange="XJPX", code="7203")
        symbol2 = EquitySymbol(exchange="XNAS", code="7203")
        assert symbol1 != symbol2

    def test_inequality_different_code(self) -> None:
        """異なる code を持つ EquitySymbol は等価でない."""
        symbol1 = EquitySymbol(exchange="XJPX", code="7203")
        symbol2 = EquitySymbol(exchange="XJPX", code="9984")
        assert symbol1 != symbol2

    def test_hash_consistency(self) -> None:
        """等価な EquitySymbol は同じハッシュ値を持つ."""
        symbol1 = EquitySymbol(exchange="XJPX", code="7203")
        symbol2 = EquitySymbol(exchange="XJPX", code="7203")
        assert hash(symbol1) == hash(symbol2)

    def test_usable_in_set(self) -> None:
        """EquitySymbol は set で使用できる."""
        symbol1 = EquitySymbol(exchange="XJPX", code="7203")
        symbol2 = EquitySymbol(exchange="XJPX", code="7203")
        symbol3 = EquitySymbol(exchange="XJPX", code="9984")
        symbol_set = {symbol1, symbol2, symbol3}
        assert len(symbol_set) == 2

    def test_usable_as_dict_key(self) -> None:
        """EquitySymbol は辞書のキーとして使用できる."""
        symbol = EquitySymbol(exchange="XJPX", code="7203")
        data: dict[EquitySymbol, str] = {symbol: "Toyota"}
        assert data[symbol] == "Toyota"

    def test_pickle_roundtrip(self) -> None:
        """EquitySymbol は pickle でシリアライズ/デシリアライズできる."""
        symbol = EquitySymbol(exchange="XJPX", code="7203")
        pickled = pickle.dumps(symbol)
        restored = pickle.loads(pickled)
        assert restored == symbol
        assert type(restored) is EquitySymbol

    def test_immutable(self) -> None:
        """EquitySymbol は frozen dataclass として変更不可."""
        symbol = EquitySymbol(exchange="XJPX", code="7203")
        with pytest.raises(AttributeError):
            symbol.exchange = "XNAS"  # type: ignore[misc]

    def test_post_init_invalid_exchange(self) -> None:
        """無効な exchange で EquitySymbol を生成すると E007 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            EquitySymbol(exchange="XX", code="7203")
        assert exc_info.value.error_code == ErrorCode.UNKNOWN_EXCHANGE

    def test_post_init_invalid_code_empty(self) -> None:
        """空の code で EquitySymbol を生成すると E008 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            EquitySymbol(exchange="XJPX", code="")
        assert exc_info.value.error_code == ErrorCode.INVALID_CODE

    def test_post_init_invalid_code_too_long(self) -> None:
        """code が長すぎると E008 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            EquitySymbol(exchange="XJPX", code="A" * 11)
        assert exc_info.value.error_code == ErrorCode.INVALID_CODE


class TestFutureSymbol:
    """FutureSymbol のテスト."""

    def test_create_future_symbol(self) -> None:
        """FutureSymbol を生成できる."""
        symbol = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        assert symbol.exchange == "XJPX"
        assert symbol.code == "NK"
        assert symbol.expiry == "20250314"

    def test_asset_class_is_future(self) -> None:
        """asset_class プロパティは FUTURE を返す."""
        symbol = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        assert symbol.asset_class == AssetClass.FUTURE

    def test_str_format(self) -> None:
        """__str__ は 'exchange:code:expiry:F' 形式を返す."""
        symbol = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        assert str(symbol) == "XJPX:NK:20250314:F"

    def test_equality(self) -> None:
        """同じ値を持つ FutureSymbol は等価."""
        symbol1 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        symbol2 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        assert symbol1 == symbol2

    def test_inequality_different_expiry(self) -> None:
        """異なる expiry を持つ FutureSymbol は等価でない."""
        symbol1 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        symbol2 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250614")
        assert symbol1 != symbol2

    def test_hash_consistency(self) -> None:
        """等価な FutureSymbol は同じハッシュ値を持つ."""
        symbol1 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        symbol2 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        assert hash(symbol1) == hash(symbol2)

    def test_usable_in_set(self) -> None:
        """FutureSymbol は set で使用できる."""
        symbol1 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        symbol2 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        symbol3 = FutureSymbol(exchange="XJPX", code="NK", expiry="20250614")
        symbol_set = {symbol1, symbol2, symbol3}
        assert len(symbol_set) == 2

    def test_pickle_roundtrip(self) -> None:
        """FutureSymbol は pickle でシリアライズ/デシリアライズできる."""
        symbol = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        pickled = pickle.dumps(symbol)
        restored = pickle.loads(pickled)
        assert restored == symbol
        assert type(restored) is FutureSymbol

    def test_immutable(self) -> None:
        """FutureSymbol は frozen dataclass として変更不可."""
        symbol = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        with pytest.raises(AttributeError):
            symbol.expiry = "20250614"  # type: ignore[misc]

    def test_post_init_invalid_expiry_format(self) -> None:
        """無効な expiry フォーマットで FutureSymbol を生成すると E003 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            FutureSymbol(exchange="XJPX", code="NK", expiry="2025031")
        assert exc_info.value.error_code == ErrorCode.INVALID_EXPIRY_FORMAT

    def test_post_init_invalid_expiry_date(self) -> None:
        """無効な日付で FutureSymbol を生成すると E005 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            FutureSymbol(exchange="XJPX", code="NK", expiry="20250230")
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE


class TestOptionSymbol:
    """OptionSymbol のテスト."""

    def test_create_call_option_symbol(self) -> None:
        """コールオプション OptionSymbol を生成できる."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        assert symbol.exchange == "XJPX"
        assert symbol.code == "NK"
        assert symbol.expiry == "20250314"
        assert symbol.option_type == OptionType.CALL
        assert symbol.strike == 40000

    def test_create_put_option_symbol(self) -> None:
        """プットオプション OptionSymbol を生成できる."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.PUT,
            strike=38000,
        )
        assert symbol.option_type == OptionType.PUT
        assert symbol.strike == 38000

    def test_create_series_option_symbol(self) -> None:
        """シリーズオプション OptionSymbol を生成できる (strike は None)."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.SERIES,
            strike=None,
        )
        assert symbol.option_type == OptionType.SERIES
        assert symbol.strike is None

    def test_asset_class_is_option(self) -> None:
        """asset_class プロパティは OPTION を返す."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        assert symbol.asset_class == AssetClass.OPTION

    def test_str_format_call(self) -> None:
        """コールオプションの __str__ は 'exchange:code:expiry:C:strike' 形式."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        assert str(symbol) == "XJPX:NK:20250314:C:40000"

    def test_str_format_put(self) -> None:
        """プットオプションの __str__ は 'exchange:code:expiry:P:strike' 形式."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.PUT,
            strike=38000,
        )
        assert str(symbol) == "XJPX:NK:20250314:P:38000"

    def test_str_format_series(self) -> None:
        """シリーズオプションの __str__ は 'exchange:code:expiry:O' 形式 (strike なし)."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.SERIES,
            strike=None,
        )
        assert str(symbol) == "XJPX:NK:20250314:O"

    def test_equality(self) -> None:
        """同じ値を持つ OptionSymbol は等価."""
        symbol1 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        symbol2 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        assert symbol1 == symbol2

    def test_inequality_different_strike(self) -> None:
        """異なる strike を持つ OptionSymbol は等価でない."""
        symbol1 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        symbol2 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=41000,
        )
        assert symbol1 != symbol2

    def test_inequality_different_option_type(self) -> None:
        """異なる option_type を持つ OptionSymbol は等価でない."""
        symbol1 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        symbol2 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.PUT,
            strike=40000,
        )
        assert symbol1 != symbol2

    def test_hash_consistency(self) -> None:
        """等価な OptionSymbol は同じハッシュ値を持つ."""
        symbol1 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        symbol2 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        assert hash(symbol1) == hash(symbol2)

    def test_usable_in_set(self) -> None:
        """OptionSymbol は set で使用できる."""
        symbol1 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        symbol2 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        symbol3 = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=41000,
        )
        symbol_set = {symbol1, symbol2, symbol3}
        assert len(symbol_set) == 2

    def test_pickle_roundtrip(self) -> None:
        """OptionSymbol は pickle でシリアライズ/デシリアライズできる."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        pickled = pickle.dumps(symbol)
        restored = pickle.loads(pickled)
        assert restored == symbol
        assert type(restored) is OptionSymbol

    def test_pickle_roundtrip_series(self) -> None:
        """シリーズオプションも pickle でシリアライズ/デシリアライズできる."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.SERIES,
            strike=None,
        )
        pickled = pickle.dumps(symbol)
        restored = pickle.loads(pickled)
        assert restored == symbol

    def test_immutable(self) -> None:
        """OptionSymbol は frozen dataclass として変更不可."""
        symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        with pytest.raises(AttributeError):
            symbol.strike = 41000  # type: ignore[misc]

    def test_post_init_call_without_strike(self) -> None:
        """CALL オプションに strike なしで生成すると E002 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            OptionSymbol(
                exchange="XJPX",
                code="NK",
                expiry="20250314",
                option_type=OptionType.CALL,
                strike=None,
            )
        assert exc_info.value.error_code == ErrorCode.OPTION_WITHOUT_STRIKE

    def test_post_init_put_without_strike(self) -> None:
        """PUT オプションに strike なしで生成すると E002 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            OptionSymbol(
                exchange="XJPX",
                code="NK",
                expiry="20250314",
                option_type=OptionType.PUT,
                strike=None,
            )
        assert exc_info.value.error_code == ErrorCode.OPTION_WITHOUT_STRIKE

    def test_post_init_series_with_strike(self) -> None:
        """SERIES オプションに strike ありで生成すると E001 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            OptionSymbol(
                exchange="XJPX",
                code="NK",
                expiry="20250314",
                option_type=OptionType.SERIES,
                strike=40000,
            )
        assert exc_info.value.error_code == ErrorCode.FUTURE_WITH_STRIKE

    def test_post_init_invalid_strike_zero(self) -> None:
        """strike が 0 で生成すると E009 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            OptionSymbol(
                exchange="XJPX",
                code="NK",
                expiry="20250314",
                option_type=OptionType.CALL,
                strike=0,
            )
        assert exc_info.value.error_code == ErrorCode.INVALID_STRIKE_VALUE

    def test_post_init_invalid_strike_negative(self) -> None:
        """負の strike で生成すると E009 エラーを発生する."""
        with pytest.raises(SymbolValidationError) as exc_info:
            OptionSymbol(
                exchange="XJPX",
                code="NK",
                expiry="20250314",
                option_type=OptionType.CALL,
                strike=-100,
            )
        assert exc_info.value.error_code == ErrorCode.INVALID_STRIKE_VALUE


class TestSymbolTypeAlias:
    """Symbol 型エイリアスのテスト."""

    def test_equity_is_symbol(self) -> None:
        """EquitySymbol は Symbol 型に含まれる."""
        symbol: Symbol = EquitySymbol(exchange="XJPX", code="7203")
        assert isinstance(symbol, EquitySymbol)

    def test_future_is_symbol(self) -> None:
        """FutureSymbol は Symbol 型に含まれる."""
        symbol: Symbol = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        assert isinstance(symbol, FutureSymbol)

    def test_option_is_symbol(self) -> None:
        """OptionSymbol は Symbol 型に含まれる."""
        symbol: Symbol = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        assert isinstance(symbol, OptionSymbol)

    def test_symbol_list_heterogeneous(self) -> None:
        """異なる Symbol 型を同じリストに格納できる."""
        symbols: list[Symbol] = [
            EquitySymbol(exchange="XJPX", code="7203"),
            FutureSymbol(exchange="XJPX", code="NK", expiry="20250314"),
            OptionSymbol(
                exchange="XJPX",
                code="NK",
                expiry="20250314",
                option_type=OptionType.CALL,
                strike=40000,
            ),
        ]
        assert len(symbols) == 3
        assert all(hasattr(s, "asset_class") for s in symbols)


class TestSymbolInequality:
    """異なる Symbol 型間の不等価性テスト."""

    def test_equity_not_equal_to_future(self) -> None:
        """EquitySymbol と FutureSymbol は等価でない."""
        equity = EquitySymbol(exchange="XJPX", code="NK")
        future = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        assert equity != future

    def test_equity_not_equal_to_option(self) -> None:
        """EquitySymbol と OptionSymbol は等価でない."""
        equity = EquitySymbol(exchange="XJPX", code="NK")
        option = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        assert equity != option

    def test_future_not_equal_to_option(self) -> None:
        """FutureSymbol と OptionSymbol は等価でない."""
        future = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        option = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.CALL,
            strike=40000,
        )
        assert future != option

    def test_different_symbol_types_in_set(self) -> None:
        """異なる Symbol 型は set で別々にカウントされる."""
        equity = EquitySymbol(exchange="XJPX", code="NK")
        future = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")
        option = OptionSymbol(
            exchange="XJPX",
            code="NK",
            expiry="20250314",
            option_type=OptionType.SERIES,
            strike=None,
        )
        symbol_set = {equity, future, option}
        assert len(symbol_set) == 3
