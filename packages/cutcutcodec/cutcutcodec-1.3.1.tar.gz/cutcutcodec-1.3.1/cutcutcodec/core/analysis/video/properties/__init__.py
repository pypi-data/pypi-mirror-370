#!/usr/bin/env python3

"""Recover basic video information."""

from .duration import get_duration_video
from .nb_frames import get_nb_frames
from .pxl_format import get_pxl_format
from .rate import get_rate_video
from .resolution import get_resolution
from .timestamps import get_timestamps_video


__all__ = [
    "get_duration_video",
    "get_nb_frames",
    "get_pxl_format",
    "get_rate_video",
    "get_resolution",
    "get_timestamps_video",
]
