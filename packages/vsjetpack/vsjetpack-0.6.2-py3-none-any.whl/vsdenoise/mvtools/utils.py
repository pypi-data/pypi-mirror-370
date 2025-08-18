from __future__ import annotations

from typing import Sequence

from vstools import CustomValueError

__all__ = ["normalize_thscd", "planes_to_mvtools"]


def planes_to_mvtools(input_planes: Sequence[int]) -> int:
    """
    Convert a sequence of plane indices to MVTools' plane parameter value.

    MVTools uses a single integer to represent which planes to process:
        - 0: Process Y plane only
        - 1: Process U plane only
        - 2: Process V plane only
        - 3: Process UV planes only
        - 4: Process all planes

    Args:
        input_planes: Sequence of plane indices (0=Y, 1=U, 2=V) to process.

    Returns:
        Integer value used by MVTools to specify which planes to process.
    """

    planes = set(input_planes)

    if planes == {0, 1, 2}:
        return 4

    if len(planes) == 1 and planes.intersection({0, 1, 2}):
        return planes.pop()

    if planes == {1, 2}:
        return 3

    raise CustomValueError("Invalid planes specified!", planes_to_mvtools)


def normalize_thscd(
    thscd: int | tuple[int | None, int | float | None] | None, scale: bool = True
) -> tuple[int | None, int | None]:
    """
    Normalize and scale the thscd parameter.

    Args:
        thscd: thscd value to scale and/or normalize.
        scale: Whether to scale thscd2 from 0-100 percentage threshold to 0-255.

    Returns:
        Scaled and/or normalized thscd tuple.
    """

    thscd1, thscd2 = thscd if isinstance(thscd, tuple) else (thscd, None)

    if scale and thscd2 is not None:
        thscd2 = round(thscd2 / 100 * 255)

    if isinstance(thscd2, float):
        thscd2 = int(thscd2)

    return (thscd1, thscd2)
