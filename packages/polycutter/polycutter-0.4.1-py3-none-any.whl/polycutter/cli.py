import os
import time
import json
import shutil
from typing import List, Optional, Any, Dict, Tuple
from enum import Enum
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import traceback

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from minlog import logger, Verbosity

from .video_cutter import (
    VideoCutter,
    SegmentSpec,
    SnapMode,
    ConfigError,
    ProbeError,
    SnapError,
    ExtractError,
    MergeError,
    ValidateError,
    CompatibilityError,
)
from .segment_parser import SegmentParser
from .util import humanize_bytes, parse_timestamp, format_time

# --- constants ---
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
APP_NAME = "polycutter"
APP_DESC = "lossless media cut tool"
APP_VERSION = "0.4.0"

# --- typer app setup ---
app = typer.Typer(
    name=APP_NAME,
    help=f"{APP_NAME}: {APP_DESC}",
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
    pretty_exceptions_show_locals=False,
)

# console for rich-specific display
console = Console()


# --- enums for cli choices ---
class SnapModeChoice(str, Enum):
    OUT = "out"
    IN = "in"
    SMART = "smart"


class VerbosityChoice(str, Enum):
    ERROR = "error"  # maps to minlog.Verbosity.ERROR (1)
    WARN = "warn"  # maps to minlog.Verbosity.WARN (2)
    INFO = "info"  # maps to minlog.Verbosity.INFO (3)
    DEBUG = "debug"  # maps to minlog.Verbosity.DEBUG (5)


# --- helper functions: logging and setup ---


def setup_logger(verbosity: VerbosityChoice):
    """configures the global minlog logger based on the cli verbosity choice."""
    # Map cli choice string to correct minlog.Verbosity enum member
    level_map = {
        VerbosityChoice.ERROR: Verbosity.ERROR,
        VerbosityChoice.WARN: Verbosity.WARN,
        VerbosityChoice.INFO: Verbosity.INFO,
        VerbosityChoice.DEBUG: Verbosity.DEBUG,
        # Note: minlog.TRACE (4) is not exposed via cli currently
    }
    target_level = level_map[verbosity]
    if hasattr(logger, "configure"):
        logger.configure(level=target_level)
        logger.debug(
            f"logger configured to level: {target_level.name} ({target_level.value})"
        )
    else:
        # Fallback for older minlog? Unlikely needed but safe
        logger._level = target_level
        logger.debug(
            f"logger level set via fallback to: {target_level.name} ({target_level.value})"
        )


# --- helper functions: segment parsing ---


def _probe_video_duration(input_path: Path, ffprobe_path: str) -> Optional[Fraction]:
    """Probe video duration for segment parsing."""
    import subprocess
    import json

    try:
        # Run ffprobe to get duration
        cmd = [
            ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(input_path),
        ]

        logger.debug(f"probing duration: {' '.join(cmd)}")
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )

        probe_data = json.loads(proc.stdout)
        duration_str = probe_data.get("format", {}).get("duration")

        if duration_str:
            # Convert to Fraction for precision
            from decimal import Decimal
            return Fraction(Decimal(duration_str))
        else:
            logger.warn("duration not found in ffprobe output")
            return None

    except subprocess.CalledProcessError as e:
        logger.warn(f"ffprobe failed: {e}")
        return None
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.warn(f"could not parse ffprobe output: {e}")
        return None
    except FileNotFoundError:
        logger.warn(f"ffprobe executable not found at '{ffprobe_path}'")
        return None
    except Exception as e:
        logger.warn(f"unexpected error probing duration: {e}")
        return None


# --- helper functions: output path validation ---


