from __future__ import annotations

from typing import Optional, Tuple, Union
from dweb.network import _Network
from autonomi_client import DataAddress


def get(
    address: Union[str, DataAddress],
    *,
    network: _Network = ..., 
    timeout: Optional[float] = ..., 
) -> bytes: ...


def put(
    data: bytes,
    fee_limit_wei: Optional[int] = ..., 
    *,
    network: _Network = ...,
    private: bool = ..., 
    timeout: Optional[float] = ...,
) -> Tuple[float, str]: ...


def get_balance(
    *, network: _Network = ..., timeout: Optional[float] = ...
) -> float: ...


def get_gas(
    *, network: _Network = ..., timeout: Optional[float] = ...
) -> float: ...


def get_wallet_address(
    *, network: _Network = ..., timeout: Optional[float] = ...
) -> str: ...


def set_secret_key(secret_key: str) -> None: ...

# Module-level convenience properties
balance: float
gas: float
wallet: str
