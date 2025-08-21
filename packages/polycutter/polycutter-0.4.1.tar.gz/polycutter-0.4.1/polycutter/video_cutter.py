import time
import shutil
import tempfile
import subprocess
import json
import os
import shlex
from pathlib import Path
from fractions import Fraction
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)
from bisect import (
    bisect_right,
    bisect_left,
)
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from enum import Enum

from .util import humanize_bytes, format_time

# --- custom exceptions ---
# these custom exception classes help signal specific failure modes during the cutting process,
# making error handling in the cli more specific.


class ConfigError(Exception):
    """error related to configuration, paths, or segment definitions."""

    pass


class ProbeError(Exception):
    """error occurred during ffprobe execution (analyzing the input file)."""

    pass


class SnapError(Exception):
    """error occurred while snapping requested times to actual keyframes."""

    pass


class ExtractError(Exception):
    """error occurred during ffmpeg execution for extracting a single segment."""

    pass


class MergeError(Exception):
    """error occurred during ffmpeg execution for merging segments."""

    pass


class ValidateError(Exception):
    """error occurred during ffmpeg validation of an output file."""

    pass


class CompatibilityError(Exception):
    """detected an incompatible codec/container combination (e.g., non-standard audio in webm)."""

    pass


# --- enums and data classes ---


class SnapMode(str, Enum):
    """
    defines how requested segment times are adjusted ('snapped') to the nearest keyframes.
    lossless cutting requires starting cuts *exactly* at a keyframe.

    why keyframes?
    video codecs like h.264, hevc, vp9, av1 use compression techniques where most frames
    (called p-frames or b-frames) only store the *differences* from previous or future frames.
    keyframes (often i-frames or idr-frames) are self-contained and don't depend on other
    frames to be decoded. starting a cut mid-gop (group of pictures, sequence between keyframes)
    would result in a broken video because the initial p/b-frames would lack their reference frame.

    modes:
    - out: expand segment outwards. start time snaps to the keyframe *before* or at the requested start.
           end time snaps to the keyframe *after* or at the requested end. preserves all requested content.
    - in: contract segment inwards. start time snaps to the keyframe *after* or at the requested start.
          end time snaps to the keyframe *before* or at the requested end. might remove small parts at edges.
    - smart: expand outwards like 'out', but *only* if the time shift required is below a threshold
             (max_shift_ms). if the shift is too large, it contracts inwards like 'in'. this tries
             to preserve content unless it would significantly alter the segment length.
    """

    OUT = "out"
    IN = "in"
    SMART = "smart"


@dataclass(frozen=True)
class SegmentSpec:
    """
    represents a user's requested segment before keyframe snapping.
    uses fractions.fraction for timestamps to maintain absolute precision,
    avoiding floating-point inaccuracies that could cause off-by-one frame errors.
    """

    # user-requested raw times, using exact fraction-of-second precision.
    # fractions avoid floating point errors inherent in binary representation (e.g., 0.1 + 0.2 != 0.3).
    start: Fraction  # beginning timestamp requested by user (in seconds).
    end: Fraction  # ending timestamp requested by user (in seconds).
    index: int  # ordinal number (0, 1, 2...) for naming/sorting temporary files.


@dataclass(frozen=True)
class SnappedSegment:
    """
    represents a segment after its start/end times have been snapped to keyframes.
    also includes the path to the temporary file (if merging) or final output file
    (if not merging) where this segment will be extracted.
    """

    spec: SegmentSpec  # the original user specification for reference.
    snap_start: Fraction  # the actual keyframe-aligned start time (in seconds).
    snap_end: Fraction  # the actual keyframe-aligned end time (in seconds).
    target_path: Path  # path to the output file (temp or final) for this segment.