def _validate_output_dir(output_dir: Path):
    """ensures output directory exists and is writable."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        test_file = output_dir / f".polycut_write_test_{os.getpid()}"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        raise typer.BadParameter(
            f"output directory '{output_dir}' is not writable or could not be created: {e}"
        )


def _handle_existing_output(output_path: Path, force_yes: bool):
    """prompts or removes a single existing output file."""
    if not force_yes:
        overwrite = typer.confirm(
            f"output file '{output_path}' already exists. overwrite?", default=False
        )
        if not overwrite:
            logger.warn("operation canceled by user.")
            raise typer.Exit(code=0)

    logger.info(f"attempting to remove existing output: {output_path}")
    try:
        if output_path.is_dir():
            shutil.rmtree(output_path)
        else:
            output_path.unlink()
    except Exception as e:
        raise typer.BadParameter(
            f"failed to remove existing output '{output_path}': {e}"
        )


def _handle_existing_pattern_output(existing_files: List[Path], force_yes: bool):
    """prompts or removes existing files matching the output pattern."""
    logger.warn(
        f"found {len(existing_files)} existing output file(s) matching the pattern:"
    )
    for f in existing_files[:5]:  # show first few
        logger.warn(f"  - {f.name}")
    if len(existing_files) > 5:
        logger.warn(f"  ... and {len(existing_files) - 5} more.")

    if not force_yes:
        overwrite = typer.confirm(
            f"overwrite {len(existing_files)} existing file(s)?", default=False
        )
        if not overwrite:
            logger.warn("operation canceled by user.")
            raise typer.Exit(code=0)

    # If overwriting or force_yes is true, attempt removal
    logger.info(
        f"attempting to remove {len(existing_files)} existing output file(s)..."
    )
    removed_count = 0
    failed_removals = []
    for f_path in existing_files:
        try:
            if f_path.is_dir():
                shutil.rmtree(f_path)
            else:
                f_path.unlink()
            removed_count += 1
        except Exception as e:
            logger.error(f"failed to remove existing file '{f_path}': {e}")
            failed_removals.append(f_path)

    if failed_removals:
        raise typer.BadParameter(
            f"failed to remove {len(failed_removals)} existing output file(s). cannot proceed."
        )
    logger.info(f"successfully removed {removed_count} existing file(s).")


def validate_output_path(
    output_path_or_pattern: Path,
    num_segments: int,
    no_merge: bool,
    dry_run: bool = False,
    force_yes: bool = False,
):
    """
    ensures output directory exists and handles existing output file(s).
    delegates logic based on merge mode.
    """
    output_dir: Path
    if not no_merge:
        # --- single output file mode ---
        output_path = output_path_or_pattern
        output_dir = output_path.parent
        logger.debug(f"validating single output file path: {output_path}")
        _validate_output_dir(output_dir)
        if output_path.exists() and not dry_run:
            _handle_existing_output(output_path, force_yes)
    else:
        # --- multiple output files mode (no-merge) ---
        output_pattern = str(output_path_or_pattern)
        logger.debug(f"validating output pattern: {output_pattern}")

        if "{}" not in output_pattern:
            raise typer.BadParameter(
                "output pattern must contain '{}' placeholder for segment index when using --no-merge."
            )

        try:
            sample_path = Path(output_pattern.format(1))  # use 1 for sample formatting
            output_dir = sample_path.parent
        except Exception as e:
            raise typer.BadParameter(
                f"invalid output pattern format '{output_pattern}': {e}"
            )

        logger.debug(f"target output directory for pattern: {output_dir}")
        _validate_output_dir(output_dir)

        # Check for existing files based on the pattern
        existing_files: List[Path] = []
        for i in range(num_segments):
            try:
                segment_index = i + 1  # 1-based index for filename pattern
                potential_path = Path(output_pattern.format(segment_index)).resolve()
                if potential_path.exists():
                    existing_files.append(potential_path)
            except Exception as e:
                # Catch errors during formatting (e.g., invalid pattern parts)
                raise typer.BadParameter(
                    f"error generating output path for segment {segment_index} from pattern '{output_pattern}': {e}"
                )

        if existing_files and not dry_run:
            _handle_existing_pattern_output(existing_files, force_yes)

    # Return the original path/pattern - the caller will use it
    return output_path_or_pattern


# --- helper functions: display ---


def display_requested_segment_table(segments: List[SegmentSpec]):
    """prints a rich table summarizing the segments requested by the user."""
    table = Table(title="requested segments")
    table.add_column("#", style="dim")  # use dim style for index
    table.add_column("start time")
    table.add_column("end time")
    table.add_column("duration", justify="right")

    total_requested_duration = Fraction(0)
    for seg in segments:
        start_str = format_time(float(seg.start))
        end_str = format_time(float(seg.end))
        duration = seg.end - seg.start
        duration_str = format_time(float(duration))
        total_requested_duration += duration

        table.add_row(
            str(seg.index + 1),  # Display 1-based index
            f"{start_str} ({float(seg.start):.3f}s)",
            f"{end_str} ({float(seg.end):.3f}s)",
            duration_str,
        )

    console.print(table)
    console.print(
        f"total requested duration: {format_time(float(total_requested_duration))}"
    )


def _display_no_merge_summary(segments: List[Dict[str, Any]]):
    """displays the summary table for the no-merge mode."""
    table = Table(title="extracted segments summary")
    table.add_column("#", style="dim")
    table.add_column("output file", style="magenta", no_wrap=True)
    table.add_column("duration", justify="right")
    table.add_column("size", justify="right")
    table.add_column("start shift", justify="right", style="yellow")
    table.add_column("end shift", justify="right", style="yellow")

    total_actual_duration = Fraction(0)
    total_output_size = 0
    files_missing = 0

    for seg in segments:
        act = seg.get("actual", {})
        shifts = seg.get("shifts", {})
        output_file_str = seg.get("output_file", "n/a")
        output_file_path = Path(output_file_str)

        try:
            # Convert exact duration string directly to Fraction
            act_duration_str = act.get("duration_exact", "0")
            act_duration = Fraction(act_duration_str)
        except (ValueError, TypeError) as e:
            logger.warn(
                f"could not parse exact duration '{act_duration_str}' for segment {seg.get('index', 'n/a')}: {e}"
            )
            act_duration = Fraction(0)  # Default to 0 if parsing fails

        total_actual_duration += act_duration
        duration_str = format_time(float(act_duration))

        start_shift_val = shifts.get("start", 0.0)
        end_shift_val = shifts.get("end", 0.0)
        start_shift_str = f"{start_shift_val:+.3f}s"
        end_shift_str = f"{end_shift_val:+.3f}s"

        size_str = "[dim]n/a[/]"
        try:
            if output_file_path.exists() and output_file_path.is_file():
                size_bytes = output_file_path.stat().st_size
                total_output_size += size_bytes
                size_str = humanize_bytes(size_bytes)
            else:
                files_missing += 1
                size_str = "[red]missing[/]"
        except Exception as e:
            logger.trace(f"could not stat file {output_file_path}: {e}")
            size_str = "[red]error[/]"

        table.add_row(
            str(seg.get("index", "n/a") + 1),
            output_file_path.name,  # Show only filename
            duration_str,
            size_str,
            start_shift_str,
            end_shift_str,
        )

    console.print(table)
    console.print(f"total actual duration: {format_time(float(total_actual_duration))}")
    console.print(
        f"total output size: {humanize_bytes(total_output_size)} ({len(segments)} files)"
    )
    if files_missing > 0:
        logger.warn(
            f"{files_missing} output file(s) were reported missing or inaccessible."
        )


def _display_merge_summary(
    segments: List[Dict[str, Any]], segment_info: Dict[str, Any]
):
    """displays the summary table for the merge mode."""
    table = Table(title="merged segments summary")
    table.add_column("#", style="dim")
    table.add_column("requested", style="blue")
    table.add_column("actual", style="cyan")
    table.add_column("shifts", style="yellow")
    table.add_column("duration Δ", style="green")

    for seg in segments:
        req = seg.get("requested", {})
        act = seg.get("actual", {})
        shifts = seg.get("shifts", {})

        req_fmt = req.get("formatted", {})
        act_fmt = act.get("formatted", {})
        req_dur = req.get("duration", 0.0)
        start_shift_val = shifts.get("start", 0.0)
        end_shift_val = shifts.get("end", 0.0)
        duration_change = shifts.get("duration", 0.0)

        start_shift = f"{start_shift_val:+.3f}s"
        end_shift = f"{end_shift_val:+.3f}s"

        has_shift = abs(start_shift_val) > 0.001 or abs(end_shift_val) > 0.001
        shift_str = f"start: {start_shift}\nend: {end_shift}"
        if has_shift:
            shift_str = f"[yellow]{shift_str}[/]"

        req_str = f"{req_fmt.get('start','n/a')} - {req_fmt.get('end','n/a')}"
        act_str = f"{act_fmt.get('start','n/a')} - {act_fmt.get('end','n/a')}"

        duration_str = "no change"
        if abs(duration_change) > 0.001:
            change_pct = (duration_change / req_dur * 100) if req_dur > 1e-6 else 0
            duration_str = f"{duration_change:+.3f}s ({change_pct:+.1f}%)"
            duration_str = (
                f"[green]{duration_str}[/]"
                if duration_change > 0
                else f"[red]{duration_str}[/]"
            )

        table.add_row(
            str(seg.get("index", "n/a") + 1), req_str, act_str, shift_str, duration_str
        )

    totals = segment_info.get("totals", {})
    totals_fmt = totals.get("formatted", {})
    requested_duration = totals.get("requested_duration", 0.0)
    actual_duration = totals.get("actual_duration", 0.0)

    total_duration_change = actual_duration - requested_duration
    change_str = ""
    if abs(total_duration_change) > 0.001:
        change_pct = (
            (total_duration_change / requested_duration * 100)
            if requested_duration > 1e-6
            else 0
        )
        change_str = f"Δ: {total_duration_change:+.3f}s ({change_pct:+.1f}%)"
        change_str = (
            f"[green]{change_str}[/]"
            if total_duration_change > 0
            else f"[red]{change_str}[/]"
        )

    table.add_section()
    table.add_row(
        "TOTAL",
        f"requested: {totals_fmt.get('requested', 'n/a')}",
        f"actual: {totals_fmt.get('actual', 'n/a')}",
        f"{len(segments)} segments merged",
        change_str,
    )
    console.print(table)


def display_output_summary(segment_info: Dict[str, Any], no_merge: bool):
    """prints a rich table summarizing the actual extracted/merged output."""
    segments = segment_info.get("segments", [])
    if not segments:
        logger.warn("no segment data available to display summary.")
        return

    if no_merge:
        _display_no_merge_summary(segments)
    else:
        _display_merge_summary(segments, segment_info)


# --- helper functions: execution and reporting ---


def run_cutting_process(cutter: VideoCutter, logger_level: int, no_merge: bool):
    """runs the VideoCutter instance, optionally with a progress bar."""
    progress_description = (
        "extracting segments..." if no_merge else "cutting and merging..."
    )
    progress_complete_desc = (
        "[green]extraction complete[/]" if no_merge else "[green]cut complete[/]"
    )
    progress_fail_desc = (
        "[red]extraction failed[/]" if no_merge else "[red]cut failed[/]"
    )

    # show progress bar only if logger level is INFO or more verbose (DEBUG, TRACE)
    # minlog levels: error=1, warn=2, info=3, trace=4, debug=5
    if logger_level >= Verbosity.INFO.value:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None, complete_style="cyan"),
            TimeElapsedColumn(),
            console=console,
            transient=True,  # clear progress on exit
        ) as progress:
            task_id = progress.add_task(progress_description, total=None)
            try:
                cutter.run()
                progress.update(
                    task_id,
                    completed=1,
                    total=1,
                    description=progress_complete_desc,
                )
            except Exception as e:
                progress.update(
                    task_id, description=progress_fail_desc, total=1, completed=1
                )
                raise  # re-raise after updating progress
    else:
        # run without progress bar in error/warn mode
        cutter.run()


def report_final_summary(
    segment_info: Dict[str, Any],
    no_merge: bool,
    output_path_or_pattern: Path,
    input_file_size: int,
    dry_run: bool,
):
    """logs the final summary message about output files and sizes."""
    if dry_run:
        logger.info("[dry run] completed without creating output file(s).")
        return

    if no_merge:
        output_files = segment_info.get("output_files", [])
        total_output_size = 0
        files_checked = 0
        files_missing = 0
        for file_path_str in output_files:
            try:
                file_path = Path(file_path_str)
                if file_path.exists() and file_path.is_file():
                    total_output_size += file_path.stat().st_size
                    files_checked += 1
                else:
                    files_missing += 1
            except Exception as e:
                logger.warn(f"could not stat output file '{file_path_str}': {e}")

        size_str = humanize_bytes(total_output_size)
        ratio_str = ""
        if input_file_size > 0:
            output_size_ratio = total_output_size / input_file_size * 100
            ratio_str = f" ({output_size_ratio:.1f}% of input)"

        logger.info(
            f"created {files_checked} output file(s) matching pattern: {output_path_or_pattern}"
        )
        logger.info(f"total output size: {size_str}{ratio_str}")
        if files_missing > 0:
            logger.warn(
                f"{files_missing} expected output file(s) were not found or inaccessible."
            )

    else:  # merge mode
        output_path = output_path_or_pattern
        if output_path.exists() and output_path.is_file():
            try:
                output_file_size = output_path.stat().st_size
                size_str = humanize_bytes(output_file_size)
                ratio_str = ""
                if input_file_size > 0:
                    output_file_size_ratio = output_file_size / input_file_size * 100
                    ratio_str = f" ({output_file_size_ratio:.1f}% of input)"
                logger.info(f"output file: {output_path} ({size_str}){ratio_str}")
            except Exception as e:
                logger.warn(f"could not stat output file '{output_path}': {e}")
        else:
            logger.warn(f"expected output file '{output_path}' not found after merge.")


# --- helper functions: probe command ---
def _display_probe_format_table(format_info: Dict, input_path: Path) -> float:
    """displays the file information table for the probe command. returns duration."""
    table = Table(title="file information", show_header=False, box=None, padding=(0, 1))
    table.add_column("property", style="cyan", no_wrap=True)
    table.add_column("value")
    table.add_row("filename", str(input_path.name))
    table.add_row("path", str(input_path.parent))
    table.add_row("format", format_info.get("format_long_name", "n/a"))

    duration = 0.0  # default
    duration_str = format_info.get("duration", "0")
    try:
        duration = float(duration_str)
        table.add_row("duration", f"{format_time(duration)} ({duration:.3f}s)")
    except ValueError:
        logger.warn(f"invalid duration value '{duration_str}' in probe data.")
        table.add_row("duration", f"{duration_str} (invalid)")

    if size_str := format_info.get("size"):
        if size_str.isdigit():
            table.add_row("size", humanize_bytes(int(size_str)))
    if bitrate_str := format_info.get("bit_rate"):
        if bitrate_str.isdigit():
            table.add_row("bitrate", f"{int(bitrate_str) / 1000:.1f} kbps")
    console.print(table)
    return duration  # return parsed duration


def _display_probe_video_table(video_stream: Dict):
    """displays the video stream table for the probe command."""
    table = Table(title="video stream", show_header=False, box=None, padding=(0, 1))
    table.add_column("property", style="cyan", no_wrap=True)
    table.add_column("value")
    codec = video_stream.get("codec_name", "n/a")
    profile = video_stream.get("profile", "")
    # Handle profile being -99 sometimes
    codec_display = (
        f"{codec} ({profile})"
        if profile and profile not in ["unknown", "n/a", -99]
        else codec
    )
    width = video_stream.get("width", 0)
    height = video_stream.get("height", 0)
    aspect_ratio = video_stream.get("display_aspect_ratio", "n/a")
    fps_str = video_stream.get("r_frame_rate", "0/1")
    try:
        num, denom = map(int, fps_str.split("/"))
        fps_display = f"{num / denom:.3f} fps" if denom else fps_str
    except ValueError:
        fps_display = f"{fps_str} (invalid)"

    table.add_row("codec", codec_display)
    table.add_row("resolution", f"{width}x{height} (dar {aspect_ratio})")
    table.add_row("frame rate", fps_display)
    if fmt := video_stream.get("pix_fmt"):
        table.add_row("pixel format", fmt)
    if cs := video_stream.get("color_space"):
        table.add_row("color space", cs)
    if bd := video_stream.get("bits_per_raw_sample", "N/A"):
        if bd != "N/A":
            table.add_row("bit depth", str(bd))
    console.print(table)


def _run_keyframe_probe(ffprobe_path: str, input_path: Path) -> Tuple[List[float], str]:
    """runs ffprobe commands to detect keyframes, returns list and method used."""
    keyframes = []
    kf_scan_method = "n/a"
    import subprocess  # local import

    # Method 1: packet flags (fast)
    cmd_kf_pkt = [
        ffprobe_path,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_packets",
        "-show_entries",
        "packet=pts_time,flags",
        "-of",
        "csv=p=0",
        str(input_path),
    ]
    try:
        logger.debug(f"running ffprobe kf packets: {' '.join(cmd_kf_pkt)}")
        proc = subprocess.run(
            cmd_kf_pkt,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        kf_scan_method = "packets"
        for line in proc.stdout.strip().splitlines():
            parts = line.split(",")
            if len(parts) == 2 and "k" in parts[1].lower():
                try:
                    keyframes.append(float(parts[0]))
                except ValueError:
                    pass
    except Exception as e:
        logger.debug(f"kf packet scan failed: {e}, trying skip_frame...")

    # Method 2: skip frame (fallback)
    if not keyframes:
        cmd_kf_skip = [
            ffprobe_path,
            "-v",
            "error",
            "-skip_frame",
            "nokey",
            "-select_streams",
            "v:0",
            "-show_entries",
            "frame=pts_time",
            "-of",
            "csv=p=0",
            str(input_path),
        ]
        try:
            logger.debug(f"running ffprobe kf skip_frame: {' '.join(cmd_kf_skip)}")
            proc = subprocess.run(
                cmd_kf_skip,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            kf_scan_method = "skip_frame"
            for line in proc.stdout.strip().splitlines():
                try:
                    keyframes.append(float(line.strip()))
                except ValueError:
                    pass
        except Exception as e:
            logger.warn(f"kf skip_frame scan also failed: {e}")

    if keyframes:
        keyframes = sorted(
            list(set(kf for kf in keyframes if kf >= 0))
        )  # Dedupe, sort, non-negative
    return keyframes, kf_scan_method


def _display_probe_keyframes(
    keyframes: List[float], kf_scan_method: str, duration: float
):
    """displays keyframe analysis tables for the probe command."""
    if not keyframes:
        logger.warn("failed to retrieve keyframe information.")
        return

    # keyframe stats table
    kf_table = Table(
        title=f"keyframe analysis ({kf_scan_method} scan)",
        show_header=False,
        box=None,
        padding=(0, 1),
    )
    kf_table.add_column("property", style="cyan", no_wrap=True)
    kf_table.add_column("value")
    kf_table.add_row("total found", str(len(keyframes)))
    if len(keyframes) >= 2:
        intervals = [keyframes[i] - keyframes[i - 1] for i in range(1, len(keyframes))]
        intervals = [i for i in intervals if i > 1e-6]  # Filter tiny/zero
        if intervals:
            kf_table.add_row("avg interval", f"{sum(intervals)/len(intervals):.3f}s")
            kf_table.add_row("min interval", f"{min(intervals):.3f}s")
            kf_table.add_row("max interval", f"{max(intervals):.3f}s")
        if duration > 0:
            kf_table.add_row("density", f"{len(keyframes)/(duration/60):.2f} per min")
    console.print(kf_table)

    # keyframe timestamps list (limited)
    kf_list_table = Table(title="keyframe timestamps", box=None, padding=(0, 1))
    kf_list_table.add_column("#", style="dim")
    kf_list_table.add_column("formatted")
    kf_list_table.add_column("seconds", justify="right")
    limit = 5
    if len(keyframes) <= 2 * limit:
        for i, kf in enumerate(keyframes):
            kf_list_table.add_row(str(i + 1), format_time(kf), f"{kf:.3f}")
    else:
        for i, kf in enumerate(keyframes[:limit]):
            kf_list_table.add_row(str(i + 1), format_time(kf), f"{kf:.3f}")
        kf_list_table.add_row("...", "...", "...")
        for i, kf in enumerate(keyframes[-limit:]):
            kf_list_table.add_row(
                str(len(keyframes) - limit + i + 1), format_time(kf), f"{kf:.3f}"
            )
    console.print(kf_list_table)


def _display_probe_audio_table(audio_streams: List[Dict]):
    """displays the audio streams table for the probe command."""
    table = Table(
        title=f"audio streams ({len(audio_streams)})", box=None, padding=(0, 1)
    )
    table.add_column("#", style="dim")
    table.add_column("codec")
    table.add_column("channels")
    table.add_column("sample rate")
    table.add_column("bitrate", justify="right")
    table.add_column("language")
    for i, stream in enumerate(audio_streams):
        codec = stream.get("codec_name", "n/a")
        profile = stream.get("profile", "")
        codec_display = (
            f"{codec} ({profile})"
            if profile and profile not in ["unknown", "n/a", -99]
            else codec
        )
        channels = stream.get("channels", 0)
        channel_layout = stream.get("channel_layout", "")
        chan_display = (
            f"{channels} ({channel_layout})" if channel_layout else str(channels)
        )
        sample_rate = stream.get("sample_rate", "0")
        bitrate_str = stream.get("bit_rate")
        bitrate_display = "n/a"
        if bitrate_str and bitrate_str.isdigit():
            bitrate_display = f"{int(bitrate_str)/1000:.0f} kbps"
        language = stream.get("tags", {}).get("language", "und")
        table.add_row(
            str(i + 1),
            codec_display,
            chan_display,
            f"{sample_rate} hz",
            bitrate_display,
            language,
        )
    console.print(table)


def _display_probe_subtitle_table(subtitle_streams: List[Dict]):
    """displays the subtitle streams table for the probe command."""
    table = Table(
        title=f"subtitle streams ({len(subtitle_streams)})", box=None, padding=(0, 1)
    )
    table.add_column("#", style="dim")
    table.add_column("codec")
    table.add_column("language")
    table.add_column("title")
    for i, stream in enumerate(subtitle_streams):
        codec = stream.get("codec_name", "n/a")
        language = stream.get("tags", {}).get("language", "und")
        title = stream.get("tags", {}).get("title", "-")
        table.add_row(str(i + 1), codec, language, title)
    console.print(table)


# --- typer commands ---


@app.callback()
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="show version and exit.",
        is_eager=True,
        callback=lambda v: v,
    ),
    verbose: VerbosityChoice = typer.Option(
        VerbosityChoice.INFO.value,
        "--verbose",
        "-v",
        help="set verbosity level (error, warn, info, debug).",
        case_sensitive=False,
    ),
):
    """
    polycutter: lossless media cutting tool.

    use 'cut' to extract segments or 'probe' to analyze files.
    set verbosity with -v [error|warn|info|debug].
    """
    if version:
        console.print(f"[bold]{APP_NAME}[/] version [cyan]{APP_VERSION}[/]")
        raise typer.Exit()

    setup_logger(verbose)
    ctx.ensure_object(dict)
    # Store numeric level for easier comparison later, using the correct minlog mapping
    ctx.obj["logger_level"] = getattr(Verbosity, verbose.upper()).value


@app.command()
def cut(
    ctx: typer.Context,
    # input/output options
    input_path: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="input media file path.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        show_default=False,
    ),
    output_path: Path = typer.Option(
        ...,
        "--output",
        "-o",
        help="output file path (e.g., 'output.mp4') or pattern for --no-merge "
        "(e.g., 'output_seg_{}.mp4', where {} is 1-based segment index).",
        resolve_path=True,
        show_default=False,
    ),
    segments: str = typer.Option(
        ...,
        "--segments",
        "-s",
        help="segment specs: 'start-end[,start-end...]' (times like 10.5, 1:30.250) "
        "or path to file (one start-end per line). Use '_' for video end (e.g., '00:37-_').",
        show_default=False,
    ),
    # general behavior options
    no_merge: bool = typer.Option(
        False,
        "--no-merge",
        help="extract segments to individual files instead of merging. "
        "output path must contain '{}' for segment index.",
    ),
    temp_dir: Optional[Path] = typer.Option(
        None,
        "--temp",
        "-t",
        help="temporary directory for intermediate files. auto-created if not set.",
        resolve_path=True,
    ),
    keep_temp: bool = typer.Option(
        False,
        "--keep-temp",
        "-k",
        help="keep temporary directory and files after completion.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="plan cuts and show commands without executing.",
    ),
    force_yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="answer yes to all prompts (e.g., force overwrite).",
    ),
    jobs: Optional[int] = typer.Option(
        1,
        "--jobs",
        "-j",
        help="number of parallel extraction jobs.",
        min=1,
    ),
    # path options
    ffmpeg_path: str = typer.Option("ffmpeg", help="path to ffmpeg executable."),
    ffprobe_path: str = typer.Option("ffprobe", help="path to ffprobe executable."),
    # cutting behavior options
    snap_mode: SnapModeChoice = typer.Option(
        SnapModeChoice.OUT.value,
        "--snap",
        help="keyframe snapping mode ('out', 'in', 'smart').",
        rich_help_panel="cutting behavior",
        case_sensitive=False,
    ),
    max_shift_ms: int = typer.Option(
        500,
        "--max-shift",
        help="max time shift (ms) allowed in 'smart' snap mode before contracting.",
        rich_help_panel="cutting behavior",
        min=0,
    ),
    accurate_seek: bool = typer.Option(
        False,
        "--accurate-seek",
        help="use slower, potentially more frame-accurate seek method.",
        rich_help_panel="cutting behavior",
    ),
    ignore_webm_compat: bool = typer.Option(
        False,
        "--ignore-webm-compat",
        help="allow potentially incompatible audio codecs in webm output.",
        rich_help_panel="cutting behavior",
    ),
    # advanced / technical options
    min_segment_warning: float = typer.Option(
        0.5,
        "--min-seg-warn",
        help="warn if snapped segments are shorter than this duration (seconds).",
        rich_help_panel="advanced options",
        min=0.0,
    ),
    timestamp_precision: int = typer.Option(
        6,
        "--ts-precision",
        help="decimal places for timestamps used in ffmpeg commands.",
        rich_help_panel="advanced options",
        min=0,
        max=9,
    ),
    validate_segments: bool = typer.Option(
        False,  # default validate to false for speed
        "--validate/--no-validate",
        help="validate output segment files using ffmpeg (can be slow).",
        rich_help_panel="advanced options",
    ),
    write_manifest: bool = typer.Option(
        False,  # default manifest to false for cleaner output dir
        "--manifest/--no-manifest",
        help="write a json manifest file detailing segments and shifts.",
        rich_help_panel="advanced options",
    ),
):
    """
    cut media files losslessly based on specified time segments.

    by default, merges segments into a single output file.
    use --no-merge to extract each segment to a separate file using a pattern in -o.
    aligns cuts to keyframes for perfect quality preservation.
    handles segment parsing, keyframe snapping, parallel extraction, and merging.
    """
    logger_level = ctx.obj.get("logger_level", Verbosity.INFO.value)
    start_time = time.time()

    try:
        logger.info(f"{APP_NAME} v{APP_VERSION}")

        # --- input file info ---
        input_file_size = 0
        try:
            input_file_size = input_path.stat().st_size
            logger.info(f"input file: {input_path} ({humanize_bytes(input_file_size)})")
        except Exception as e:
            logger.warn(f"could not stat input file '{input_path}': {e}")

        # --- output info & validation ---
        if no_merge:
            logger.info(
                f"output pattern: {output_path} (mode: extract individual segments)"
            )
        else:
            logger.info(f"output file: {output_path} (mode: merge segments)")

        if input_path.resolve() == output_path.resolve() and not no_merge:
            raise typer.BadParameter(
                "input and output paths must be different when merging."
            )

        # --- probe video duration for segment parsing ---
        video_duration = _probe_video_duration(input_path, ffprobe_path)
        if video_duration is None:
            logger.warn("could not determine video duration; '_' symbol in segments will not work")

        try:
            parser = SegmentParser(duration=video_duration)
            segment_specs = parser.parse(segments)
            num_segments = len(segment_specs)
            logger.info(f"parsed {num_segments} segment specifications.")
            # Display requested segments only if logger level is info or higher
            if logger_level >= Verbosity.INFO.value:
                display_requested_segment_table(segment_specs)
        except typer.BadParameter as e:
            logger.error(f"segment parsing error: {e}")
            raise typer.Exit(code=1)

        try:
            validate_output_path(
                output_path, num_segments, no_merge, dry_run, force_yes
            )
        except typer.BadParameter as e:
            logger.error(f"output path validation failed: {e}")
            raise typer.Exit(code=1)
        except typer.Exit:  # handle user cancellation from confirm prompt
            raise

        # --- initialize cutter ---
        try:
            cutter = VideoCutter(
                input_path=input_path,
                output_path=output_path,  # pass the path or pattern
                segments=segment_specs,
                logger=logger,
                no_merge=no_merge,
                temp_dir=temp_dir,
                keep_temp=keep_temp,
                validate=validate_segments,
                dry_run=dry_run,
                jobs=jobs,
                ffprobe_path=ffprobe_path,
                ffmpeg_path=ffmpeg_path,
                min_segment_warning=min_segment_warning,
                timestamp_precision=timestamp_precision,
                accurate_seek=accurate_seek,
                snap_mode=SnapMode(snap_mode.value),
                max_shift_ms=max_shift_ms,
                ignore_webm_compatibility=ignore_webm_compat,
                write_manifest=write_manifest,
            )
        except ConfigError as e:
            logger.error(f"configuration error: {e}")
            raise typer.Exit(code=1)

        # --- run cutting process ---
        run_cutting_process(cutter, logger_level, no_merge)

        # --- display summary & final report ---
        segment_info = cutter.get_segment_info()

        # Display output summary only if logger level is info or higher
        if not dry_run and logger_level >= Verbosity.INFO.value:
            display_output_summary(segment_info, no_merge)

        elapsed = time.time() - start_time
        logger.info(
            f"success! processed {len(segment_specs)} segments in {elapsed:.2f}s"
        )

        report_final_summary(
            segment_info, no_merge, output_path, input_file_size, dry_run
        )

    except (
        ConfigError,
        ProbeError,
        SnapError,
        ExtractError,
        MergeError,
        ValidateError,
        CompatibilityError,
    ) as e:
        logger.error(f"processing error: {e}")
        raise typer.Exit(code=1)
    except typer.Exit:
        raise  # allow typer exits to pass through
    except Exception as e:
        logger.error(f"an unexpected error occurred: {e}")
        # Show traceback only if logger level is debug or higher
        if logger_level >= Verbosity.DEBUG.value:
            logger.debug(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command()
def probe(
    ctx: typer.Context,
    input_path: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="input media file path.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        show_default=False,
    ),
    ffprobe_path: str = typer.Option("ffprobe", help="path to ffprobe executable."),
    output_json: Optional[Path] = typer.Option(
        None,
        "--json",
        "-j",
        help="save full ffprobe json output to a file.",
        resolve_path=True,
    ),
    show_keyframes: bool = typer.Option(
        False,
        "--keyframes",
        "-k",
        help="show keyframe information (requires ffprobe analysis, can be slow).",
    ),
):
    """
    analyze media file properties using ffprobe.

    displays format, stream info, and optionally keyframe details.
    """
    logger_level = ctx.obj.get("logger_level", Verbosity.INFO.value)
    import subprocess  # import locally as it's only used here

    # JSON imported at top level now

    try:
        logger.info(f"probing {input_path}")

        # --- basic format & stream info ---
        cmd_basic = [
            ffprobe_path,
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(input_path),
        ]
        logger.debug(f"running ffprobe basic command: {' '.join(cmd_basic)}")

        try:
            proc_basic = subprocess.run(
                cmd_basic,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            probe_data = json.loads(proc_basic.stdout)
        except FileNotFoundError:
            raise ConfigError(f"ffprobe executable not found at '{ffprobe_path}'.")
        except subprocess.CalledProcessError as e:
            raise ProbeError(
                f"ffprobe basic info failed (code {e.returncode}): {e.stderr.strip()}"
            )
        except json.JSONDecodeError as e:
            raise ProbeError(f"failed to parse ffprobe basic json output: {e}")
        except Exception as e:
            raise ProbeError(f"error running ffprobe basic command: {e}")

        # --- save json output ---
        if output_json:
            try:
                output_json.parent.mkdir(parents=True, exist_ok=True)
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(probe_data, f, indent=2, ensure_ascii=False)
                logger.info(f"full ffprobe json data saved to {output_json}")
            except Exception as e:
                logger.warn(f"failed to save json output to '{output_json}': {e}")

        # --- display parsed info ---
        format_info = probe_data.get("format", {})
        streams = probe_data.get("streams", [])

        duration = _display_probe_format_table(format_info, input_path)

        video_stream = next(
            (s for s in streams if s.get("codec_type") == "video"), None
        )
        audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
        subtitle_streams = [s for s in streams if s.get("codec_type") == "subtitle"]

        # video stream table & keyframes
        if video_stream:
            _display_probe_video_table(video_stream)
            if show_keyframes:
                logger.info("analyzing keyframes (this might take a moment)...")
                keyframes, kf_scan_method = _run_keyframe_probe(
                    ffprobe_path, input_path
                )
                _display_probe_keyframes(keyframes, kf_scan_method, duration)

        # audio streams table
        if audio_streams:
            _display_probe_audio_table(audio_streams)

        # subtitle streams table
        if subtitle_streams:
            _display_probe_subtitle_table(subtitle_streams)

    except (ConfigError, ProbeError) as e:
        logger.error(f"probe error: {e}")
        raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"unexpected error during probe: {e}")
        # Show traceback only if logger level is debug or higher
        if logger_level >= Verbosity.DEBUG.value:
            logger.debug(traceback.format_exc())
        raise typer.Exit(code=1)


# --- main execution guard ---
if __name__ == "__main__":
    app()
