"""Phrase offset (base.md §4.4, Task 2.12).

`phrase_offset_bars` is measured relative to the *outgoing track's own* phrase
anchor — per base.md §4.4 ("establish the outgoing track's phrase grid... compute
where the incoming track's first downbeat lands relative to that grid"), not the
mix's absolute bar 0. The anchor for a given transition is wherever that outgoing
track itself started playing — in practice, the previous transition's overlap
centre (or the mix start, for the first track). Assembling that per-transition
anchor across a full transition list is the caller's job (out of scope for this
isolated bar-arithmetic module); it's passed in explicitly as `segment_start_s`.
"""

from __future__ import annotations

from analyzer import config
from analyzer.features.rhythm import DownbeatGrid


def phrase_offset_bars(
    downbeat_grid: DownbeatGrid,
    segment_start_s: float,
    incoming_first_downbeat_s: float,
    phrase_length_bars: int = config.PHRASE_LENGTH_BARS,
) -> int:
    """`(incoming_first_downbeat_bar - outgoing_segment_start_bar) mod 32` (base.md
    §4.4). Reports the raw number only, no verdict — 0 and 16 are common/intentional,
    anything else is usually a mistake, but that judgement is left to the reader.
    """
    start_bar = downbeat_grid.bar_index_at(segment_start_s)
    incoming_bar = downbeat_grid.bar_index_at(incoming_first_downbeat_s)
    return (incoming_bar - start_bar) % phrase_length_bars
