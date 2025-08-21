from pathlib import Path
from typing import List, Optional
from fractions import Fraction
from decimal import Decimal

import typer

from .util import parse_timestamp
from .video_cutter import SegmentSpec


class SegmentParser:
    """
    Parses segment specifications with support for open-ended segments using _.

    Supports formats like:
    - "00:37-04:23" (normal start-end)
    - "00:37-_" (from start time to end of video)
    - "_-00:42" (from start of video to end time)
    - "0-_" (entire video)
    """

    def __init__(self, duration: Optional[Fraction] = None):
        """
        Initialize the parser.

        Args:
            duration: Total duration of the video. Required for _ symbol support.
        """
        self.duration = duration

    def parse(self, segment_str: str) -> List[SegmentSpec]:
        """
        Parse segment string or file path into a list of SegmentSpec objects.

        Args:
            segment_str: Either a comma-separated string of segments or path to a file

        Returns:
            List of SegmentSpec objects

        Raises:
            typer.BadParameter: If parsing fails or segments are invalid
        """
        segment_lines: List[str] = []
        segment_path = Path(segment_str)

        if segment_path.exists() and segment_path.is_file():
            segment_lines = self._parse_segments_from_file(segment_path)
        else:
            # assume comma-separated string if not a file
            segment_lines = [s.strip() for s in segment_str.split(",") if s.strip()]

        if not segment_lines:
            raise typer.BadParameter(
                "no segment specifications found in input string or file."
            )

        segments: List[SegmentSpec] = []
        for i, line in enumerate(segment_lines):
            segments.append(self._parse_single_segment(line, i))

        if not segments:
            raise typer.BadParameter("no valid segments specified after parsing.")

        return segments

    def _parse_segments_from_file(self, segment_path: Path) -> List[str]:
        """Read segment lines from a file."""
        try:
            with open(segment_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            raise typer.BadParameter(f"error reading segment file {segment_path}: {e}")

    def _parse_single_segment(self, line: str, index: int) -> SegmentSpec:
        """
        Parse a single 'start-end' line into a SegmentSpec.

        Supports _ symbol for open-ended segments:
        - "start-_" uses video duration as end
        - "_-end" uses 0 as start
        """
        if "-" not in line:
            raise typer.BadParameter(
                f"invalid segment format: '{line}'. use 'start-end' (e.g., '10-20', '1:30.5-2:45', '00:37-_')."
            )

        start_str, end_str = line.split("-", 1)
        start_str = start_str.strip()
        end_str = end_str.strip()

        # Handle _ symbol
        if start_str == "_" or end_str == "_":
            if self.duration is None:
                raise typer.BadParameter(
                    f"cannot use '_' symbol in segment '{line}': video duration not available. "
                    "This usually means the input file could not be probed."
                )

        # Parse start time
        if start_str == "_":
            start_seconds = 0.0
        else:
            try:
                start_seconds = parse_timestamp(start_str)
            except ValueError as e:
                raise typer.BadParameter(f"invalid start timestamp in segment '{line}': {e}")

        # Parse end time
        if end_str == "_":
            end_seconds = float(self.duration)
        else:
            try:
                end_seconds = parse_timestamp(end_str)
            except ValueError as e:
                raise typer.BadParameter(f"invalid end timestamp in segment '{line}': {e}")

        if end_seconds <= start_seconds:
            raise typer.BadParameter(
                f"end time must be after start time in segment: '{line}'"
            )

        # Create segment spec with exact fraction precision
        try:
            start_frac = Fraction(Decimal(str(start_seconds)))
            end_frac = Fraction(Decimal(str(end_seconds)))
        except ValueError:
            raise typer.BadParameter(
                f"could not convert parsed timestamps to exact fractions for segment: '{line}'"
            )

        return SegmentSpec(start=start_frac, end=end_frac, index=index)
