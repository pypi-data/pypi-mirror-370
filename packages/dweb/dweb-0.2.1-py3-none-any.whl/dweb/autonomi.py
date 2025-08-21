from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Union, Tuple

from autonomi_client import DataAddress

from . import network as network_mod
from importlib import import_module


_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="dweb-autonomi")


def _run_coro_in_thread(coro):
    def _runner():
        return asyncio.run(coro)

    return _executor.submit(_runner).result()


def get(
    address: Union[str, DataAddress],
    *,
    network: network_mod._Network = network_mod.mainnet,
    timeout: Optional[float] = None,
) -> bytes:
    """Synchronous wrapper around the async `get` API.

    Args:
        address: 64-hex data map address (string) or `DataAddress`.
        network: network selector (`network.mainnet` or `network.alpha`).
        timeout: optional timeout in seconds for the operation.
    """

    # Lazy import to allow monkeypatching in tests and avoid import cycles during startup
    async_api = import_module("dweb.aio.autonomi")
    coro = async_api.get(address, network=network)

    # If already in an event loop (e.g., Jupyter), we must not nest loops.
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        future = _executor.submit(lambda: asyncio.run(coro))
        return future.result(timeout=timeout)
    else:
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout) if timeout else coro)


def put(
    data: bytes,
    fee_limit_wei: Optional[int] = None,
    *,
    network: network_mod._Network = network_mod.mainnet,
    private: bool = False,
    timeout: Optional[float] = None,
) -> Tuple[float, str]:
    """Synchronous wrapper around the async `put` API.

    Args:
        data: raw bytes to upload.
        network: network selector.
        private: set True to perform private put (no datamap upload), default public.
        timeout: optional timeout in seconds.
    Returns:
        (cost_in_AUTONOMI as float, data_address_hex as str)
    """

    async_api = import_module("dweb.aio.autonomi")
    coro = async_api.put(data, fee_limit_wei, network=network, private=private)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        future = _executor.submit(lambda: asyncio.run(coro))
        return future.result(timeout=timeout)
    else:
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout) if timeout else coro)


def _sync_bridge(async_fn_name: str, *, network: network_mod._Network, timeout: Optional[float]) -> float:
    async_api = import_module("dweb.aio.autonomi")
    coro = getattr(async_api, async_fn_name)(network=network)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        future = _executor.submit(lambda: asyncio.run(coro))
        return future.result(timeout=timeout)
    else:
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout) if timeout else coro)


def get_balance(*, network: network_mod._Network = network_mod.mainnet, timeout: Optional[float] = None) -> float:
    """Return AUTONOMI token balance (sync)."""
    return _sync_bridge("balance", network=network, timeout=timeout)


def get_gas(*, network: network_mod._Network = network_mod.mainnet, timeout: Optional[float] = None) -> float:
    """Return ETH(Arb) balance (sync)."""
    return _sync_bridge("gas", network=network, timeout=timeout)


def get_wallet_address(*, network: network_mod._Network = network_mod.mainnet, timeout: Optional[float] = None) -> str:
    """Return wallet address (sync)."""
    async_api = import_module("dweb.aio.autonomi")
    coro = async_api.wallet_address(network=network)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        future = _executor.submit(lambda: asyncio.run(coro))
        return future.result(timeout=timeout)
    else:
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout) if timeout else coro)


def set_secret_key(secret_key: str) -> None:
    """Set process-wide SECRET_KEY override (sync wrapper)."""
    async_api = import_module("dweb.aio.autonomi")
    async_api.set_secret_key(secret_key)


def __getattr__(name: str):  # module-level properties: balance, gas
    if name == "balance":
        # expose as property-like access but calls the sync function
        return get_balance()
    if name == "gas":
        return get_gas()
    if name == "wallet":
        return get_wallet_address()
    raise AttributeError(name)
