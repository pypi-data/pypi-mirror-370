from __future__ import annotations

from typing import Optional, Union, Tuple, Dict

import os
import warnings
from pathlib import Path
from getpass import getpass
from decimal import Decimal
try:
    from dotenv import dotenv_values as _dotenv_values  # type: ignore
except Exception:  # pragma: no cover
    _dotenv_values = None  # type: ignore

from autonomi_client import (
    Client,
    DataAddress,
    Wallet,
    PaymentOption,
    TransactionConfig,
    MaxFeePerGas,
)

from .._client_manager import async_client_manager
from ..errors import InvalidAddressError
from .. import network as network_mod


def _address_from_hex_maybe(address: Union[str, DataAddress]) -> DataAddress:
    if isinstance(address, DataAddress):
        return address
    if isinstance(address, str):
        hex_str = address.lower()
        if hex_str.startswith("0x"):
            hex_str = hex_str[2:]
        if len(hex_str) != 64:
            raise InvalidAddressError(
                "Data map address must be 64 hex chars (with or without 0x prefix)."
            )
        try:
            return DataAddress.from_hex(hex_str)
        except Exception as exc:  # pragma: no cover - relies on upstream validation
            raise InvalidAddressError("Invalid data address hex string.") from exc
    raise InvalidAddressError("Unsupported address type.")


async def get(
    address: Union[str, DataAddress],
    *,
    network: network_mod._Network = network_mod.mainnet,
    client: Optional[Client] = None,
) -> bytes:
    """Fetch immutable public data by data map address.

    Args:
        address: 64-hex data map address (string) or `DataAddress`.
        network: network selector (`network.mainnet` or `network.alpha`). Defaults to mainnet.
        client: optional pre-initialized `autonomi_client.Client`.

    Returns:
        Raw bytes of the immutable data.
    """

    data_address = _address_from_hex_maybe(address)

    use_client: Client
    if client is not None:
        use_client = client
    else:
        use_client = await async_client_manager.get_client(alpha=(network is network_mod.alpha))

    return await use_client.data_get_public(data_address)


# --- Wallet & key management -------------------------------------------------

def _normalize_secret_key(raw_key: str) -> str:
    key = raw_key.strip()
    if not key:
        raise ValueError("SECRET_KEY is empty.")
    if not key.startswith("0x"):
        key = "0x" + key
    hex_part = key[2:]
    if len(hex_part) != 64:
        raise ValueError("SECRET_KEY must be 64 hex chars (32 bytes) with optional 0x prefix.")
    # basic hex validation
    int(hex_part, 16)
    return key


def _load_secret_key_hierarchical(*, use_alpha: bool) -> str:
    """Resolve SECRET_KEY with the hierarchy:
    1) If a .env in CWD defines SECRET_KEY, use that
    2) Else if os.environ has SECRET_KEY, use it
    3) Else prompt masked input
    """
    from dotenv import dotenv_values  # runtime dependency

    # 0) Manual override has highest priority
    if _secret_key_override is not None:
        return _secret_key_override

    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists() and _dotenv_values is not None:
        values = _dotenv_values(cwd_env.as_posix())
        preferred_key = "SECRET_KEY_ALPHA" if use_alpha else "SECRET_KEY"
        fallback_key = "SECRET_KEY"
        key = values.get(preferred_key) if values else None
        if not key and values:
            key = values.get(fallback_key)
        if key:
            return _normalize_secret_key(str(key))

    preferred_env = "SECRET_KEY_ALPHA" if use_alpha else "SECRET_KEY"
    env_key = os.getenv(preferred_env) or os.getenv("SECRET_KEY")
    if env_key:
        return _normalize_secret_key(env_key)

    entered = getpass("Enter SECRET_KEY (Ethereum private key for AUTONOMI & ETH(Arb)): ")
    return _normalize_secret_key(entered)


_wallet_cache: Dict[str, Wallet] = {}
_wallet_warned_zero: Dict[str, bool] = {}
_secret_key_override: Optional[str] = None
DEFAULT_MAX_FEE_PER_GAS_WEI = 20_000_000


async def _get_client_for_network(network: network_mod._Network) -> Client:
    return await async_client_manager.get_client(alpha=(network is network_mod.alpha))


def _create_wallet_from_secret(client: Client, secret_key: str) -> Wallet:
    # Support multiple possible constructors for forward/backward compatibility
    if hasattr(Wallet, "new_from_private_key"):
        return Wallet.new_from_private_key(client.evm_network(), secret_key)  # type: ignore[attr-defined]
    if hasattr(Wallet, "from_private_key"):
        return Wallet.from_private_key(client.evm_network(), secret_key)  # type: ignore[attr-defined]
    # Fallback: construct then import private key if available
    try:
        return Wallet(client.evm_network(), secret_key)  # type: ignore[call-arg]
    except Exception as exc:
        raise RuntimeError("Unsupported Wallet construction method in autonomi_client.") from exc


def set_secret_key(secret_key: str) -> None:
    """Set a process-wide SECRET_KEY override (highest priority).

    Re-initializes cached wallets so subsequent calls use the new key.
    """
    global _secret_key_override
    _secret_key_override = _normalize_secret_key(secret_key)
    _clear_wallet_cache()