class VideoCutter:
    """
    main class orchestrating the video cutting process.

    it takes input/output paths, segment specifications, and configuration options,
    then uses ffprobe and ffmpeg to perform the lossless cut. handles both merging
    segments and extracting them to individual files.
    """

    # --- class constants for ffmpeg flags ---

    # mapping from container format names (lowercase tokens from ffprobe's 'format_name')
    # to ffmpeg flags often needed for optimal playback or compatibility.
    _FORMAT_FLAGS = {
        # mp4-family formats: '-movflags +faststart' moves the 'moov' atom
        # (containing metadata like timestamps and index) to the beginning of the file.
        # this allows web players to start playback before downloading the entire file.
        "mp4": "-movflags +faststart",
        "mov": "-movflags +faststart",
        "m4a": "-movflags +faststart",  # audio-only mp4
        "3gp": "-movflags +faststart",
        "3g2": "-movflags +faststart",
        # matroska/webm: generally don't need special flags for basic playback.
        "matroska": "",
        "webm": "",
        # mpeg transport stream: often used in broadcasting, doesn't benefit from faststart.
        "mpegts": "",
    }

    # special case: av1 codec in mp4 container.
    # requires both 'faststart' (for web playback) and 'frag_keyframe'
    # (to ensure each fragment starts with necessary headers when using fragmented mp4).
    # these flags must be joined with '+' under a single '-movflags'.
    _AV1_MP4_FLAGS = "-movflags +faststart+frag_keyframe"

    # muxer-specific flags related to timestamp handling during the *merge* step
    # (using the ffmpeg 'concat' demuxer). these help avoid timing glitches or sync issues.
    _TS_MERGE_FLAGS = {
        # mp4 family: '-muxdelay 0 -muxpreload 0' can help prevent initial buffering delays
        # or gaps when concatenating mp4 files.
        "mp4": "-muxdelay 0 -muxpreload 0",
        "mov": "-muxdelay 0 -muxpreload 0",
        "m4a": "-muxdelay 0 -muxpreload 0",
        "3gp": "-muxdelay 0 -muxpreload 0",
        "3g2": "-muxdelay 0 -muxpreload 0",
        # matroska/webm: these containers handle timestamp concatenation differently
        # and generally don't need or benefit from these specific flags.
        "matroska": "",
        "webm": "",
        # mpegts: transport streams have specific timestamp requirements.
        # '-avoid_negative_ts make_zero': prevents negative timestamps, shifting if needed.
        # '-copyts': copies timestamps directly from the input segments, important for
        #            maintaining timing accuracy, especially if the segments will be
        #            further processed (e.g., packaged for hls).
        "mpegts": "-avoid_negative_ts make_zero -copyts",
    }

    # basic information about common video codecs.
    # 'type': broad category (avc includes h.264/hevc, vp includes vp8/vp9/av1).
    # 'keyframe_type': typical name used for keyframes (idr for avc, keyframe for vp/av1).
    # 'requires_closed_gop': whether clean cuts typically require 'closed gops'.
    #   - closed gop: a group of pictures where all frames within the gop *only* reference
    #                 frames *within the same gop*. ensures the gop can be decoded independently.
    #   - open gop: frames (especially b-frames) near the end of a gop might reference
    #               frames in the *next* gop. cutting at the end of an open gop can lead
    #               to artifacts in the next segment's beginning. h.264/hevc often use
    #               closed gops for editing friendliness, while vp/av1 handle this differently.
    _CODEC_INFO = {
        "h264": {"type": "avc", "keyframe_type": "idr", "requires_closed_gop": True},
        "hevc": {"type": "avc", "keyframe_type": "idr", "requires_closed_gop": True},
        "vp8": {
            "type": "vp",
            "keyframe_type": "keyframe",
            "requires_closed_gop": False,
        },
        "vp9": {
            "type": "vp",
            "keyframe_type": "keyframe",
            "requires_closed_gop": False,
        },
        "av1": {
            "type": "vp",
            "keyframe_type": "keyframe",
            "requires_closed_gop": False,
        },
        # add more codecs as needed
    }

    # official list of audio codecs allowed in the webm container format.
    # attempting to mux other audio codecs (like aac) into webm can cause playback issues.
    _WEBM_AUDIO_CODECS = ["vorbis", "opus", "flac"]

    # set of container formats based on the iso base media file format (ismf) or quicktime.
    # these often share similar internal structures and benefit from flags like 'faststart'.
    _MP4_FAMILY = {"mp4", "mov", "m4a", "3gp", "3g2"}

    def __init__(
        self,
        input_path: Path,
        output_path: Path,  # can be path or pattern
        segments: List[SegmentSpec],
        logger,  # expects a minlog logger instance
        *,  # force subsequent arguments to be keyword-only
        no_merge: bool = False,  # flag to control merging
        temp_dir: Optional[Path] = None,  # allow user to specify temp dir
        keep_temp: bool = False,  # option to keep intermediate files/dir
        validate: bool = True,  # run ffmpeg validation on output files
        dry_run: bool = False,  # plan cuts but don't execute ffmpeg commands
        jobs: Optional[
            int
        ] = None,  # number of parallel extraction jobs (default: auto)
        ffprobe_path: str = "ffprobe",  # path to ffprobe executable
        ffmpeg_path: str = "ffmpeg",  # path to ffmpeg executable
        min_segment_warning: float = 0.5,  # warn if snapped segments are very short
        timestamp_precision: int = 6,  # decimal places for timestamps in ffmpeg commands (microseconds)
        accurate_seek: bool = False,  # use slower but potentially more precise seeking
        snap_mode: SnapMode = SnapMode.OUT,  # keyframe snapping strategy
        max_shift_ms: int = 500,  # threshold for 'smart' snap mode
        ignore_webm_compatibility: bool = False,  # allow incompatible audio in webm
        write_manifest: bool = True,  # output a json file detailing the cuts
    ):
        """
        initializes the video cutter instance.

        sets up paths, configuration, and validates basic requirements like directory writability.
        """
        # store configuration parameters. use pathlib for robust path handling.
        self.input_path = Path(input_path)
        # output_path is the single file path if merging, or the pattern if not merging
        self.output_path_or_pattern = Path(output_path)
        self.segments = segments  # list of user-requested segment specs
        self.logger = logger
        self.no_merge = no_merge
        self.keep_temp = keep_temp
        self.validate = validate
        self.dry_run = dry_run
        # determine number of parallel jobs: use user value if valid, otherwise cpu count (min 1).
        self.jobs = (
            jobs if jobs is not None and jobs > 0 else max(1, os.cpu_count() or 1)
        )
        self.ffprobe_path = ffprobe_path
        self.ffmpeg_path = ffmpeg_path
        self.min_segment_warning = min_segment_warning
        self.timestamp_precision = timestamp_precision
        self.accurate_seek = accurate_seek
        self.snap_mode = snap_mode
        self.max_shift_ms = max_shift_ms
        self.ignore_webm_compatibility = ignore_webm_compatibility
        self.write_manifest = write_manifest

        self.logger.info("→ initializing video cutter")
        self.logger.debug("→ configuration:")
        self.logger.debug(f"    input: {self.input_path}")
        if self.no_merge:
            self.logger.debug(f"    output pattern: {self.output_path_or_pattern}")
            self.logger.debug("    mode: extract individual segments (--no-merge)")
        else:
            self.logger.debug(f"    output file: {self.output_path_or_pattern}")
            self.logger.debug("    mode: merge segments")
        self.logger.debug(f"    segments: {len(self.segments)} requested")
        self.logger.debug(f"    temp dir: {'user-specified' if temp_dir else 'auto'}")
        self.logger.debug(f"    keep temp: {self.keep_temp}")
        self.logger.debug(f"    validate output: {self.validate}")
        self.logger.debug(f"    dry run: {self.dry_run}")
        self.logger.debug(f"    jobs: {self.jobs}")
        self.logger.debug(f"    ffprobe: {self.ffprobe_path}")
        self.logger.debug(f"    ffmpeg: {self.ffmpeg_path}")
        self.logger.debug(f"    snap mode: {self.snap_mode.value}")
        self.logger.debug(f"    smart snap threshold: {self.max_shift_ms}ms")
        self.logger.debug(f"    accurate seek: {self.accurate_seek}")
        self.logger.debug(f"    ignore webm compat: {self.ignore_webm_compatibility}")
        self.logger.debug(f"    write manifest: {self.write_manifest}")

        # --- determine output directory (used for temp dir placement if not specified) ---
        if self.no_merge:
            # derive directory from pattern
            try:
                # use index 1 as sample, doesn't matter if it will actually exist
                sample_path = Path(str(self.output_path_or_pattern).format(1))
                self._output_dir = sample_path.parent
            except Exception as e:
                raise ConfigError(
                    f"invalid output pattern format '{self.output_path_or_pattern}': {e}"
                )
        else:
            # directory is simply the parent of the single output file
            self._output_dir = self.output_path_or_pattern.parent

        # --- validate output directory writability (already done in cli, but good safety check) ---
        try:
            self._output_dir.mkdir(parents=True, exist_ok=True)
            test_file = self._output_dir / f".polycut_write_test_{os.getpid()}"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            raise ConfigError(
                f"output directory '{self._output_dir}' is not writable: {e}"
            )

        # --- set up temporary directory ---
        # temporary directory is still needed for keyframe scans, concat list (if merging), etc.
        if temp_dir:
            # user provided a temp directory path.
            self.temp_dir_base = Path(temp_dir)
            self._temp_dir_created = False  # flag indicating we didn't create it
            try:
                self.temp_dir_base.mkdir(parents=True, exist_ok=True)
                test_file = self.temp_dir_base / f".polycut_write_test_{os.getpid()}"
                test_file.touch()
                test_file.unlink()
                # use a subdirectory within the user's temp dir to avoid potential conflicts
                self.temp_dir = Path(
                    tempfile.mkdtemp(prefix="polycut_", dir=self.temp_dir_base)
                )
            except Exception as e:
                raise ConfigError(
                    f"provided temp directory '{self.temp_dir_base}' is not usable: {e}"
                )
        else:
            # create a temporary directory automatically.
            # place it in the determined output directory, hidden by default.
            self.temp_dir_base = self._output_dir
            # use mkdtemp for guaranteed unique temporary directory name.
            self.temp_dir = Path(
                tempfile.mkdtemp(prefix=".polycut_temp_", dir=self.temp_dir_base)
            )
            self._temp_dir_created = True  # flag indicating we created it
            self.logger.debug(f"→ created temporary directory: {self.temp_dir}")

        # --- initialize internal state variables ---
        self._idr_pts: List[Fraction] = (
            []
        )  # list to store keyframe timestamps (as fractions)
        self.snapped: List[SnappedSegment] = []  # list to store segments after snapping
        self.codec: Optional[str] = None  # detected video codec name
        self.container_formats: Optional[List[str]] = (
            None  # detected container format names
        )
        self._probe_cache: Dict[str, Any] = {}  # cache for ffprobe results
        self.duration: Optional[Fraction] = None  # total duration of the input file
        self._final_output_paths: List[str] = (
            []
        )  # list to store final output file paths

    def run(self):
        """
        executes the entire cutting pipeline: probe, validate, scan, snap, extract,
        (optionally) merge, (optionally) validate, cleanup.
        """
        self.logger.info("→ starting cutting pipeline")
        start_time = time.time()  # for overall timing

        try:
            # 1. analyze input file: detect codec, container, duration.
            self._detect_media_properties()

            # 2. validate segments: check times are within duration, sort, check overlaps.
            self.load_and_validate_segments()

            # 3. find keyframes: use ffprobe to get precise timestamps of keyframes.
            self.scan_keyframes()

            # 4. check gop structure (optional but recommended for some codecs).
            codec_info = self._CODEC_INFO.get(self.codec or "", {})
            if codec_info.get("requires_closed_gop"):
                self.verify_closed_gop()

            # 5. check for potential codec/container compatibility issues.
            self._check_compatibility()

            # 6. snap segments: adjust requested start/end times to actual keyframe times.
            # this also determines the target output path for each segment.
            self.snap_segments()

            # 7. extract segments: run ffmpeg in parallel to create segment files
            # (either temporary or final based on no_merge flag).
            self.extract_all_segments()

            # 8. merge segments (only if no_merge is false).
            if not self.no_merge:
                self.merge_segments()
                # add the single merged output path to the list for the manifest
                self._final_output_paths = [str(self.output_path_or_pattern.resolve())]
            # else: final paths were added during extract_all_segments

            # 9. write manifest (optional): create a json file describing the cuts.
            segment_info = (
                self.get_segment_info()
            )  # get data regardless of writing file
            if self.write_manifest and not self.dry_run:
                self._write_segment_manifest(segment_info)

            # 10. validate output (optional):
            # if merging, validate the final merged file.
            # if not merging, validation happens individually within _extract_segment.
            if self.validate and not self.no_merge and not self.dry_run:
                final_output_path = self.output_path_or_pattern
                if final_output_path.exists() and final_output_path.is_file():
                    self._validate_file(final_output_path, "final merged output")
                else:
                    self.logger.warn(
                        f"skipping validation: final merged file {final_output_path} not found."
                    )

            elapsed_time = time.time() - start_time
            self.logger.info(f"→ pipeline finished successfully in {elapsed_time:.2f}s")

        except (
            ConfigError,
            ProbeError,
            SnapError,
            ExtractError,
            MergeError,
            ValidateError,
            CompatibilityError,
        ) as e:
            # catch specific errors from the cutting process and log them.
            self.logger.error(f"pipeline failed: {e}")
            # re-raise the exception so the cli can catch it and exit appropriately.
            raise
        except Exception as e:
            # catch unexpected errors.
            self.logger.error(f"unexpected error during pipeline: {e}")
            # log traceback if in debug mode.
            if self.logger.level <= Verbosity.DEBUG.value:  # use enum value for check
                import traceback

                self.logger.debug(traceback.format_exc())
            raise  # re-raise for cli handling
        finally:
            # 11. cleanup: remove temporary directory unless requested otherwise.
            # this runs even if errors occurred during the pipeline.
            self.cleanup()

    # --- internal helper methods for media properties ---

    def _is_mp4_family(self) -> bool:
        """checks if the detected container format belongs to the mp4/mov family."""
        if not self.container_formats:
            return False
        # check if any of the detected format names are in our predefined set.
        return any(fmt in self._MP4_FAMILY for fmt in self.container_formats)

    def _is_container_type(self, container_type: str) -> bool:
        """checks if a specific container type (e.g., 'webm') was detected."""
        if not self.container_formats:
            return False
        return container_type.lower() in self.container_formats

    def _check_compatibility(self):
        """warns about or prevents known incompatible codec/container combinations."""
        self.logger.debug("→ checking codec/container compatibility")
        if not self.codec or not self.container_formats:
            self.logger.debug(
                "→ skipping compatibility check (codec or container unknown)"
            )
            return

        # example: vp8/vp9 in mp4 is technically allowed by some specs but poorly supported by players.
        if self.codec in ["vp8", "vp9"] and self._is_mp4_family():
            self.logger.warn(
                f"unusual combination: {self.codec} codec in an mp4-family container."
            )
            self.logger.warn(
                "this is valid but may not be playable in all applications."
            )

        # strict check for webm: only specific audio codecs are allowed by the standard.
        if self._is_container_type("webm"):
            try:
                # probe for audio streams specifically.
                audio_info = self._probe_streams("a")  # 'a' for audio
                if not audio_info or not audio_info.get("streams"):
                    self.logger.debug(
                        "→ no audio streams found in webm, skipping codec check."
                    )
                    return

                for stream in audio_info.get("streams", []):
                    audio_codec = stream.get("codec_name")
                    if audio_codec and audio_codec not in self._WEBM_AUDIO_CODECS:
                        # found an incompatible audio codec.
                        msg = (
                            f"incompatible audio codec '{audio_codec}' found in webm container. "
                            f"webm standard only supports: {', '.join(self._WEBM_AUDIO_CODECS)}."
                        )

                        if not self.ignore_webm_compatibility:
                            # raise an error unless the user explicitly overrides.
                            raise CompatibilityError(
                                msg + " use --ignore-webm-compat to force."
                            )
                        else:
                            # log a warning if overriding.
                            self.logger.warn(
                                msg + " proceeding due to --ignore-webm-compat flag."
                            )
            except ProbeError as e:
                # log if probing audio streams failed, but don't stop the process.
                self.logger.warn(f"could not verify webm audio compatibility: {e}")
            except CompatibilityError:
                # re-raise compatibility errors directly if not ignoring.
                raise
            except Exception as e:
                # log other unexpected errors during the check.
                self.logger.warn(f"error during webm audio compatibility check: {e}")

    def _detect_media_properties(self):
        """uses ffprobe to detect codec, container format, and duration."""
        self.logger.info("→ detecting media properties (codec, container, duration)")

        # --- probe basic format and stream info ---
        format_info = self._probe_format()
        if not format_info:
            # if basic probing failed, we can't proceed reliably.
            raise ProbeError(
                "failed to retrieve basic format/stream information from input file."
            )

        self._probe_cache["format"] = format_info
        # extract duration from the cached format info if available.
        duration_str = format_info.get("format", {}).get("duration")
        if duration_str:
            try:
                # use decimal for intermediate step to avoid float issues with fraction.
                self.duration = Fraction(Decimal(duration_str))
                self.logger.info(
                    f"→ detected duration: {format_time(float(self.duration))} ({float(self.duration):.3f}s)"
                )
            except (ValueError, TypeError) as e:
                self.logger.warn(f"→ could not parse duration '{duration_str}': {e}")
        else:
            self.logger.warn("→ duration not found in format info.")

        # if duration wasn't found in the initial probe, try a specific duration probe.
        if self.duration is None:
            try:
                self.duration = self._probe_duration()
                self.logger.info(
                    f"→ detected duration (separate probe): {format_time(float(self.duration))} ({float(self.duration):.3f}s)"
                )
            except ProbeError as e:
                # if duration probe fails here, it's critical for segment validation.
                raise ProbeError(f"failed to determine media duration: {e}")

        # --- detect video codec ---
        # attempt to get codec from the cached format info first.
        video_stream = next(
            (
                s
                for s in format_info.get("streams", [])
                if s.get("codec_type") == "video"
            ),
            None,
        )
        if video_stream:
            self.codec = video_stream.get("codec_name")

        # if not found in cache, probe specifically for video streams (should be rare now).
        if not self.codec:
            video_streams_info = self._probe_streams("v")  # 'v' for video
            if (
                video_streams_info
                and "streams" in video_streams_info
                and video_streams_info["streams"]
            ):
                # take the codec from the first video stream found.
                self.codec = video_streams_info["streams"][0].get("codec_name")

        # log detected codec info.
        if self.codec:
            codec_details = self._CODEC_INFO.get(self.codec, {})
            kf_type = codec_details.get("keyframe_type", "unknown")
            closed_gop = codec_details.get("requires_closed_gop", "unknown")
            self.logger.info(
                f"→ detected video codec: {self.codec} (keyframe: {kf_type}, needs closed gop: {closed_gop})"
            )
        else:
            # warning, as lossless cutting relies heavily on video stream properties.
            self.logger.warn(
                "→ unable to detect video codec. proceeding may have unexpected results."
            )

        # --- detect container format(s) ---
        # use cached format info if available.
        format_name_str = format_info.get("format", {}).get("format_name", "")
        if format_name_str:
            # format_name can be comma-separated (e.g., "mov,mp4,m4a"). split into a list.
            self.container_formats = [fmt.strip() for fmt in format_name_str.split(",")]

        # if not in cache, probe specifically for the format name (should be rare now).
        if not self.container_formats:
            self.container_formats = self._probe_container_format_direct()

        # log detected container formats.
        if self.container_formats:
            self.logger.info(
                f"→ detected container formats: {', '.join(self.container_formats)}"
            )
        else:
            self.logger.warn("→ unable to detect container format.")

    def _run_probe(self, cmd: List[str], description: str) -> Optional[Dict[str, Any]]:
        """helper to run ffprobe, parse json output, and handle errors."""
        self.logger.debug(f"→ running ffprobe ({description}): {' '.join(cmd)}")
        try:
            # run ffprobe command. capture output, treat as utf-8 (ignoring errors).
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",  # replace invalid utf-8 sequences
                check=False,  # don't raise exception on non-zero exit code here
            )

            # check ffprobe's return code.
            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                self.logger.error(
                    f"ffprobe failed ({description}). exit code: {proc.returncode}"
                )
                self.logger.error(
                    f"ffprobe stderr: {stderr if stderr else 'no stderr output'}"
                )
                # raise specific probeerror for upstream handling.
                raise ProbeError(f"ffprobe command failed for {description}.")

            # check if stdout is empty.
            if not proc.stdout.strip():
                self.logger.warn(f"ffprobe ({description}) produced no output.")
                return None

            # parse the json output.
            return json.loads(proc.stdout)

        except subprocess.TimeoutExpired:
            self.logger.error(f"ffprobe command timed out ({description}).")
            raise ProbeError(f"ffprobe command timed out for {description}.")
        except json.JSONDecodeError as e:
            self.logger.error(
                f"failed to parse ffprobe json output ({description}): {e}"
            )
            self.logger.debug(
                f"raw ffprobe output:\n{proc.stdout[:500]}..."
            )  # log snippet
            raise ProbeError(f"could not parse ffprobe output for {description}.")
        except FileNotFoundError:
            self.logger.error(f"ffprobe executable not found at '{self.ffprobe_path}'.")
            raise ConfigError(
                f"ffprobe not found at '{self.ffprobe_path}'. please check path."
            )
        except Exception as e:
            # catch any other unexpected errors during probing.
            self.logger.error(
                f"an unexpected error occurred during ffprobe ({description}): {e}"
            )
            raise ProbeError(f"unexpected error during ffprobe for {description}: {e}")

    def _probe_format(self) -> Optional[Dict[str, Any]]:
        """probes general format and stream information using ffprobe."""
        cache_key = "format"
        if cache_key in self._probe_cache:
            return self._probe_cache[cache_key]

        cmd = [
            self.ffprobe_path,
            "-v",
            "error",  # suppress verbose logging, only show errors
            "-show_format",  # request container format information
            "-show_streams",  # request information about all streams
            "-of",
            "json",  # output format as json
            str(self.input_path),  # input file path
        ]
        result = self._run_probe(cmd, "basic format/stream info")
        if result:
            self._probe_cache[cache_key] = result
        return result

    def _probe_streams(self, stream_type_specifier: str) -> Optional[Dict[str, Any]]:
        """probes for specific stream types (e.g., 'v' for video, 'a' for audio)."""
        cache_key = f"streams_{stream_type_specifier}"
        if cache_key in self._probe_cache:
            return self._probe_cache[cache_key]

        cmd = [
            self.ffprobe_path,
            "-v",
            "error",
            "-select_streams",
            stream_type_specifier,  # select only streams of this type
            "-show_streams",  # request details about the selected streams
            "-of",
            "json",
            str(self.input_path),
        ]
        result = self._run_probe(cmd, f"{stream_type_specifier} stream info")
        # cache even if result is none to avoid retrying failed probes
        self._probe_cache[cache_key] = result
        return result

    def _probe_container_format_direct(self) -> Optional[List[str]]:
        """probes specifically for the container format name if not found earlier."""
        cache_key = "container_format_direct"
        if cache_key in self._probe_cache:
            return self._probe_cache[cache_key]

        cmd = [
            self.ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=format_name",  # request only the format_name field
            "-of",
            "json",
            str(self.input_path),
        ]
        result = self._run_probe(cmd, "container format")
        if result and "format" in result and "format_name" in result["format"]:
            format_name_str = result["format"]["format_name"]
            formats = [fmt.strip() for fmt in format_name_str.split(",")]
            self._probe_cache[cache_key] = formats
            return formats
        else:
            self._probe_cache[cache_key] = None  # cache failure
            return None

    def _probe_duration(self) -> Fraction:
        """probes specifically for the media duration."""
        cache_key = "duration"
        cached_val = self._probe_cache.get(cache_key)
        if isinstance(cached_val, Fraction):
            return cached_val
        if isinstance(
            cached_val, (str, int, float)
        ):  # check if cached from format probe
            try:
                duration_frac = Fraction(Decimal(str(cached_val)))
                self._probe_cache[cache_key] = (
                    duration_frac  # update cache with fraction
                )
                return duration_frac
            except (ValueError, TypeError):
                pass  # ignore if cached value wasn't a valid duration string

        # if not in cache or cached value was invalid, probe directly.
        cmd = [
            self.ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=duration",  # request only the duration field
            "-of",
            "default=noprint_wrappers=1:nokey=1",  # print only value
            str(self.input_path),
        ]
        self.logger.debug(f"→ running ffprobe (duration): {' '.join(cmd)}")
        try:
            # run probe, get stdout directly
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
            )
            duration_str = proc.stdout.strip()
            if not duration_str or duration_str.lower() == "n/a":
                raise ProbeError("duration reported as n/a or empty by ffprobe.")
            # use decimal for intermediate conversion
            duration_frac = Fraction(Decimal(duration_str))
            self._probe_cache[cache_key] = duration_frac  # cache the result as fraction
            return duration_frac
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip() if e.stderr else "no stderr"
            self.logger.error(
                f"ffprobe duration command failed. exit code: {e.returncode}"
            )
            self.logger.error(f"ffprobe stderr: {stderr}")
            raise ProbeError("failed to probe duration: ffprobe command failed.")
        except (ValueError, TypeError) as e:
            self.logger.error(
                f"failed to parse duration '{duration_str}' from ffprobe: {e}"
            )
            raise ProbeError(f"could not parse duration '{duration_str}' from ffprobe.")
        except FileNotFoundError:
            self.logger.error(f"ffprobe executable not found at '{self.ffprobe_path}'.")
            raise ConfigError(f"ffprobe not found at '{self.ffprobe_path}'.")
        except Exception as e:
            self.logger.error(
                f"an unexpected error occurred during duration probe: {e}"
            )
            raise ProbeError(f"unexpected error during duration probe: {e}")

    # --- segment validation and manipulation ---

    def load_and_validate_segments(self):
        """validates user-provided segment specifications."""
        self.logger.info("→ validating segment specifications")

        # ensure duration was successfully probed earlier.
        if self.duration is None:
            raise ConfigError(
                "cannot validate segments: media duration could not be determined."
            )

        # convert min warning threshold to fraction for comparison
        min_warning_frac = Fraction(str(self.min_segment_warning))

        validated_segments: List[SegmentSpec] = []
        for i, seg in enumerate(self.segments):
            seg_id = f"segment {seg.index} ({i+1})"  # for logging

            # basic checks: start before end, non-negative times.
            if seg.start < 0:
                raise ConfigError(
                    f"{seg_id} has negative start time: {float(seg.start):.3f}s"
                )
            if seg.end <= seg.start:
                raise ConfigError(
                    f"{seg_id} has end time <= start time: start={float(seg.start):.3f}s, end={float(seg.end):.3f}s"
                )

            # check against media duration.
            if seg.start >= self.duration:
                raise ConfigError(
                    f"{seg_id} start time {float(seg.start):.3f}s is at or after "
                    f"media duration {float(self.duration):.3f}s"
                )
            if seg.end > self.duration:
                self.logger.warn(
                    f"{seg_id} end time {float(seg.end):.3f}s exceeds media duration "
                    f"{float(self.duration):.3f}s. clamping end time."
                )
                # clamp end time to duration. create a new spec object as they are frozen.
                seg = SegmentSpec(start=seg.start, end=self.duration, index=seg.index)
                # re-check if clamping made duration zero or negative.
                if seg.end <= seg.start:
                    raise ConfigError(
                        f"{seg_id} became invalid after clamping end time to duration."
                    )

            # check for very short segments (after potential clamping).
            seg_duration = seg.end - seg.start
            if seg_duration < min_warning_frac:
                self.logger.warn(
                    f"{seg_id} requested duration ({float(seg_duration):.3f}s) is very short."
                )

            validated_segments.append(seg)

        # sort segments by start time for deterministic processing and overlap checks.
        validated_segments.sort(key=lambda s: s.start)

        # check for overlaps between consecutive segments (after sorting).
        for j in range(len(validated_segments) - 1):
            seg_a = validated_segments[j]
            seg_b = validated_segments[j + 1]
            # overlap occurs if the end of segment 'a' is strictly after the start of segment 'b'.
            if seg_a.end > seg_b.start:
                raise ConfigError(
                    f"segments overlap: segment {seg_a.index} ({float(seg_a.start):.3f}-{float(seg_a.end):.3f}s) "
                    f"overlaps with segment {seg_b.index} ({float(seg_b.start):.3f}-{float(seg_b.end):.3f}s)"
                )

        self.segments = validated_segments  # update with validated (and potentially clamped) segments.
        self.logger.info(f"→ {len(self.segments)} segment specs validated and sorted.")

    # --- keyframe scanning ---

    def scan_keyframes(self):
        """
        finds keyframe timestamps using ffprobe. tries multiple methods for robustness.

        methods attempted (fastest to slowest):
        1. packet flags scan (`-show_packets`): very fast, reads packet metadata without decoding.
        2. i-slice scan (`-skip_frame nokey`): decodes *only* keyframes (i-frames/slices).
        3. full frame decode scan (`-show_frames`): slowest, decodes *all* frames.

        stores results in `self._idr_pts` as a sorted list of unique fractions.
        writes intermediate scan results to the temporary directory.
        """
        codec_info = self._CODEC_INFO.get(self.codec or "", {})
        keyframe_desc = codec_info.get("keyframe_type", "keyframe")
        self.logger.info(
            f"→ scanning for {keyframe_desc}s (codec: {self.codec or 'unknown'})"
        )

        # attempt methods in order, stopping once keyframes are found.
        scan_methods = [
            ("packet flags", self._scan_keyframes_packets),
            ("i-slice (skip_frame nokey)", self._scan_keyframes_i_slices),
            ("full frame decode", self._scan_keyframes_frame_by_frame),
        ]

        for name, method in scan_methods:
            self.logger.debug(f"→ attempting keyframe scan method: {name}")
            try:
                method()  # call the scanning function
                if self._idr_pts:
                    self.logger.info(
                        f"→ {name} scan successful: found {len(self._idr_pts)} keyframes."
                    )
                    self._post_scan_validation(name)
                    return  # exit loop once keyframes are found
                else:
                    self.logger.warn(
                        f"→ {name} scan completed but found no keyframes. trying next method..."
                    )
            except ProbeError as e:
                self.logger.warn(f"→ {name} scan failed: {e}. trying next method...")
            except Exception as e:
                self.logger.warn(
                    f"→ unexpected error during {name} scan: {e}. trying next method..."
                )

        # if we finish the loop without finding keyframes
        if not self._idr_pts:
            raise SnapError(
                "failed to find any keyframes using all available scan methods. cannot perform lossless cut."
            )

    def _run_keyframe_scan_command(self, cmd: List[str], output_path: Path, name: str):
        """helper to run an ffprobe command and write stdout directly to a file."""
        self.logger.debug(f"→ running ffprobe ({name} scan): {' '.join(cmd)}")
        try:
            # ensure temp dir exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # use subprocess.run with stdout redirection to file
            with output_path.open("wb") as outfile:
                proc = subprocess.run(
                    cmd,
                    stdout=outfile,
                    stderr=subprocess.PIPE,
                    check=False,
                    encoding="utf-8",
                    errors="replace",
                )
                if proc.returncode != 0:
                    stderr = proc.stderr.strip()
                    raise ProbeError(
                        f"{name} scan command failed (code {proc.returncode}). "
                        f"stderr: {stderr if stderr else 'none'}"
                    )
        except FileNotFoundError:
            raise ConfigError(f"ffprobe not found at '{self.ffprobe_path}'.")
        except Exception as e:
            raise ProbeError(f"error executing {name} scan command: {e}")

    def _parse_keyframe_csv(
        self,
        path: Path,
        time_field_index: int,
        key_flag_index: Optional[int] = None,
        key_flag_value: str = "K",
    ) -> List[Fraction]:
        """parses csv output from ffprobe keyframe scans."""
        pts = set()  # use set for automatic deduplication
        malformed_lines = 0
        non_keyframe_lines = 0
        invalid_ts = 0

        if not path.exists() or path.stat().st_size == 0:
            self.logger.debug(f"→ keyframe scan output file empty or missing: {path}")
            return []

        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue  # skip empty lines

                    parts = line.split(",")
                    # basic validation of line structure
                    if len(parts) <= time_field_index or (
                        key_flag_index is not None and len(parts) <= key_flag_index
                    ):
                        malformed_lines += 1
                        if malformed_lines < 10:  # log first few malformed lines
                            self.logger.trace(
                                f"→ malformed csv line #{line_num+1} in {path.name}: {line}"
                            )
                        continue

                    # check keyframe flag if specified
                    if key_flag_index is not None:
                        flags = parts[key_flag_index]
                        # case-insensitive check for 'k' in packet flags
                        is_keyframe = (
                            (key_flag_value.lower() in flags.lower())
                            if key_flag_value == "K"
                            else (flags == key_flag_value)
                        )
                        if not is_keyframe:
                            non_keyframe_lines += 1
                            continue

                    # extract timestamp string
                    ts_str = parts[time_field_index]
                    if not ts_str or ts_str.lower() == "n/a":
                        invalid_ts += 1
                        if invalid_ts < 10:
                            self.logger.trace(
                                f"→ invalid timestamp 'n/a' on line #{line_num+1} in {path.name}"
                            )
                        continue

                    # convert timestamp string to fraction
                    try:
                        # use decimal for intermediate conversion for robustness
                        pts.add(Fraction(Decimal(ts_str)))
                    except (ValueError, TypeError):
                        invalid_ts += 1
                        if invalid_ts < 10:  # log first few invalid timestamps
                            self.logger.trace(
                                f"→ invalid timestamp format on line #{line_num+1} in {path.name}: {ts_str}"
                            )

        except Exception as e:
            self.logger.warn(f"error reading or parsing keyframe csv {path.name}: {e}")
            return []  # return empty list on error

        if malformed_lines > 0:
            self.logger.debug(
                f"→ skipped {malformed_lines} malformed lines in {path.name}."
            )
        if non_keyframe_lines > 0:
            self.logger.debug(
                f"→ skipped {non_keyframe_lines} non-keyframe lines in {path.name}."
            )
        if invalid_ts > 0:
            self.logger.debug(
                f"→ skipped {invalid_ts} invalid timestamps in {path.name}."
            )

        return sorted(list(pts))

    def _scan_keyframes_packets(self):
        """attempts keyframe scan using packet flags (-show_packets)."""
        path = self.temp_dir / "keyframes_packet_scan.csv"
        cmd = [
            self.ffprobe_path,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_packets",
            "-show_entries",
            "packet=pts_time,flags",
            "-of",
            "csv=p=0",
            str(self.input_path),
        ]
        try:
            self._run_keyframe_scan_command(cmd, path, "packet flags")
        except ProbeError as e:
            self.logger.warn(f"→ packet flags scan failed: {e}")
            self._idr_pts = []
            return  # allow next method

        # parse the output: format is pts_time,flags
        # look for 'k' (case-insensitive) in the flags (index 1)
        try:
            self._idr_pts = self._parse_keyframe_csv(
                path, time_field_index=0, key_flag_index=1, key_flag_value="K"
            )
            self.logger.trace(
                f"→ parsed {len(self._idr_pts)} keyframes from packet scan output {path.name}"
            )
        except Exception as parse_err:
            self.logger.warn(
                f"failed to parse packet scan output {path.name}: {parse_err}. trying next method..."
            )
            self._idr_pts = []

    def _scan_keyframes_i_slices(self):
        """attempts keyframe scan using i-slice decoding (-skip_frame nokey)."""
        path = self.temp_dir / "keyframes_iframe_scan.csv"
        cmd = [
            self.ffprobe_path,
            "-v",
            "error",
            "-skip_frame",
            "nokey",
            "-select_streams",
            "v:0",
            "-show_entries",
            "frame=key_frame,pts_time,best_effort_timestamp_time",
            "-of",
            "csv=p=0",
            str(self.input_path),
        ]
        try:
            self._run_keyframe_scan_command(cmd, path, "i-slice (skip_frame nokey)")
        except ProbeError as e:
            self.logger.warn(
                f"→ i-slice scan command potentially failed (may indicate no keyframes): {e}"
            )
            self._idr_pts = []
            return  # allow next method

        # parse the csv output: key_frame, pts_time, best_effort_timestamp_time
        # prefer best_effort (index 2), fallback to pts_time (index 1)
        pts = set()
        malformed_lines = 0
        invalid_ts_count = 0

        if not path.exists() or path.stat().st_size == 0:
            self.logger.debug(f"→ i-slice scan output file empty or missing: {path}")
            self._idr_pts = []
            return

        try:
            with path.open("r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(",")
                    if len(parts) < 3:
                        malformed_lines += 1
                        continue

                    ts_str_best = parts[2]
                    ts_str_pts = parts[1]
                    ts_str = ""

                    if ts_str_best and ts_str_best.lower() != "n/a":
                        ts_str = ts_str_best
                    elif ts_str_pts and ts_str_pts.lower() != "n/a":
                        ts_str = ts_str_pts
                    else:
                        invalid_ts_count += 1
                        continue  # skip if both timestamps are invalid

                    try:
                        pts.add(Fraction(Decimal(ts_str)))
                    except (ValueError, TypeError):
                        invalid_ts_count += 1
                        if invalid_ts_count < 10:
                            self.logger.trace(
                                f"→ invalid timestamp format '{ts_str}' on line #{line_num+1} in {path.name}"
                            )

        except Exception as e:
            self.logger.warn(
                f"error reading or parsing i-slice scan csv {path.name}: {e}"
            )
            self._idr_pts = []
            return

        if malformed_lines > 0:
            self.logger.debug(
                f"→ skipped {malformed_lines} malformed lines in {path.name}."
            )
        if invalid_ts_count > 0:
            self.logger.debug(
                f"→ skipped {invalid_ts_count} invalid timestamps in {path.name}."
            )

        self._idr_pts = sorted(list(pts))
        self.logger.trace(
            f"→ parsed {len(self._idr_pts)} keyframes from i-slice scan output {path.name}"
        )

    def _scan_keyframes_frame_by_frame(self):
        """attempts keyframe scan using full frame decoding (-show_frames json)."""
        # note: this method is slow and outputs json
        path = self.temp_dir / "keyframes_full_frame_scan.json"
        cmd = [
            self.ffprobe_path,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_frames",
            "-show_entries",
            "frame=key_frame,pts_time,best_effort_timestamp_time",
            "-of",
            "json",
            str(self.input_path),
        ]
        try:
            result = self._run_probe(cmd, "full frame decode")
            if not result or "frames" not in result:
                self.logger.warn("→ full frame scan result missing 'frames' data.")
                self._idr_pts = []
                return
        except ProbeError as e:
            self.logger.warn(f"→ full frame scan command failed: {e}")
            self._idr_pts = []
            return
        except Exception as e:  # catch other errors like json parsing
            self.logger.warn(f"→ error during full frame scan processing: {e}")
            self._idr_pts = []
            return

        # write the received json to the temp file for potential debugging
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        except Exception as write_err:
            self.logger.warn(
                f"could not write full frame scan json to {path}: {write_err}"
            )

        # parse the json data
        pts = set()
        invalid_ts_count = 0
        non_keyframe_count = 0
        frames_processed = 0
        for frame in result.get("frames", []):
            frames_processed += 1
            if frame.get("key_frame") != 1:  # check key_frame flag
                non_keyframe_count += 1
                continue

            # extract timestamp, preferring best_effort_timestamp_time
            ts_str_best = frame.get("best_effort_timestamp_time")
            ts_str_pts = frame.get("pts_time")
            ts_str = ""

            # check validity carefully, including 'n/a' and numeric types
            if isinstance(ts_str_best, str) and ts_str_best.lower() != "n/a":
                ts_str = ts_str_best
            elif isinstance(ts_str_pts, str) and ts_str_pts.lower() != "n/a":
                ts_str = ts_str_pts
            elif isinstance(ts_str_best, (int, float)):
                ts_str = str(ts_str_best)
            elif isinstance(ts_str_pts, (int, float)):
                ts_str = str(ts_str_pts)
            else:
                invalid_ts_count += 1
                continue  # skip if no valid timestamp found

            # convert to fraction
            try:
                pts.add(Fraction(Decimal(ts_str)))
            except (ValueError, TypeError):
                invalid_ts_count += 1
                if invalid_ts_count < 10:
                    self.logger.trace(
                        f"→ invalid timestamp format in full frame scan json: {ts_str}"
                    )

        self.logger.debug(f"→ full frame scan processed {frames_processed} frames.")
        if non_keyframe_count > 0:
            self.logger.debug(
                f"→ skipped {non_keyframe_count} non-keyframes in full frame scan."
            )
        if invalid_ts_count > 0:
            self.logger.debug(
                f"→ skipped {invalid_ts_count} invalid timestamps in full frame scan."
            )

        self._idr_pts = sorted(list(pts))
        self.logger.trace(
            f"→ parsed {len(self._idr_pts)} keyframes from full frame scan json"
        )

    def _post_scan_validation(self, source_name: str):
        """performs basic checks and logs warnings based on keyframe scan results."""
        if not self._idr_pts:
            self.logger.warn(
                f"→ {source_name} scan reported success but yielded no keyframes."
            )
            return

        count = len(self._idr_pts)
        self.logger.debug(
            f"→ keyframe scan validation ({source_name}): {count} keyframes found."
        )

        # check if the first keyframe is significantly after time 0.
        first_kf_tolerance = Fraction(50, 1000)  # 50ms tolerance
        if self._idr_pts[0] > first_kf_tolerance:
            self.logger.warn(
                f"→ first keyframe detected at {float(self._idr_pts[0]):.3f}s, "
                f"significantly after start of file. initial segment may be affected."
            )

        # check if the last keyframe is significantly before the end of the file.
        if self.duration and count > 0:
            last_kf_tolerance = Fraction(500, 1000)  # larger tolerance for end (0.5s)
            time_after_last_kf = self.duration - self._idr_pts[-1]
            if time_after_last_kf > last_kf_tolerance:
                self.logger.warn(
                    f"→ last keyframe detected at {float(self._idr_pts[-1]):.3f}s, which is "
                    f"{float(time_after_last_kf):.3f}s before the reported media duration. "
                    f"final segment may be shorter than expected."
                )

        # check for very few keyframes.
        if count < 2:
            self.logger.warn(
                f"→ only {count} keyframe(s) detected by {source_name}. "
                f"cutting might be imprecise or segments may be very long."
            )
            return  # no intervals to check

        # calculate intervals between keyframes.
        intervals = [self._idr_pts[i] - self._idr_pts[i - 1] for i in range(1, count)]

        # check for zero-duration intervals (duplicate timestamps).
        zero_intervals = sum(1 for i in intervals if i <= 0)
        if zero_intervals > 0:
            self.logger.warn(
                f"→ found {zero_intervals} keyframes with duplicate or non-increasing timestamps."
            )
            intervals = [i for i in intervals if i > 0]  # filter out for stats below
            if not intervals:
                return  # no valid intervals left

        # calculate statistics on intervals (if any valid intervals exist).
        if intervals:
            avg_interval = float(sum(intervals) / len(intervals))
            min_interval = float(min(intervals))
            max_interval = float(max(intervals))
            self.logger.debug(
                f"→ keyframe interval stats: avg={avg_interval:.3f}s, "
                f"min={min_interval:.3f}s, max={max_interval:.3f}s"
            )

            # check for excessively large gaps (e.g., > 15 seconds).
            max_gap_threshold = 15.0
            if max_interval > max_gap_threshold:
                self.logger.warn(
                    f"→ detected unusually large keyframe gap: {max_interval:.3f}s."
                )

            # check for high variation in intervals.
            variation_threshold = 10.0
            if (
                min_interval > 1e-6
                and (max_interval / min_interval) > variation_threshold
            ):
                self.logger.warn(
                    f"→ high variation in keyframe intervals detected (max/min ratio > {variation_threshold:.1f}). "
                    f"this might indicate variable frame rate or unusual encoding."
                )

    def verify_closed_gop(self):
        """
        attempts to infer if the video uses closed gops, primarily for h.264/hevc.
        this is an estimation based on keyframe interval consistency.
        """
        self.logger.info("→ verifying gop structure (heuristic check)")

        if not self._idr_pts or len(self._idr_pts) < 3:
            self.logger.debug("→ skipping gop check: not enough keyframes detected.")
            return

        # calculate intervals between keyframes.
        intervals = [
            self._idr_pts[i] - self._idr_pts[i - 1]
            for i in range(1, len(self._idr_pts))
        ]
        intervals = [i for i in intervals if i > 0]  # filter out zero/negative

        if not intervals:
            self.logger.debug(
                "→ skipping gop check: no valid keyframe intervals found."
            )
            return

        # calculate average interval.
        avg_interval = sum(intervals) / len(intervals)

        # check for unusually short intervals relative to the average.
        short_interval_threshold = avg_interval * Fraction(2, 10)  # 0.2
        short_intervals = [i for i in intervals if i < short_interval_threshold]

        if short_intervals:
            self.logger.warn(
                f"→ detected {len(short_intervals)} keyframe interval(s) significantly shorter "
                f"than average (e.g., < {float(short_interval_threshold):.3f}s)."
            )
            self.logger.warn(
                "   this *could* indicate an open gop structure or scene change detection frames."
                "   cuts near these points might exhibit minor artifacts in some players."
            )

        # check for high overall variation
        min_interval = min(intervals)
        max_interval = max(intervals)
        if min_interval > 1e-6:  # avoid division by zero
            interval_variation_ratio = float(max_interval / min_interval)
            variation_threshold = 5.0  # lower threshold for this specific check?
            if interval_variation_ratio > variation_threshold:
                self.logger.warn(
                    f"→ high variation in keyframe intervals detected (ratio: {interval_variation_ratio:.1f})."
                )
                self.logger.warn(
                    "   consistent intervals are more typical of closed gop encoding."
                    "   variable intervals might occur with scene changes or open gop settings."
                )

    # --- segment snapping ---

    def snap_segments(self):
        """
        adjusts start/end times of each requested segment spec to align with keyframes.

        uses the `snap_mode` setting to determine whether to expand (`out`),
        contract (`in`), or conditionally expand (`smart`).
        populates `self.snapped` with `snappedsegment` objects, determining the
        correct `target_path` based on whether merging will occur.
        """
        self.logger.info(
            f"→ snapping segments to keyframe boundaries (mode: {self.snap_mode.value})"
        )

        if not self._idr_pts:
            raise SnapError("cannot snap segments: no keyframes were found.")

        # determine the base file extension for output files.
        try:
            if self.no_merge:
                # derive from pattern (use index 1 as sample)
                ext = Path(str(self.output_path_or_pattern).format(1)).suffix
            else:
                ext = self.output_path_or_pattern.suffix
            ext = ext.lstrip(".") or "tmp"
        except Exception:
            self.logger.warn(
                "could not determine output extension, defaulting to 'tmp'"
            )
            ext = "tmp"

        self.snapped = []  # clear any previous snapped segments
        max_shift_frac = Fraction(
            self.max_shift_ms, 1000
        )  # convert ms threshold to fraction

        for spec in self.segments:
            seg_id = f"segment {spec.index}"  # for logging
            self.logger.debug(
                f"--> snapping {seg_id}: req=[{float(spec.start):.3f}s - {float(spec.end):.3f}s]"
            )

            # find the index of the keyframe immediately *before* or *at* the requested start time.
            kf_index_before_start = bisect_right(self._idr_pts, spec.start) - 1

            # find the index of the keyframe immediately *after* or *at* the requested end time.
            kf_index_after_end = bisect_left(self._idr_pts, spec.end)

            # --- handle edge cases ---
            if kf_index_before_start < 0:
                self.logger.warn(
                    f"{seg_id}: requested start {float(spec.start):.3f}s is before the "
                    f"first keyframe at {float(self._idr_pts[0]):.3f}s. snapping start to first keyframe."
                )
                kf_index_before_start = 0

            if kf_index_after_end >= len(self._idr_pts):
                kf_index_after_end = len(self._idr_pts) - 1
                self.logger.warn(
                    f"{seg_id}: requested end {float(spec.end):.3f}s is after the "
                    f"last keyframe at {float(self._idr_pts[kf_index_after_end]):.3f}s. snapping end to last keyframe."
                )

            # --- determine initial snap points based on 'out' mode ---
            initial_snap_start = self._idr_pts[kf_index_before_start]
            initial_snap_end = self._idr_pts[kf_index_after_end]

            # --- apply snap mode adjustments ---
            final_snap_start = initial_snap_start
            final_snap_end = initial_snap_end

            if self.snap_mode == SnapMode.IN:
                # try to move start time *inward*
                if (
                    initial_snap_start < spec.start
                    and kf_index_before_start + 1 < len(self._idr_pts)
                    and self._idr_pts[kf_index_before_start + 1] < initial_snap_end
                ):
                    final_snap_start = self._idr_pts[kf_index_before_start + 1]
                    self.logger.trace(
                        f"{seg_id}: snap 'in' moved start from {float(initial_snap_start):.3f} to {float(final_snap_start):.3f}"
                    )
                # try to move end time *inward*
                if (
                    initial_snap_end > spec.end
                    and kf_index_after_end - 1 >= 0
                    and self._idr_pts[kf_index_after_end - 1]
                    > final_snap_start  # use final_snap_start
                ):
                    final_snap_end = self._idr_pts[kf_index_after_end - 1]
                    self.logger.trace(
                        f"{seg_id}: snap 'in' moved end from {float(initial_snap_end):.3f} to {float(final_snap_end):.3f}"
                    )

            elif self.snap_mode == SnapMode.SMART:
                shift_start = spec.start - initial_snap_start
                shift_end = initial_snap_end - spec.end

                # if start shift exceeds threshold, try to move start *inward*.
                if shift_start > max_shift_frac:
                    if (
                        kf_index_before_start + 1 < len(self._idr_pts)
                        and self._idr_pts[kf_index_before_start + 1] < initial_snap_end
                    ):
                        final_snap_start = self._idr_pts[kf_index_before_start + 1]
                        self.logger.trace(
                            f"{seg_id}: smart snap moved start inward due to large shift ({float(shift_start):.3f}s > {float(max_shift_frac):.3f}s)"
                        )
                    else:
                        self.logger.trace(
                            f"{seg_id}: smart snap wanted to move start inward, but couldn't (no next kf or collapse)."
                        )

                # if end shift exceeds threshold, try to move end *inward*.
                if shift_end > max_shift_frac:
                    if (
                        kf_index_after_end - 1 >= 0
                        and self._idr_pts[kf_index_after_end - 1]
                        > final_snap_start  # use final_snap_start
                    ):
                        final_snap_end = self._idr_pts[kf_index_after_end - 1]
                        self.logger.trace(
                            f"{seg_id}: smart snap moved end inward due to large shift ({float(shift_end):.3f}s > {float(max_shift_frac):.3f}s)"
                        )
                    else:
                        self.logger.trace(
                            f"{seg_id}: smart snap wanted to move end inward, but couldn't (no prev kf or collapse)."
                        )

            # --- final validation and logging ---
            if final_snap_end <= final_snap_start:
                raise SnapError(
                    f"{seg_id} requested [{float(spec.start):.3f}-{float(spec.end):.3f}] "
                    f"collapsed after snapping between keyframes {float(initial_snap_start):.3f} and "
                    f"{float(initial_snap_end):.3f} (mode: {self.snap_mode.value}). "
                    f"try 'out' snap mode or adjust segment times."
                )

            start_shift = final_snap_start - spec.start
            end_shift = final_snap_end - spec.end
            snapped_duration = final_snap_end - final_snap_start

            self.logger.debug(
                f"  snapped {seg_id}: "
                f"final=[{float(final_snap_start):.3f}s - {float(final_snap_end):.3f}s], "
                f"dur={float(snapped_duration):.3f}s "
                f"(shifts: start={float(start_shift):+.3f}s, end={float(end_shift):+.3f}s)"
            )

            min_warning_frac = Fraction(str(self.min_segment_warning))
            if snapped_duration < min_warning_frac:
                self.logger.warn(
                    f"{seg_id}: resulting snapped duration ({float(snapped_duration):.3f}s) is very short."
                )

            # --- determine target path ---
            target_path: Path
            if self.no_merge:
                # generate final output path from pattern
                try:
                    segment_1_based_index = spec.index + 1
                    target_path = Path(
                        str(self.output_path_or_pattern).format(segment_1_based_index)
                    )
                    target_path = target_path.resolve()  # ensure the path is absolute
                except Exception as e:
                    raise ConfigError(
                        f"failed to format output pattern '{self.output_path_or_pattern}' for {seg_id}: {e}"
                    )
            else:
                # generate temporary filename in the temp directory
                temp_filename = (
                    f"_seg{spec.index:03d}_"
                    f"{self._fmt_fname_ts(final_snap_start)}-{self._fmt_fname_ts(final_snap_end)}."
                    f"{ext}"
                )
                target_path = self.temp_dir / temp_filename

            # --- create snapped segment object ---
            self.snapped.append(
                SnappedSegment(
                    spec=spec,
                    snap_start=final_snap_start,
                    snap_end=final_snap_end,
                    target_path=target_path,  # store the determined path
                )
            )

        # log summary after processing all segments.
        self.logger.info(f"→ finished snapping {len(self.snapped)} segments.")
        if len(self.snapped) != len(self.segments):
            # this should not happen if logic is correct, but good sanity check
            self.logger.error(
                "internal error: number of snapped segments doesn't match requested segments."
            )

    # --- segment extraction ---

    def extract_all_segments(self):
        """
        extracts all snapped segments using ffmpeg.
        target is temporary files if merging, or final files if not merging.
        uses a thread pool for parallel extraction if `self.jobs > 1`.
        """
        if not self.snapped:
            self.logger.warn("→ no segments to extract.")
            return

        mode_desc = (
            "to individual output files" if self.no_merge else "to temporary files"
        )
        self.logger.info(
            f"→ extracting {len(self.snapped)} segments {mode_desc} using {self.jobs} parallel job(s)"
        )

        # clear list of final output paths before extraction begins
        self._final_output_paths = []

        # handle dry run separately.
        if self.dry_run:
            self.logger.warn("[dry run] skipping actual segment extraction.")
            for seg in self.snapped:
                # build the command for logging purposes
                cmd = self._build_extract_cmd(
                    seg.target_path, seg.snap_start, seg.snap_end
                )
                self.logger.info(
                    f"[dry run] would execute for {seg.target_path.name}: {' '.join(map(str, cmd))}"
                )
                # create dummy empty files if merging (needed for concat list)
                if not self.no_merge:
                    try:
                        seg.target_path.parent.mkdir(parents=True, exist_ok=True)
                        seg.target_path.touch()
                    except Exception as e:
                        self.logger.warn(
                            f"[dry run] failed to create dummy temp file {seg.target_path}: {e}"
                        )
                # still add the intended path to the list for the manifest
                self._final_output_paths.append(str(seg.target_path.resolve()))

            # sort paths for consistent manifest output
            self._final_output_paths.sort()
            return

        # use threadpoolexecutor for parallel execution.
        with ThreadPoolExecutor(
            max_workers=self.jobs, thread_name_prefix="polycut_extract"
        ) as executor:
            futures = {
                executor.submit(self._extract_segment, seg): seg for seg in self.snapped
            }

            completed_count = 0
            total_count = len(futures)
            # use as_completed to process results as they become available.
            for future in as_completed(futures):
                seg = futures[future]  # get the segment associated with this future
                seg_id = f"segment {seg.spec.index}"  # for logging
                try:
                    # future.result() returns the path on success or re-raises exception
                    output_path_result = future.result()
                    if output_path_result:  # should always return path on success
                        self._final_output_paths.append(
                            str(output_path_result.resolve())
                        )
                    completed_count += 1
                    self.logger.debug(
                        f"→ extraction progress: {completed_count}/{total_count} segments complete."
                    )
                except ExtractError as e:
                    self.logger.error(
                        f"failed to extract {seg_id} ({seg.target_path.name}): {e}"
                    )
                    raise  # re-raise the exception to stop the overall process
                except Exception as e:
                    self.logger.error(
                        f"unexpected error extracting {seg_id} ({seg.target_path.name}): {e}"
                    )
                    if self.logger.level <= Verbosity.DEBUG.value:
                        import traceback

                        self.logger.debug(traceback.format_exc())
                    raise ExtractError(
                        f"unexpected error during extraction of {seg_id}"
                    ) from e

        # sort final paths for consistent manifest output
        self._final_output_paths.sort()
        self.logger.info(f"→ finished extracting all {len(self.snapped)} segments.")

    def _extract_segment(self, seg: SnappedSegment) -> Path:
        """
        builds and executes the ffmpeg command to extract a single segment to its target path.
        handles seeking, codec copying, applying necessary flags, and optional validation.
        returns the path to the successfully created output file.
        """
        seg_id = f"segment {seg.spec.index}"  # for logging

        # calculate duration of the segment to extract.
        duration = seg.snap_end - seg.snap_start
        if duration <= 0:
            self.logger.warn(
                f"skipping extraction for {seg_id}: zero or negative duration."
            )
            return seg.target_path  # return intended path even if skipped

        # build the ffmpeg command line arguments, passing the target path.
        cmd = self._build_extract_cmd(seg.target_path, seg.snap_start, seg.snap_end)
        cmd_str = " ".join(map(shlex.quote, cmd))  # safely quote arguments for logging

        log_target_desc = "output file" if self.no_merge else "temporary file"
        self.logger.debug(
            f"→ extracting {seg_id} to {log_target_desc} ({seg.target_path.name})"
        )
        self.logger.debug(f"  command: {cmd_str}")

        # --- execute ffmpeg ---
        try:
            # ensure the target directory exists.
            seg.target_path.parent.mkdir(parents=True, exist_ok=True)

            # run ffmpeg.
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            # check ffmpeg's return code.
            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                self.logger.error(
                    f"ffmpeg extraction failed for {seg_id} ({seg.target_path.name})."
                )
                self.logger.error(f"ffmpeg exit code: {proc.returncode}")
                self.logger.error(f"failed command: {cmd_str}")
                self.logger.error(
                    f"ffmpeg stderr:\n---\n{stderr if stderr else 'no stderr output'}\n---"
                )
                raise ExtractError(f"ffmpeg failed during extraction of {seg_id}.")

            # --- post-extraction validation ---
            if not seg.target_path.exists():
                raise ExtractError(
                    f"ffmpeg command succeeded but output file not found: {seg.target_path}"
                )

            try:
                output_size = seg.target_path.stat().st_size
                if output_size == 0:
                    raise ExtractError(
                        f"output file was created but is empty: {seg.target_path}"
                    )
            except FileNotFoundError:
                raise ExtractError(
                    f"output file disappeared after successful ffmpeg command: {seg.target_path}"
                )
            except OSError as e:
                raise ExtractError(
                    f"error accessing output file stats for {seg.target_path}: {e}"
                )

            # log success for this segment.
            self.logger.info(
                f"extracted {seg_id}: {seg.target_path.name} ({humanize_bytes(output_size)})"
            )

            # run optional ffmpeg validation on the output file (temp or final).
            if self.validate:
                self._validate_file(seg.target_path, f"{seg_id} output")

            # return the path of the created file
            return seg.target_path

        except FileNotFoundError:
            # ffmpeg executable itself not found.
            self.logger.error(f"ffmpeg executable not found at '{self.ffmpeg_path}'.")
            raise ConfigError(
                f"ffmpeg not found at '{self.ffmpeg_path}'. cannot extract segments."
            )
        except ExtractError:
            # re-raise specific extraction errors caught above.
            raise
        except Exception as e:
            # catch any other unexpected errors during subprocess execution.
            self.logger.error(
                f"unexpected error during ffmpeg execution for {seg_id}: {e}"
            )
            raise ExtractError(f"unexpected error during extraction of {seg_id}") from e

    # --- segment merging ---

    def merge_segments(self):
        """
        merges all extracted temporary segment files into the final output file.
        uses ffmpeg's 'concat' demuxer for lossless concatenation.
        this is only called if `self.no_merge` is false.
        """
        if self.no_merge:
            self.logger.warn(
                "→ merge_segments called unexpectedly when no_merge is true. skipping."
            )
            return

        if not self.snapped:
            self.logger.warn("→ no extracted segments to merge.")
            return

        # filter snapped segments to ensure target paths exist (important for dry run where touch might fail)
        segments_to_merge = [
            seg
            for seg in self.snapped
            if seg.target_path.exists() and seg.target_path.is_file()
        ]
        if len(segments_to_merge) != len(self.snapped):
            self.logger.warn(
                f"found {len(segments_to_merge)} existing temporary files out of {len(self.snapped)} expected. merging only existing files."
            )
            if not segments_to_merge:
                raise MergeError("no valid temporary segment files found to merge.")

        final_output_path = (
            self.output_path_or_pattern
        )  # in merge mode, this is the single output file
        self.logger.info(
            f"→ merging {len(segments_to_merge)} segments into {final_output_path.name}"
        )

        # --- create concat list file ---
        list_path = self.temp_dir / "concat_list.txt"
        try:
            with list_path.open("w", encoding="utf-8") as f:
                for seg in segments_to_merge:
                    # use relative path (filename) as ffmpeg will run from temp_dir
                    safe_name = self._escape_path_for_concat(seg.target_path.name)
                    f.write(f"file '{safe_name}'\n")
            self.logger.debug(f"→ created concat list file: {list_path}")
        except Exception as e:
            raise MergeError(f"failed to write concat list file {list_path}: {e}")

        # handle dry run (already handled in run(), but double check here)
        if self.dry_run:
            self.logger.warn("[dry run] skipping actual segment merging.")
            cmd = self._build_merge_cmd(list_path, final_output_path)
            self.logger.info(
                f"[dry run] would execute: {' '.join(map(shlex.quote, cmd))}"
            )
            return

        # --- build merge command ---
        cmd = self._build_merge_cmd(list_path, final_output_path)
        cmd_str = " ".join(map(shlex.quote, cmd))
        self.logger.debug(f"→ merge command: {cmd_str}")

        # --- execute ffmpeg merge ---
        try:
            # run the merge command from the temporary directory
            proc = subprocess.run(
                cmd,
                cwd=str(self.temp_dir),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            # check ffmpeg return code.
            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                self.logger.error("ffmpeg merge command failed.")
                self.logger.error(f"ffmpeg exit code: {proc.returncode}")
                self.logger.error(f"failed command: {cmd_str}")
                self.logger.error(
                    f"ffmpeg stderr:\n---\n{stderr if stderr else 'no stderr output'}\n---"
                )
                raise MergeError("ffmpeg failed during segment merging.")

            # --- post-merge validation ---
            if not final_output_path.exists():
                raise MergeError(
                    f"merge command succeeded but output file not found: {final_output_path}"
                )

            try:
                output_size = final_output_path.stat().st_size
                if output_size == 0:
                    raise MergeError(
                        f"merged output file was created but is empty: {final_output_path}"
                    )
            except FileNotFoundError:
                raise MergeError(
                    f"merged output file disappeared after successful ffmpeg command: {final_output_path}"
                )
            except OSError as e:
                raise MergeError(
                    f"error accessing merged output file stats for {final_output_path}: {e}"
                )

            self.logger.info(
                f"successfully merged segments into: {final_output_path.name} ({humanize_bytes(output_size)})"
            )

        except FileNotFoundError:
            self.logger.error(f"ffmpeg executable not found at '{self.ffmpeg_path}'.")
            raise ConfigError(
                f"ffmpeg not found at '{self.ffmpeg_path}'. cannot merge segments."
            )
        except MergeError:
            raise  # re-raise specific merge errors
        except Exception as e:
            self.logger.error(f"unexpected error during ffmpeg merge execution: {e}")
            raise MergeError("unexpected error during segment merging.") from e

    # --- manifest and validation ---

    def get_segment_info(self) -> Dict[str, Any]:
        """
        compiles detailed information about the requested and actual (snapped) segments.

        used for both the json manifest file and the summary table displayed in the cli.
        includes timestamps (float and exact fraction strings), durations, shifts,
        and final output file path(s).

        returns:
            a dictionary containing segment details and totals.
        """
        if not self.snapped:
            # handle case where snapping might have failed or produced no segments
            return {
                "input_file": str(self.input_path),
                "output_path_or_pattern": str(self.output_path_or_pattern),
                "no_merge_mode": self.no_merge,
                "output_files": [],
                "codec": self.codec,
                "container_formats": self.container_formats,
                "segments": [],
                "totals": {
                    "requested_duration": 0.0,
                    "actual_duration": 0.0,
                    "formatted": {"requested": "0:00.000", "actual": "0:00.000"},
                },
                "warning": "no segments were successfully snapped or processed.",
            }

        # build list of segment details
        segment_details = []
        total_req_duration = Fraction(0)
        total_act_duration = Fraction(0)

        for seg in self.snapped:
            req_duration = seg.spec.end - seg.spec.start
            act_duration = seg.snap_end - seg.snap_start
            start_shift = seg.snap_start - seg.spec.start
            end_shift = seg.snap_end - seg.spec.end
            duration_shift = act_duration - req_duration

            total_req_duration += req_duration
            total_act_duration += act_duration

            details = {
                "index": seg.spec.index,
                "requested": {
                    "start": float(seg.spec.start),
                    "end": float(seg.spec.end),
                    "start_exact": str(
                        seg.spec.start
                    ),  # store exact fraction as string
                    "end_exact": str(seg.spec.end),
                    "duration": float(req_duration),
                    "duration_exact": str(req_duration),
                    "formatted": {
                        "start": format_time(float(seg.spec.start)),
                        "end": format_time(float(seg.spec.end)),
                        "duration": format_time(float(req_duration)),
                    },
                },
                "actual": {
                    "start": float(seg.snap_start),
                    "end": float(seg.snap_end),
                    "start_exact": str(seg.snap_start),
                    "end_exact": str(seg.snap_end),
                    "duration": float(act_duration),
                    "duration_exact": str(act_duration),
                    "formatted": {
                        "start": format_time(float(seg.snap_start)),
                        "end": format_time(float(seg.snap_end)),
                        "duration": format_time(float(act_duration)),
                    },
                },
                "shifts": {  # shifts: actual - requested
                    "start": float(start_shift),
                    "end": float(end_shift),
                    "duration": float(duration_shift),
                    "start_exact": str(start_shift),
                    "end_exact": str(end_shift),
                    "duration_exact": str(duration_shift),
                },
                # store the final target path (absolute)
                "output_file": str(seg.target_path.resolve()),
            }
            segment_details.append(details)

        # compile final dictionary
        manifest_data = {
            "input_file": str(self.input_path.resolve()),
            "output_path_or_pattern": str(self.output_path_or_pattern),
            "no_merge_mode": self.no_merge,
            # include the list of actual output files created (or intended in dry run)
            "output_files": self._final_output_paths,
            "detected_codec": self.codec,
            "detected_container_formats": self.container_formats,
            "snap_mode": self.snap_mode.value,
            "segments": segment_details,
            "totals": {
                "requested_duration": float(total_req_duration),
                "actual_duration": float(total_act_duration),
                "requested_duration_exact": str(total_req_duration),
                "actual_duration_exact": str(total_act_duration),
                "formatted": {
                    "requested": format_time(float(total_req_duration)),
                    "actual": format_time(float(total_act_duration)),
                },
            },
        }
        return manifest_data

    def _write_segment_manifest(self, segment_info: Dict[str, Any]):
        """writes the segment information dictionary to a json file."""
        if self.dry_run:
            self.logger.warn("[dry run] skipping writing segment manifest file.")
            return

        # determine manifest filename based on output path/pattern directory
        output_stem = self.output_path_or_pattern.stem
        manifest_filename = f"{output_stem}.segments.json"
        # handle potential edge case where stem itself ends in .segments
        if manifest_filename.endswith(".segments.segments.json"):
            manifest_filename = f"{output_stem}.json"

        manifest_path = self._output_dir / manifest_filename

        self.logger.info(f"→ writing segment manifest to: {manifest_path}")
        try:
            with manifest_path.open("w", encoding="utf-8") as f:
                # use indent for human-readable json output.
                json.dump(segment_info, f, indent=2, ensure_ascii=False)
            self.logger.debug("→ successfully wrote manifest file.")
        except Exception as e:
            # log warning but don't treat as fatal error.
            self.logger.warn(
                f"failed to write segment manifest file {manifest_path}: {e}"
            )

    def _validate_file(self, file_path: Path, file_description: str):
        """
        runs ffmpeg in a null-output mode to check for basic integrity errors.
        """
        self.logger.info(f"→ validating {file_description} ({file_path.name})")

        if not file_path.exists() or not file_path.is_file():
            self.logger.warn(
                f"cannot validate {file_description}: file not found or not a file at {file_path}"
            )
            return

        # ffmpeg command: -v error -i file -f null -
        cmd = [
            self.ffmpeg_path,
            "-v",
            "error",
            "-nostdin",
            "-i",
            str(file_path),
            "-f",
            "null",
            "-",
        ]
        cmd_str = " ".join(map(shlex.quote, cmd))
        self.logger.debug(f"  validation command: {cmd_str}")

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            if proc.returncode != 0:
                stderr = proc.stderr.strip()
                self.logger.error(
                    f"validation failed for {file_description} ({file_path.name})."
                )
                self.logger.error(f"ffmpeg exit code: {proc.returncode}")
                self.logger.error(f"failed command: {cmd_str}")
                self.logger.error(
                    f"ffmpeg stderr:\n---\n{stderr if stderr else 'no stderr output'}\n---"
                )
                raise ValidateError(
                    f"validation check failed for {file_description} ({file_path.name})."
                )
            else:
                # check stderr even on success for warnings.
                stderr = proc.stderr.strip()
                if stderr:
                    self.logger.warn(
                        f"validation check passed for {file_description}, but ffmpeg reported warnings:"
                    )
                    self.logger.warn(f"---\n{stderr}\n---")
                else:
                    self.logger.debug(
                        f"→ validation successful for {file_description} ({file_path.name})"
                    )

        except FileNotFoundError:
            self.logger.error(f"ffmpeg executable not found at '{self.ffmpeg_path}'.")
            raise ConfigError(
                f"ffmpeg not found at '{self.ffmpeg_path}'. cannot validate files."
            )
        except ValidateError:
            raise  # re-raise validation errors
        except Exception as e:
            self.logger.error(
                f"unexpected error during validation of {file_path.name}: {e}"
            )
            raise ValidateError(
                f"unexpected error validating {file_description}"
            ) from e

    # --- cleanup ---

    def cleanup(self):
        """removes the temporary directory unless `keep_temp` is true."""
        # determine if we should remove the main temp dir we created/used
        should_remove = (self._temp_dir_created and not self.keep_temp) or (
            not self._temp_dir_created
            and not self.keep_temp
            and self.temp_dir != self.temp_dir_base
        )

        if self.keep_temp:
            self.logger.info(f"→ keeping temporary directory: {self.temp_dir}")
            # if user provided base dir and we created subdir, clarify location
            if not self._temp_dir_created and self.temp_dir != self.temp_dir_base:
                self.logger.info(
                    f"   (note: intermediate files are inside {self.temp_dir})"
                )

        elif self.temp_dir and self.temp_dir.exists() and should_remove:
            try:
                # recursively remove the temporary directory and its contents.
                shutil.rmtree(self.temp_dir)
                self.logger.info(
                    f"→ successfully cleaned up temporary directory: {self.temp_dir}"
                )
            except Exception as e:
                # log warning if cleanup fails, but don't raise error.
                self.logger.warn(
                    f"could not automatically remove temporary directory {self.temp_dir}: {e}"
                )
                self.logger.warn("you may need to remove it manually.")
        else:
            self.logger.debug(
                "→ no temporary directory to clean up or cleanup skipped."
            )

    # --- ffmpeg command building ---

    def _fmt_ffmpeg_ts(self, ts: Fraction) -> str:
        """
        formats a fraction-of-seconds timestamp into a decimal string suitable for ffmpeg.
        uses decimal arithmetic and specified precision.
        """
        if ts < 0:
            ts = Fraction(0)  # ensure non-negative

        decimal_ts = Decimal(ts.numerator) / Decimal(ts.denominator)
        quantizer = Decimal("1e-" + str(self.timestamp_precision))
        quantized_ts = decimal_ts.quantize(quantizer, rounding=ROUND_HALF_UP)
        # format using 'f' but normalize to remove trailing zeros/point if integer
        return format(quantized_ts.normalize(), "f")

    def _build_extract_cmd(
        self, target_path: Path, snap_start: Fraction, snap_end: Fraction
    ) -> List[str]:
        """constructs the ffmpeg command line arguments for extracting a single segment."""
        duration = snap_end - snap_start
        start_str = self._fmt_ffmpeg_ts(snap_start)
        duration_str = self._fmt_ffmpeg_ts(duration)

        cmd: List[str] = [
            self.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
        ]

        # --- seeking strategy ---
        if self.accurate_seek:
            cmd.extend(["-i", str(self.input_path)])
            cmd.extend(["-ss", start_str, "-copyts", "-avoid_negative_ts", "make_zero"])
        else:
            cmd.extend(["-ss", start_str, "-i", str(self.input_path)])
            if self._is_mp4_family():
                cmd.extend(["-avoid_negative_ts", "make_zero"])

        # --- duration and stream mapping ---
        cmd.extend(["-t", duration_str])
        cmd.extend(["-map", "0:v?", "-map", "0:a?"])  # map video/audio if present

        # --- codec and format flags ---
        cmd.extend(["-c", "copy"])  # lossless copy

        if self.codec == "hevc" and self._is_mp4_family():
            cmd.extend(["-tag:v", "hvc1"])

        format_flags = self._determine_format_flags()
        if format_flags:
            cmd.extend(format_flags.split())

        # --- bitstream filters (bsf) ---
        if self.codec in ("h264", "hevc") and self._is_mp4_family():
            bsf_name = (
                "h264_mp4toannexb" if self.codec == "h264" else "hevc_mp4toannexb"
            )
            cmd.extend(["-bsf:v", bsf_name])

        # --- output ---
        cmd.append(str(target_path))  # use the provided target path

        return cmd

    def _build_merge_cmd(
        self, concat_list_path: Path, final_output_path: Path
    ) -> List[str]:
        """constructs the ffmpeg command line arguments for merging segments."""
        cmd: List[str] = [
            self.ffmpeg_path,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list_path.name),  # relative path from temp_dir
            "-map",
            "0:v?",
            "-map",
            "0:a?",
            "-c",
            "copy",
        ]

        # --- timestamp handling for merge ---
        ts_flags = self._determine_merge_timestamp_flags()
        if ts_flags:
            cmd.extend(ts_flags.split())

        # --- codec tags and format flags ---
        if self.codec == "hevc" and self._is_mp4_family():
            cmd.extend(["-tag:v", "hvc1"])

        format_flags = self._determine_format_flags()
        if format_flags:
            cmd.extend(format_flags.split())

        # --- final output path ---
        cmd.append(str(final_output_path.resolve()))  # absolute path for final output

        return cmd

    # --- utility methods ---

    def _determine_format_flags(self) -> str:
        """selects appropriate '-movflags' or other format-specific flags based on detected container."""
        if self.codec == "av1" and self._is_mp4_family():
            return self._AV1_MP4_FLAGS
        if self.container_formats:
            for fmt in self.container_formats:
                if fmt in self._FORMAT_FLAGS:
                    return self._FORMAT_FLAGS[fmt]
        return ""

    def _determine_merge_timestamp_flags(self) -> str:
        """selects appropriate timestamp-related flags for the merge command."""
        if self.container_formats:
            for fmt in self.container_formats:
                if fmt in self._TS_MERGE_FLAGS:
                    return self._TS_MERGE_FLAGS[fmt]
        return ""

    def _fmt_fname_ts(self, t: Fraction) -> str:
        """
        converts a fraction-of-seconds timestamp into a filename-safe string (hhmmssmsus).
        """
        if t < 0:
            t = Fraction(0)
        total_us = int(t.numerator * 1_000_000 / t.denominator)
        us = total_us % 1000
        total_ms = total_us // 1000
        ms = total_ms % 1000
        total_s = total_ms // 1000
        s = total_s % 60
        total_m = total_s // 60
        m = total_m % 60
        h = total_m // 60
        return f"{h:02d}{m:02d}{s:02d}{ms:03d}{us:03d}"

    def _escape_path_for_concat(self, path_str: str) -> str:
        """
        escapes characters in a path string that are special to ffmpeg's concat demuxer.
        """
        # rule 1: backslash needs to be escaped as \\
        # rule 2: single quote needs to be escaped as '\''
        escaped = path_str.replace("\\", "\\\\").replace("'", "'\\''")
        return escaped
