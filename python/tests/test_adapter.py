"""BaseAdapter と AdapterRegistry のテスト."""

from __future__ import annotations

import concurrent.futures
import threading
from typing import TYPE_CHECKING

import pytest

from marketsymbol import (
    AssetClass,
    EquitySymbol,
    FutureSymbol,
    OptionSymbol,
    OptionType,
)

if TYPE_CHECKING:
    from marketsymbol.adapter import BaseAdapter


class TestBaseAdapter:
    """BaseAdapter 抽象基底クラスのテスト."""

    def test_cannot_instantiate_directly(self) -> None:
        """BaseAdapter を直接インスタンス化できないことを確認."""
        from marketsymbol.adapter import BaseAdapter

        with pytest.raises(TypeError, match="abstract"):
            BaseAdapter()  # type: ignore[abstract]

    def test_subclass_must_implement_to_symbol(self) -> None:
        """to_symbol メソッドの実装が必要であることを確認."""
        from marketsymbol.adapter import BaseAdapter

        class IncompleteAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def from_symbol(
                self, _symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return ""

        with pytest.raises(TypeError, match="to_symbol"):
            IncompleteAdapter()  # type: ignore[abstract]

    def test_subclass_must_implement_from_symbol(self) -> None:
        """from_symbol メソッドの実装が必要であることを確認."""
        from marketsymbol.adapter import BaseAdapter

        class IncompleteAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, _vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                return EquitySymbol(exchange="XJPX", code="7203")

        with pytest.raises(TypeError, match="from_symbol"):
            IncompleteAdapter()  # type: ignore[abstract]

    def test_subclass_must_implement_supported_asset_classes(self) -> None:
        """supported_asset_classes プロパティの実装が必要であることを確認."""
        from marketsymbol.adapter import BaseAdapter

        class IncompleteAdapter(BaseAdapter):
            def to_symbol(
                self, _vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                return EquitySymbol(exchange="XJPX", code="7203")

            def from_symbol(
                self, _symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return ""

        with pytest.raises(TypeError, match="supported_asset_classes"):
            IncompleteAdapter()  # type: ignore[abstract]

    def test_complete_subclass_can_be_instantiated(self) -> None:
        """完全な実装を持つサブクラスはインスタンス化できることを確認."""
        from marketsymbol.adapter import BaseAdapter

        class CompleteAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, _vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                return EquitySymbol(exchange="XJPX", code="7203")

            def from_symbol(
                self, _symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return "7203.T"

        adapter = CompleteAdapter()
        assert adapter is not None

    def test_to_symbol_conversion(self) -> None:
        """to_symbol でベンダー固有シンボルを統一シンボルに変換できることを確認."""
        from marketsymbol.adapter import BaseAdapter

        class JpxAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                code, _ = vendor_symbol.split(".")
                return EquitySymbol(exchange="XJPX", code=code)

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return f"{symbol.code}.T"

        adapter = JpxAdapter()
        symbol = adapter.to_symbol("7203.T")

        assert isinstance(symbol, EquitySymbol)
        assert symbol.exchange == "XJPX"
        assert symbol.code == "7203"

    def test_from_symbol_conversion(self) -> None:
        """from_symbol で統一シンボルをベンダー固有シンボルに変換できることを確認."""
        from marketsymbol.adapter import BaseAdapter

        class JpxAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                code, _ = vendor_symbol.split(".")
                return EquitySymbol(exchange="XJPX", code=code)

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return f"{symbol.code}.T"

        adapter = JpxAdapter()
        symbol = EquitySymbol(exchange="XJPX", code="7203")
        vendor_symbol = adapter.from_symbol(symbol)

        assert vendor_symbol == "7203.T"

    def test_supported_asset_classes_returns_frozenset(self) -> None:
        """supported_asset_classes が frozenset を返すことを確認."""
        from marketsymbol.adapter import BaseAdapter

        class MultiAssetAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY, AssetClass.FUTURE})

            def to_symbol(
                self, _vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                return EquitySymbol(exchange="XJPX", code="7203")

            def from_symbol(
                self, _symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return ""

        adapter = MultiAssetAdapter()
        asset_classes = adapter.supported_asset_classes

        assert isinstance(asset_classes, frozenset)
        assert AssetClass.EQUITY in asset_classes
        assert AssetClass.FUTURE in asset_classes
        assert AssetClass.OPTION not in asset_classes

    def test_to_symbol_raises_valueerror_for_invalid_format(self) -> None:
        """無効な形式のベンダーシンボルで ValueError が発生することを確認."""
        from marketsymbol.adapter import BaseAdapter

        class StrictAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                if "." not in vendor_symbol:
                    msg = f"Invalid format: {vendor_symbol}"
                    raise ValueError(msg)
                code, suffix = vendor_symbol.split(".", 1)
                if suffix != "T":
                    msg = f"Unknown suffix: {suffix}"
                    raise ValueError(msg)
                return EquitySymbol(exchange="XJPX", code=code)

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return f"{symbol.code}.T"

        adapter = StrictAdapter()

        with pytest.raises(ValueError, match="Invalid format"):
            adapter.to_symbol("INVALID")

        with pytest.raises(ValueError, match="Unknown suffix"):
            adapter.to_symbol("7203.X")

    def test_from_symbol_raises_typeerror_for_unsupported_asset_class(self) -> None:
        """サポートしていない資産クラスで TypeError が発生することを確認."""
        from marketsymbol.adapter import BaseAdapter

        class EquityOnlyAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                code, _ = vendor_symbol.split(".")
                return EquitySymbol(exchange="XJPX", code=code)

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                if not isinstance(symbol, EquitySymbol):
                    msg = "Unsupported asset class"
                    raise TypeError(msg)
                return f"{symbol.code}.T"

        adapter = EquityOnlyAdapter()
        future_symbol = FutureSymbol(exchange="XJPX", code="NK", expiry="20250314")

        with pytest.raises(TypeError, match="Unsupported asset class"):
            adapter.from_symbol(future_symbol)

    def test_roundtrip_conversion(self) -> None:
        """to_symbol と from_symbol の変換が可逆であることを確認."""
        from marketsymbol.adapter import BaseAdapter

        class RoundtripAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                code, _ = vendor_symbol.split(".")
                return EquitySymbol(exchange="XJPX", code=code)

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return f"{symbol.code}.T"

        adapter = RoundtripAdapter()
        original_vendor_symbol = "7203.T"

        # vendor -> symbol -> vendor
        symbol = adapter.to_symbol(original_vendor_symbol)
        result = adapter.from_symbol(symbol)
        assert result == original_vendor_symbol

        # symbol -> vendor -> symbol
        original_symbol = EquitySymbol(exchange="XJPX", code="9984")
        vendor = adapter.from_symbol(original_symbol)
        result_symbol = adapter.to_symbol(vendor)
        assert result_symbol == original_symbol


class TestAdapterRegistry:
    """AdapterRegistry のテスト."""

    def _create_test_adapter(self) -> BaseAdapter:
        """テスト用アダプターを作成."""
        from marketsymbol.adapter import BaseAdapter

        class TestAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                code, _ = vendor_symbol.split(".")
                return EquitySymbol(exchange="XJPX", code=code)

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return f"{symbol.code}.T"

        return TestAdapter()

    def test_register_and_get_adapter(self) -> None:
        """アダプターを登録して取得できることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        adapter = self._create_test_adapter()

        registry.register("test", adapter)
        retrieved = registry.get("test")

        assert retrieved is adapter

    def test_get_returns_none_for_unknown_vendor(self) -> None:
        """未登録のベンダーに対して None を返すことを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        result = registry.get("unknown")

        assert result is None

    def test_list_returns_registered_vendor_names(self) -> None:
        """登録済みベンダー名の一覧を取得できることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        adapter1 = self._create_test_adapter()
        adapter2 = self._create_test_adapter()

        registry.register("vendor_a", adapter1)
        registry.register("vendor_b", adapter2)

        vendors = registry.list()

        assert "vendor_a" in vendors
        assert "vendor_b" in vendors
        assert len(vendors) == 2

    def test_list_returns_empty_for_new_registry(self) -> None:
        """新規レジストリでは空のリストを返すことを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        vendors = registry.list()

        assert vendors == []

    def test_register_duplicate_vendor_raises_error(self) -> None:
        """同じベンダー名での重複登録はエラーになることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        adapter1 = self._create_test_adapter()
        adapter2 = self._create_test_adapter()

        registry.register("test", adapter1)

        with pytest.raises(ValueError, match="already registered"):
            registry.register("test", adapter2)

    def test_register_empty_vendor_name_raises_error(self) -> None:
        """空のベンダー名での登録はエラーになることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        adapter = self._create_test_adapter()

        with pytest.raises(ValueError, match="empty"):
            registry.register("", adapter)

    def test_register_whitespace_vendor_name_raises_error(self) -> None:
        """空白のみのベンダー名での登録はエラーになることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        adapter = self._create_test_adapter()

        with pytest.raises(ValueError, match="empty"):
            registry.register("   ", adapter)

    def test_get_or_raise_returns_adapter(self) -> None:
        """get_or_raise が登録済みアダプターを返すことを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        adapter = self._create_test_adapter()
        registry.register("test", adapter)

        result = registry.get_or_raise("test")
        assert result is adapter

    def test_get_or_raise_raises_keyerror_for_unknown_vendor(self) -> None:
        """get_or_raise が未登録ベンダーで KeyError を発生させることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()

        with pytest.raises(KeyError, match="unknown"):
            registry.get_or_raise("unknown")

    def test_acceptance_criteria(self) -> None:
        """Issue #9 の受入条件を満たすことを確認."""
        from marketsymbol.adapter import AdapterRegistry, BaseAdapter

        class TestAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                code, _ = vendor_symbol.split(".")
                return EquitySymbol(exchange="XJPX", code=code)

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return f"{symbol.code}.T"

        registry = AdapterRegistry()
        registry.register("test", TestAdapter())
        adapter = registry.get("test")

        assert adapter is not None
        assert registry.get("unknown") is None
        assert "test" in registry.list()


class TestAdapterRegistryThreadSafety:
    """AdapterRegistry のスレッドセーフ性テスト."""

    def _create_test_adapter(self, name: str) -> BaseAdapter:
        """テスト用アダプターを作成."""
        from marketsymbol.adapter import BaseAdapter

        class TestAdapter(BaseAdapter):
            def __init__(self, adapter_name: str) -> None:
                self.name = adapter_name

            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.EQUITY})

            def to_symbol(
                self, _vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                return EquitySymbol(exchange="XJPX", code="7203")

            def from_symbol(
                self, _symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                return "7203.T"

        return TestAdapter(name)

    def test_concurrent_reads(self) -> None:
        """複数スレッドからの同時読み取りが安全であることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        adapter = self._create_test_adapter("test")
        registry.register("test", adapter)

        results: list[BaseAdapter | None] = []
        lock = threading.Lock()

        def read_adapter() -> None:
            result = registry.get("test")
            with lock:
                results.append(result)

        threads = [threading.Thread(target=read_adapter) for _ in range(100)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 100
        assert all(r is adapter for r in results)

    def test_concurrent_writes(self) -> None:
        """複数スレッドからの同時書き込みが安全であることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        errors: list[Exception] = []
        lock = threading.Lock()

        def register_adapter(name: str) -> None:
            try:
                adapter = self._create_test_adapter(name)
                registry.register(name, adapter)
            except ValueError:
                pass
            except Exception as e:
                with lock:
                    errors.append(e)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(register_adapter, f"vendor_{i}") for i in range(50)
            ]
            concurrent.futures.wait(futures)

        assert len(errors) == 0
        vendors = registry.list()
        assert len(vendors) == 50

    def test_concurrent_read_write(self) -> None:
        """読み取りと書き込みの同時実行が安全であることを確認."""
        from marketsymbol.adapter import AdapterRegistry

        registry = AdapterRegistry()
        errors: list[Exception] = []
        lock = threading.Lock()

        def writer(start: int) -> None:
            for i in range(start, start + 10):
                try:
                    adapter = self._create_test_adapter(f"vendor_{i}")
                    registry.register(f"vendor_{i}", adapter)
                except ValueError:
                    pass
                except Exception as e:
                    with lock:
                        errors.append(e)

        def reader() -> None:
            for _ in range(100):
                try:
                    registry.get("vendor_0")
                    registry.list()
                except Exception as e:
                    with lock:
                        errors.append(e)

        threads: list[threading.Thread] = []

        for i in range(5):
            threads.append(threading.Thread(target=writer, args=(i * 10,)))

        for _ in range(5):
            threads.append(threading.Thread(target=reader))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestAdapterWithMultipleAssetClasses:
    """複数の資産クラスをサポートするアダプターのテスト."""

    def test_adapter_with_futures(self) -> None:
        """先物シンボルを扱うアダプターのテスト."""
        from marketsymbol.adapter import BaseAdapter

        class FutureAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.FUTURE})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                parts = vendor_symbol.split("/")
                return FutureSymbol(exchange="XJPX", code=parts[0], expiry=parts[1])

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                if isinstance(symbol, FutureSymbol):
                    return f"{symbol.code}/{symbol.expiry}"
                msg = "Unsupported symbol type"
                raise TypeError(msg)

        adapter = FutureAdapter()
        symbol = adapter.to_symbol("NK/20250314")

        assert isinstance(symbol, FutureSymbol)
        assert symbol.exchange == "XJPX"
        assert symbol.code == "NK"
        assert symbol.expiry == "20250314"

        vendor_symbol = adapter.from_symbol(symbol)
        assert vendor_symbol == "NK/20250314"

    def test_adapter_with_options(self) -> None:
        """オプションシンボルを扱うアダプターのテスト."""
        from marketsymbol.adapter import BaseAdapter

        class OptionAdapter(BaseAdapter):
            @property
            def supported_asset_classes(self) -> frozenset[AssetClass]:
                return frozenset({AssetClass.OPTION})

            def to_symbol(
                self, vendor_symbol: str
            ) -> EquitySymbol | FutureSymbol | OptionSymbol:
                parts = vendor_symbol.split("/")
                return OptionSymbol(
                    exchange="XJPX",
                    code=parts[0],
                    expiry=parts[1],
                    option_type=OptionType.CALL if parts[2] == "C" else OptionType.PUT,
                    strike=int(parts[3]),
                )

            def from_symbol(
                self, symbol: EquitySymbol | FutureSymbol | OptionSymbol
            ) -> str:
                if isinstance(symbol, OptionSymbol):
                    return f"{symbol.code}/{symbol.expiry}/{symbol.option_type.value}/{symbol.strike}"
                msg = "Unsupported symbol type"
                raise TypeError(msg)

        adapter = OptionAdapter()
        symbol = adapter.to_symbol("N225O/20250314/C/42000")

        assert isinstance(symbol, OptionSymbol)
        assert symbol.exchange == "XJPX"
        assert symbol.code == "N225O"
        assert symbol.expiry == "20250314"
        assert symbol.option_type == OptionType.CALL
        assert symbol.strike == 42000

        vendor_symbol = adapter.from_symbol(symbol)
        assert vendor_symbol == "N225O/20250314/C/42000"
