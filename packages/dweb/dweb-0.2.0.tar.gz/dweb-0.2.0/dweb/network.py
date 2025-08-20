from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


NetworkName = Literal["mainnet", "alpha"]


@dataclass(frozen=True)
class _Network:
    name: NetworkName


mainnet = _Network("mainnet")
alpha = _Network("alpha")


