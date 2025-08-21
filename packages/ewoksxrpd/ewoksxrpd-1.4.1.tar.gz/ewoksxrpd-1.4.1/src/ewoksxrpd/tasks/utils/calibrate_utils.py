from __future__ import annotations

from typing import Sequence, Set, Union, List, Optional, Dict


def parse_fixed(
    fixed: Optional[List[str]], parametrization: Dict[str, List[str]]
) -> Set[str]:
    if not fixed:
        return set()
    allowed = {"dist", "poni1", "poni2", "rot1", "rot2", "rot3", "energy"}
    existing = set(fixed)
    unexpected = existing - allowed
    if unexpected:
        raise ValueError(f"'fixed' has unexpected parameters {sorted(unexpected)}")
    out = set()
    for param in fixed:
        out |= set(parametrization.get(param, {param}))
    return out


def parse_max_rings(max_rings: Union[int, Sequence[int], None]) -> Sequence[int | None]:
    if isinstance(max_rings, Sequence):
        return max_rings

    if not max_rings:
        return [None]

    if not isinstance(max_rings, int) or max_rings < 0:
        return [None]

    return [max_rings]
