"""AssetClass, OptionType 列挙型のテスト."""

import pytest

from marketsymbol.enums import AssetClass, OptionType


class TestAssetClass:
    """AssetClass 列挙型のテスト."""

    def test_equity_value(self) -> None:
        """EQUITY の値が 'equity' であることを検証."""
        assert AssetClass.EQUITY.value == "equity"

    def test_future_value(self) -> None:
        """FUTURE の値が 'future' であることを検証."""
        assert AssetClass.FUTURE.value == "future"

    def test_option_value(self) -> None:
        """OPTION の値が 'option' であることを検証."""
        assert AssetClass.OPTION.value == "option"

    def test_member_count(self) -> None:
        """AssetClass は 3 つのメンバーを持つ."""
        assert len(AssetClass) == 3

    def test_all_members_accessible(self) -> None:
        """全メンバーにアクセス可能であることを検証."""
        members = [AssetClass.EQUITY, AssetClass.FUTURE, AssetClass.OPTION]
        assert len(members) == 3

    def test_from_value_equity(self) -> None:
        """値 'equity' から AssetClass.EQUITY を取得できる."""
        assert AssetClass("equity") == AssetClass.EQUITY

    def test_from_value_future(self) -> None:
        """値 'future' から AssetClass.FUTURE を取得できる."""
        assert AssetClass("future") == AssetClass.FUTURE

    def test_from_value_option(self) -> None:
        """値 'option' から AssetClass.OPTION を取得できる."""
        assert AssetClass("option") == AssetClass.OPTION

    def test_invalid_value_raises(self) -> None:
        """無効な値で ValueError が発生する."""
        with pytest.raises(ValueError):
            AssetClass("invalid")


class TestOptionType:
    """OptionType 列挙型のテスト."""

    def test_call_value(self) -> None:
        """CALL の値が 'C' であることを検証."""
        assert OptionType.CALL.value == "C"

    def test_put_value(self) -> None:
        """PUT の値が 'P' であることを検証."""
        assert OptionType.PUT.value == "P"

    def test_series_value(self) -> None:
        """SERIES の値が 'O' であることを検証 (シリーズ識別用)."""
        assert OptionType.SERIES.value == "O"

    def test_member_count(self) -> None:
        """OptionType は 3 つのメンバーを持つ."""
        assert len(OptionType) == 3

    def test_from_value_call(self) -> None:
        """値 'C' から OptionType.CALL を取得できる."""
        assert OptionType("C") == OptionType.CALL

    def test_from_value_put(self) -> None:
        """値 'P' から OptionType.PUT を取得できる."""
        assert OptionType("P") == OptionType.PUT

    def test_from_value_series(self) -> None:
        """値 'O' から OptionType.SERIES を取得できる."""
        assert OptionType("O") == OptionType.SERIES

    def test_invalid_value_raises(self) -> None:
        """無効な値で ValueError が発生する."""
        with pytest.raises(ValueError):
            OptionType("X")
