"""ベンダーアダプター基盤.

BaseAdapter 抽象基底クラスと AdapterRegistry を提供する。
カスタムベンダーアダプターの実装と登録を可能にする。

Example:
    >>> from marketsymbol.adapter import BaseAdapter, AdapterRegistry
    >>> from marketsymbol import EquitySymbol, AssetClass
    >>>
    >>> class MyAdapter(BaseAdapter):
    ...     @property
    ...     def supported_asset_classes(self):
    ...         return frozenset({AssetClass.EQUITY})
    ...     def to_symbol(self, vendor_symbol):
    ...         code, _ = vendor_symbol.split(".")
    ...         return EquitySymbol(exchange="XJPX", code=code)
    ...     def from_symbol(self, symbol):
    ...         return f"{symbol.code}.T"
    >>>
    >>> registry = AdapterRegistry()
    >>> registry.register("my", MyAdapter())
    >>> adapter = registry.get("my")
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from marketsymbol.enums import AssetClass
    from marketsymbol.symbol import Symbol


class BaseAdapter(ABC):
    """ベンダーアダプター抽象基底クラス.

    ベンダー固有シンボルと統一シンボル間の双方向変換を提供する。
    サブクラスは以下の3つのメソッド/プロパティを実装する必要がある:

    - to_symbol: ベンダー固有シンボルを統一シンボルに変換
    - from_symbol: 統一シンボルをベンダー固有シンボルに変換
    - supported_asset_classes: サポートする資産クラスの集合
    """

    @abstractmethod
    def to_symbol(self, vendor_symbol: str) -> Symbol:
        """ベンダー固有シンボルを統一シンボルに変換.

        Args:
            vendor_symbol: ベンダー固有のシンボル文字列

        Returns:
            統一シンボルオブジェクト

        Raises:
            ValueError: 変換できない形式の場合
        """
        ...

    @abstractmethod
    def from_symbol(self, symbol: Symbol) -> str:
        """統一シンボルをベンダー固有シンボルに変換.

        Args:
            symbol: 統一シンボルオブジェクト

        Returns:
            ベンダー固有のシンボル文字列

        Raises:
            ValueError: 変換できないシンボルの場合
            TypeError: シンボルの資産クラスが supported_asset_classes に
                含まれない場合
        """
        ...

    @property
    @abstractmethod
    def supported_asset_classes(self) -> frozenset[AssetClass]:
        """サポートする資産クラスを返す.

        Returns:
            サポートする資産クラスの frozenset
        """
        ...


class AdapterRegistry:
    """スレッドセーフなアダプターレジストリ.

    Copy-on-Write パターンを使用し、読み取り操作はロックフリーで高速に行える。
    書き込み操作のみロックを取得する。

    Example:
        >>> from marketsymbol.adapter import AdapterRegistry, BaseAdapter
        >>> from marketsymbol import EquitySymbol, AssetClass
        >>>
        >>> class MyAdapter(BaseAdapter):
        ...     @property
        ...     def supported_asset_classes(self):
        ...         return frozenset({AssetClass.EQUITY})
        ...     def to_symbol(self, vendor_symbol):
        ...         code, _ = vendor_symbol.split(".")
        ...         return EquitySymbol(exchange="XJPX", code=code)
        ...     def from_symbol(self, symbol):
        ...         return f"{symbol.code}.T"
        >>>
        >>> registry = AdapterRegistry()
        >>> registry.register("my", MyAdapter())
        >>> adapter = registry.get("my")
        >>> vendors = registry.list()
    """

    def __init__(self) -> None:
        """レジストリを初期化."""
        self._lock = threading.Lock()
        self._adapters: dict[str, BaseAdapter] = {}

    def register(self, vendor: str, adapter: BaseAdapter) -> None:
        """アダプターを登録.

        Args:
            vendor: ベンダー識別名
            adapter: 登録するアダプターインスタンス

        Raises:
            ValueError: ベンダー名が空または空白のみ、
                または同じベンダー名が既に登録されている場合
        """
        if not vendor or not vendor.strip():
            msg = "Vendor name cannot be empty or whitespace"
            raise ValueError(msg)
        with self._lock:
            if vendor in self._adapters:
                msg = f"Adapter for '{vendor}' already registered"
                raise ValueError(msg)
            new_adapters = self._adapters.copy()
            new_adapters[vendor] = adapter
            self._adapters = new_adapters

    def get(self, vendor: str) -> BaseAdapter | None:
        """アダプターを取得.

        ロックフリーで高速に取得できる。

        Args:
            vendor: ベンダー識別名

        Returns:
            登録されているアダプター、または未登録の場合は None
        """
        return self._adapters.get(vendor)

    def list(self) -> list[str]:
        """登録済みベンダー名一覧を取得.

        Returns:
            登録されているベンダー名のリスト
        """
        return list(self._adapters.keys())

    def get_or_raise(self, vendor: str) -> BaseAdapter:
        """アダプターを取得 (未登録時はエラー).

        ロックフリーで高速に取得できる。

        Args:
            vendor: ベンダー識別名

        Returns:
            登録されているアダプター

        Raises:
            KeyError: ベンダーが未登録の場合
        """
        adapter = self._adapters.get(vendor)
        if adapter is None:
            msg = f"No adapter registered for '{vendor}'"
            raise KeyError(msg)
        return adapter
