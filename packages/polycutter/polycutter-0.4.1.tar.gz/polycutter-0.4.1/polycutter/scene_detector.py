"""
Scene detector module for polycutter.
Provides functionality to detect natural cut points in videos using scene changes or keyframes.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass
from fractions import Fraction
from bisect import bisect_right, bisect_left


# Custom exceptions for clearer error handling
class DetectionError(Exception):
    pass


class ProbeError(Exception):
    pass


class AnalysisError(Exception):
    pass


class DetectionMethod(str, Enum):
    """Methods for suggesting cut points in video."""
    SCENE = "scene"  # detect scene changes based on visual difference
    KEYFRAME = "keyframe"  # find keyframes at regular intervals
    EQUAL = "equal"  # divide video into equal parts


@dataclass
class ScenePoint:
    """Detected scene change or keyframe information."""
    timestamp: float  # time in seconds
    score: float  # scene change score or importance metric (0-1)
    method: str  # detection method used
    frame_type: str = ""  # frame type (I, P, B) if available


@dataclass
class Segment:
    """Represent a segment with start/end times."""
    index: int  # ordinal position
    start: float  # start time in seconds
    end: float  # end time in seconds
    type: str  # detection method or type
    metadata: Dict[str, Any] = None  # additional segment info


class SceneDetector:
    """
    Detect scene changes and suggest natural cut points in video files.

    This class uses ffmpeg/ffprobe to analyze videos for:
    - Visual scene changes
    - Keyframe positions
    - Other structural information

    It can suggest optimal cut points based on different strategies.
    """

    def __init__(
        self,
        input_path: Path,
        logger: Any,
        ffmpeg_path: str = "ffmpeg",
        ffprobe_path: str = "ffprobe",
    ):
        """
        Initialize the scene detector.

        Args:
            input_path: Path to the input video file
            logger: Logger object for output messages
            ffmpeg_path: Path to ffmpeg executable
            ffprobe_path: Path to ffprobe executable
        """
        self.input_path = Path(input_path)
        self.logger = logger
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

        # Will be populated during analysis
        self.duration: Optional[float] = None
        self.codec: Optional[str] = None
        self.container_formats: Optional[List[str]] = None

        # Detection results
        self.scene_changes: List[ScenePoint] = []
        self.keyframes: List[ScenePoint] = []

        # Cache for probe results
        self._probe_cache: Dict[str, Any] = {}

    def analyze_media(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Analyze media file to determine basic properties.

        Args:
            progress_callback: Optional function to report progress

        Returns:
            Dict with media properties
        """
        self.logger.info(f"analyzing media: {self.input_path.name}")

        # Probe duration and basic format info
        self._probe_duration()
        self._detect_codec()
        self._detect_container_format()

        # Prepare result
        result = {
            "duration": self.duration,
            "codec": self.codec,
            "container_formats": self.container_formats,
        }

        # Add frame rate if available
        try:
            fps = self._probe_frame_rate()
            result["frame_rate"] = fps
            self.logger.info(f"frame rate: {fps:.3f} fps")
        except Exception as e:
            self.logger.warn(f"could not detect frame rate: {e}")

        # Log detected properties
        self.logger.info(f"duration: {self._format_time(self.duration)} ({self.duration:.3f}s)")
        if self.codec:
            self.logger.info(f"codec: {self.codec}")
        if self.container_formats:
            self.logger.info(f"container formats: {', '.join(self.container_formats)}")

        return result

    def detect_scenes(
        self,
        threshold: float = 0.3,
        min_scene_length: float = 1.0,
        progress_callback: Optional[Callable] = None
    ) -> List[ScenePoint]:
        """
        Detect scene changes in the video.

        Args:
            threshold: Scene change detection threshold (0.0-1.0)
            min_scene_length: Minimum length between scenes in seconds
            progress_callback: Optional function to report progress

        Returns:
            List of detected scene changes
        """
        self.logger.info(f"detecting scene changes with threshold {threshold}")

        if progress_callback:
            progress_callback("Detecting scenes", 0)

        # Use ffmpeg with select filter to detect scene changes
        cmd = [
            self.ffmpeg_path,
            "-i", str(self.input_path),
            "-filter:v", f"select='gt(scene,{threshold})',showinfo",
            "-f", "null",
            "-"
        ]

        # Run the detection
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                errors="replace"
            )

            if progress_callback:
                progress_callback("Detecting scenes", 100)

            if proc.returncode != 0:
                self.logger.warn(f"scene detection failed: {proc.stderr}")
                return []

            # Parse output to find scene changes
            scenes = []
            last_scene_time = 0

            for line in proc.stderr.splitlines():
                if "pts_time:" in line and "scene:" in line:
                    try:
                        # Extract timestamp and score
                        pts_time = float(line.split("pts_time:")[1].split()[0])
                        scene_score = float(line.split("scene:")[1].split()[0])

                        # Only include if after beginning and before end,
                        # And respecting minimum scene length
                        if (0.5 < pts_time < self.duration - 0.5 and
                            pts_time - last_scene_time >= min_scene_length):
                            scene = ScenePoint(
                                timestamp=pts_time,
                                score=scene_score,
                                method="scene"
                            )
                            scenes.append(scene)
                            last_scene_time = pts_time
                    except (ValueError, IndexError):
                        pass

            self.scene_changes = scenes
            self.logger.info(f"detected {len(scenes)} scene changes")
            return scenes

        except Exception as e:
            if progress_callback:
                progress_callback("Scene detection failed", 100)
            self.logger.error(f"scene detection error: {str(e)}")
            raise DetectionError(f"scene detection failed: {str(e)}")

    def detect_keyframes(
        self,
        min_interval: float = 1.0,
        progress_callback: Optional[Callable] = None
    ) -> List[ScenePoint]:
        """
        Detect keyframes in the video using multiple fallback methods.

        Args:
            min_interval: Minimum interval between keyframes to include
            progress_callback: Optional function to report progress

        Returns:
            List of detected keyframes
        """
        self.logger.info("detecting keyframes")

        if progress_callback:
            progress_callback("Detecting keyframes", 0)

        # Try multiple keyframe detection methods
        keyframes = []

        # Method 1: standard ffprobe for keyframes
        try:
            keyframes = self._detect_keyframes_ffprobe()
            if keyframes:
                self.logger.info(f"found {len(keyframes)} keyframes with standard method")
        except Exception as e:
            self.logger.warn(f"standard keyframe detection failed: {e}")

        # Method 2: alternative ffmpeg filter if method 1 failed
        if not keyframes:
            if progress_callback:
                progress_callback("Trying alternative keyframe detection", 33)

            try:
                keyframes = self._detect_keyframes_ffmpeg_pict()
                if keyframes:
                    self.logger.info(f"found {len(keyframes)} keyframes with pict_type method")
            except Exception as e:
                self.logger.warn(f"alternative keyframe detection failed: {e}")

        # Method 3: another ffmpeg filter format as last resort
        if not keyframes:
            if progress_callback:
                progress_callback("Trying final keyframe detection method", 66)

            try:
                keyframes = self._detect_keyframes_ffmpeg_generic()
                if keyframes:
                    self.logger.info(f"found {len(keyframes)} keyframes with generic method")
            except Exception as e:
                self.logger.warn(f"final keyframe detection failed: {e}")

        if progress_callback:
            progress_callback("Keyframe detection complete", 100)

        if not keyframes:
            self.logger.warn("no keyframes detected with any method")
            return []

        # Filter by minimum interval to avoid too many keyframes
        filtered_keyframes = []
        last_kf_time = 0

        for kf in sorted(keyframes, key=lambda k: k.timestamp):
            if (kf.timestamp - last_kf_time >= min_interval and
                0.5 < kf.timestamp < self.duration - 0.5):
                filtered_keyframes.append(kf)
                last_kf_time = kf.timestamp

        self.keyframes = filtered_keyframes
        self.logger.info(f"using {len(filtered_keyframes)} keyframes after filtering")
        return filtered_keyframes

    def suggest_segments(
        self,
        method: DetectionMethod = DetectionMethod.SCENE,
        target_count: Optional[int] = None,
        interval_minutes: float = 5.0,
        threshold: float = 0.3,
        min_segment_length: float = 1.0,
        progress_callback: Optional[Callable] = None,
    ) -> List[Segment]:
        """
        Suggest segments based on specified method.

        Args:
            method: Detection method to use
            target_count: Desired number of segments (if None, uses interval)
            interval_minutes: Target interval between segments in minutes (if target_count is None)
            threshold: Scene change detection threshold (0.0-1.0)
            min_segment_length: Minimum segment length in seconds
            progress_callback: Optional function to report progress

        Returns:
            List of suggested segments
        """
        # Analyze media if not already done
        if self.duration is None:
            self.analyze_media(progress_callback)

        # Determine number of segments
        interval_seconds = interval_minutes * 60

        if target_count is not None:
            num_segments = target_count
            self.logger.info(f"targeting {num_segments} segments")
        else:
            num_segments = max(2, int(self.duration / interval_seconds))
            self.logger.info(f"targeting segments of ~{interval_minutes} minutes ({num_segments} segments)")

        # Detect scene changes/keyframes based on method
        segments = []
        cut_points = []

        # Method-specific detection
        if method == DetectionMethod.SCENE:
            # Try scene detection first
            if progress_callback:
                progress_callback("Detecting scenes", 0)

            scenes = self.detect_scenes(threshold, min_segment_length, progress_callback)

            if not scenes:
                self.logger.warn("falling back to keyframe detection")
                method = DetectionMethod.KEYFRAME
            else:
                # If we have too many scenes, select most significant ones
                if len(scenes) > num_segments * 2:
                    # Sort by score (highest first)
                    scenes.sort(key=lambda s: s.score, reverse=True)
                    scenes = scenes[:num_segments * 2]
                    # Resort by timestamp for processing
                    scenes.sort(key=lambda s: s.timestamp)
                    self.logger.info(f"filtered to {len(scenes)} most significant scene changes")

                # If we still have too many, select best distributed
                if len(scenes) > num_segments - 1:
                    # Select scenes closest to ideal intervals
                    ideal_interval = self.duration / num_segments
                    selected_scenes = []

                    for i in range(1, num_segments):
                        ideal_time = ideal_interval * i
                        # Find closest scene
                        closest = min(scenes, key=lambda s: abs(s.timestamp - ideal_time))
                        selected_scenes.append(closest)

                    scenes = selected_scenes
                    self.logger.info(f"selected {len(scenes)} optimally distributed scenes")

                # Use selected scenes as cut points
                cut_points = [(s.timestamp, f"scene change (score: {s.score:.2f})") for s in scenes]

        if method == DetectionMethod.KEYFRAME or not cut_points:
            # Use keyframe detection
            if progress_callback:
                progress_callback("Detecting keyframes", 0)

            keyframes = self.detect_keyframes(min_segment_length, progress_callback)

            if not keyframes:
                self.logger.warn("keyframe detection failed, falling back to equal intervals")
                method = DetectionMethod.EQUAL
            else:
                # Calculate ideal cut points
                ideal_cuts = []
                for i in range(1, num_segments):
                    ideal_time = (self.duration / num_segments) * i
                    ideal_cuts.append(ideal_time)

                # Find nearest keyframes to ideal cut points
                for ideal_time in ideal_cuts:
                    if keyframes:
                        closest_kf = min(keyframes, key=lambda k: abs(k.timestamp - ideal_time))
                        shift = abs(closest_kf.timestamp - ideal_time)
                        cut_points.append((closest_kf.timestamp, f"keyframe (shift: {shift:.2f}s)"))

                # If we didn't get enough cut points, fall back to equal
                if len(cut_points) < num_segments - 1:
                    self.logger.warn("not enough usable keyframes, falling back to equal intervals")
                    cut_points = []
                    method = DetectionMethod.EQUAL

        if method == DetectionMethod.EQUAL or not cut_points:
            # Use equal time intervals
            self.logger.info("using equal time intervals")

            cut_points = []
            for i in range(1, num_segments):
                cut_time = (self.duration / num_segments) * i
                cut_points.append((cut_time, "equal interval"))

        # Sort cut points
        cut_points.sort()

        # Generate segments from cut points
        segment_points = [0] + [p[0] for p in cut_points] + [self.duration]
        segment_types = ["start"] + [p[1] for p in cut_points] + ["end"]

        for i in range(len(segment_points) - 1):
            start = segment_points[i]
            end = segment_points[i + 1]

            # Skip very short segments
            if end - start < min_segment_length:
                continue

            segment = Segment(
                index=i + 1,
                start=start,
                end=end,
                type=segment_types[i],
                metadata={
                    "duration": end - start,
                    "method": method.value,
                    "format": {
                        "start": self._format_time(start),
                        "end": self._format_time(end),
                        "duration": self._format_time(end - start),
                        "cmd_segment": f"{start:.3f}-{end:.3f}"
                    }
                }
            )
            segments.append(segment)

        if progress_callback:
            progress_callback("Segment analysis complete", 100)

        self.logger.info(f"created {len(segments)} segments using {method.value} method")
        return segments

    def _probe_duration(self) -> float:
        """Get the duration of the media file."""
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            str(self.input_path),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if proc.returncode != 0:
            raise ProbeError(f"ffprobe error: {proc.stderr.strip()}")

        info = json.loads(proc.stdout)
        duration = float(info.get("format", {}).get("duration", 0))

        if duration <= 0:
            raise ProbeError("could not determine video duration")

        self.duration = duration
        return duration

    def _probe_frame_rate(self) -> float:
        """Get the frame rate of the video."""
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-select_streams", "v",
            "-show_entries", "stream=r_frame_rate",
            "-of", "json",
            str(self.input_path),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if proc.returncode != 0:
            raise ProbeError(f"ffprobe error: {proc.stderr.strip()}")

        info = json.loads(proc.stdout)

        if not info.get("streams"):
            raise ProbeError("no video streams found")

        fps_str = info["streams"][0].get("r_frame_rate", "0/1")

        try:
            num, denom = map(int, fps_str.split("/"))
            fps = num / denom if denom else 0
            return fps
        except (ValueError, ZeroDivisionError):
            raise ProbeError(f"invalid frame rate: {fps_str}")

    def _detect_codec(self) -> Optional[str]:
        """Detect the video codec."""
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-select_streams", "v",
            "-show_entries", "stream=codec_name",
            "-of", "json",
            str(self.input_path),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if proc.returncode == 0:
            info = json.loads(proc.stdout)
            if "streams" in info and info["streams"]:
                self.codec = info["streams"][0].get("codec_name")
                return self.codec

        return None

    def _detect_container_format(self) -> Optional[List[str]]:
        """Detect the container format(s)."""
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-show_entries", "format=format_name",
            "-of", "json",
            str(self.input_path),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if proc.returncode == 0:
            info = json.loads(proc.stdout)
            format_name = info.get("format", {}).get("format_name", "")
            if format_name:
                self.container_formats = format_name.split(",")
                return self.container_formats

        return None

    def _detect_keyframes_ffprobe(self) -> List[ScenePoint]:
        """Detect keyframes using ffprobe."""
        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-select_streams", "v",
            "-skip_frame", "nokey",
            "-show_entries", "frame=pkt_pts_time,pict_type",
            "-of", "json",
            str(self.input_path),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if proc.returncode != 0:
            raise DetectionError(f"ffprobe error: {proc.stderr.strip()}")

        info = json.loads(proc.stdout)
        keyframes = []

        for frame in info.get("frames", []):
            if "pkt_pts_time" in frame:
                keyframes.append(
                    ScenePoint(
                        timestamp=float(frame["pkt_pts_time"]),
                        score=1.0,  # keyframes have maximum score
                        method="keyframe",
                        frame_type=frame.get("pict_type", "I")
                    )
                )

        return keyframes

    def _detect_keyframes_ffmpeg_pict(self) -> List[ScenePoint]:
        """Detect keyframes using ffmpeg with pict_type filter."""
        cmd = [
            self.ffmpeg_path,
            "-i", str(self.input_path),
            "-filter:v", "select='eq(pict_type,I)',showinfo",
            "-f", "null",
            "-"
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if proc.returncode != 0:
            raise DetectionError(f"ffmpeg error: {proc.stderr.strip()}")

        keyframes = []

        for line in proc.stderr.splitlines():
            if "pts_time:" in line:
                try:
                    pts_time = float(line.split("pts_time:")[1].split()[0])
                    keyframes.append(
                        ScenePoint(
                            timestamp=pts_time,
                            score=1.0,
                            method="keyframe_pict",
                            frame_type="I"
                        )
                    )
                except (ValueError, IndexError):
                    pass

        return keyframes

    def _detect_keyframes_ffmpeg_generic(self) -> List[ScenePoint]:
        """Detect keyframes using generic ffmpeg filter."""
        cmd = [
            self.ffmpeg_path,
            "-i", str(self.input_path),
            "-vf", "select='eq(pict_type,PICT_TYPE_I)',showinfo",
            "-f", "null",
            "-"
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        if proc.returncode != 0:
            raise DetectionError(f"ffmpeg error: {proc.stderr.strip()}")

        keyframes = []

        for line in proc.stderr.splitlines():
            if "pts_time:" in line:
                try:
                    pts_time = float(line.split("pts_time:")[1].split()[0])
                    keyframes.append(
                        ScenePoint(
                            timestamp=pts_time,
                            score=1.0,
                            method="keyframe_generic",
                            frame_type="I"
                        )
                    )
                except (ValueError, IndexError):
                    pass

        return keyframes

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds as HH:MM:SS.mmm or MM:SS.mmm."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:06.3f}"
        else:
            return f"{minutes}:{secs:06.3f}"