def _clear_wallet_cache() -> None:
    _wallet_cache.clear()
    _wallet_warned_zero.clear()


async def _get_wallet_for_network(network: network_mod._Network, client: Optional[Client] = None) -> Wallet:
    key = f"{network.name}"
    if key in _wallet_cache:
        return _wallet_cache[key]

    use_client = client or await _get_client_for_network(network)
    secret_key = _load_secret_key_hierarchical(use_alpha=(network is network_mod.alpha))
    wallet = _create_wallet_from_secret(use_client, secret_key)
    # Set default transaction config to dweb's lower max fee per gas
    try:
        wallet.set_transaction_config(
            TransactionConfig(max_fee_per_gas=MaxFeePerGas.limited_auto(DEFAULT_MAX_FEE_PER_GAS_WEI))
        )
    except Exception:
        pass
    _wallet_cache[key] = wallet
    _wallet_warned_zero.setdefault(key, False)

    # Warn on zero balances once
    try:
        autonomi_balance_raw = await wallet.balance()
        gas_balance_raw = await wallet.balance_of_gas()

        def _normalize_amount(raw: object) -> float:
            # Convert raw integer-like or decimal-like to human units by dividing 1e18
            d = Decimal(str(raw))
            return float(d / (Decimal(10) ** 18))

        autonomi_balance = _normalize_amount(autonomi_balance_raw)
        gas_balance = _normalize_amount(gas_balance_raw)
        if not _wallet_warned_zero[key] and (autonomi_balance == 0.0 or gas_balance == 0.0):
            warnings.warn(
                "Wallet has zero balance for AUTONOMI token and/or ETH(Arb). Uploads may fail.",
                RuntimeWarning,
                stacklevel=2,
            )
            _wallet_warned_zero[key] = True
    except Exception:
        # If balance calls fail, do not block wallet usage; keep silent to avoid noisy tests
        pass

    return wallet


def _data_address_to_hex_str(addr_obj: Union[DataAddress, str]) -> str:
    if isinstance(addr_obj, DataAddress):
        # Try common hex getters
        for attr in ("to_hex", "as_hex"):
            if hasattr(addr_obj, attr):
                hex_val = getattr(addr_obj, attr)()
                if isinstance(hex_val, str):
                    return hex_val.lower().removeprefix("0x")
        # Fallback to str parsing: expected format DataAddress('...')
        s = str(addr_obj)
    else:
        s = addr_obj

    s = s.strip()
    if s.startswith("DataAddress(") and s.endswith(")"):
        # extract between single quotes
        try:
            inner = s.split("DataAddress(", 1)[1][:-1]
            inner = inner.strip().strip("'").strip('"')
            s = inner
        except Exception:
            pass
    if s.startswith("0x"):
        s = s[2:]
    return s.lower()


async def put(
    data: bytes,
    fee_limit_wei: Optional[int] = None,
    *,
    network: network_mod._Network = network_mod.mainnet,
    private: bool = False,
) -> Tuple[float, str]:
    """Upload data to Autonomi network.

    By default uploads as public. Set private=True to store privately (no datamap upload).

    Returns (cost_in_AUTONOMI as float, data_address_hex as str).
    """
    client = await _get_client_for_network(network)
    wallet = await _get_wallet_for_network(network, client)

    # Apply fee limit for this operation (default if not provided)
    effective_limit = int(fee_limit_wei) if fee_limit_wei is not None else DEFAULT_MAX_FEE_PER_GAS_WEI
    try:
        wallet.set_transaction_config(
            TransactionConfig(max_fee_per_gas=MaxFeePerGas.limited_auto(effective_limit))
        )
    except Exception:
        pass
    pay_opt = PaymentOption.wallet(wallet)

    if private:
        cost_str, data_addr = await client.data_put(data, pay_opt)
    else:
        cost_str, data_addr = await client.data_put_public(data, pay_opt)

    try:
        cost = float(cost_str)
    except Exception:
        cost = float(str(cost_str))
    addr_hex = _data_address_to_hex_str(data_addr)
    return cost, addr_hex


async def balance(
    *, network: network_mod._Network = network_mod.mainnet
) -> float:
    """Return AUTONOMI token balance for the resolved wallet on the given network."""
    client = await _get_client_for_network(network)
    wallet = await _get_wallet_for_network(network, client)
    bal_raw = await wallet.balance()
    return float(Decimal(str(bal_raw)) / (Decimal(10) ** 18))


async def gas(
    *, network: network_mod._Network = network_mod.mainnet
) -> float:
    """Return ETH(Arb) balance for the resolved wallet on the given network."""
    client = await _get_client_for_network(network)
    wallet = await _get_wallet_for_network(network, client)
    bal_raw = await wallet.balance_of_gas()
    return float(Decimal(str(bal_raw)) / (Decimal(10) ** 18))


async def wallet_address(
    *, network: network_mod._Network = network_mod.mainnet
) -> str:
    """Return the wallet address string for the resolved wallet on the given network."""
    client = await _get_client_for_network(network)
    wallet = await _get_wallet_for_network(network, client)
    addr = wallet.address()
    return str(addr)


