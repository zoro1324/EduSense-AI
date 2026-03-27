import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone
from ultralytics import YOLO

from api.models import EngagementLog

logger = logging.getLogger(__name__)


# COCO keypoint indices for YOLOv8 pose model.
NOSE = 0
LEFT_EYE = 1
RIGHT_EYE = 2
LEFT_EAR = 3
RIGHT_EAR = 4
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_HIP = 11
RIGHT_HIP = 12

MIN_KPT_CONF = 0.35
STILL_MOTION_NORM = 0.008
ACTIVE_MOTION_NORM_MAX = 0.045
CHAOTIC_MOTION_NORM = 0.09
STILL_FRAME_LIMIT = 30


@dataclass
class MotionSlot:
    center: Tuple[float, float]
    still_count: int


class AnonymousMotionEstimator:
    """Anonymous short-lived motion slots, no identity persistence."""

    def __init__(self, max_match_px: float = 100.0) -> None:
        self.max_match_px = max_match_px
        self._prev_slots: List[MotionSlot] = []

    def update(self, centers: List[Tuple[float, float]]) -> List[Tuple[float, int]]:
        if not centers:
            self._prev_slots = []
            return []

        if not self._prev_slots:
            self._prev_slots = [MotionSlot(center=c, still_count=0) for c in centers]
            return [(0.0, 0) for _ in centers]

        used_prev = set()
        output: List[Tuple[float, int]] = []
        new_slots: List[MotionSlot] = []

        for center in centers:
            best_idx = None
            best_dist = float("inf")

            for idx, slot in enumerate(self._prev_slots):
                if idx in used_prev:
                    continue
                dist = float(np.linalg.norm(np.array(center) - np.array(slot.center)))
                if dist < best_dist and dist <= self.max_match_px:
                    best_dist = dist
                    best_idx = idx

            if best_idx is None:
                displacement = 0.0
                still_count = 0
            else:
                used_prev.add(best_idx)
                prev_still = self._prev_slots[best_idx].still_count
                displacement = best_dist
                still_count = prev_still + 1 if displacement < 2.0 else 0

            output.append((displacement, still_count))
            new_slots.append(MotionSlot(center=center, still_count=still_count))

        self._prev_slots = new_slots
        return output


class EngagementAnalyzer:
    def __init__(self, model_path: str, conf_thres: float = 0.3, imgsz: int = 640) -> None:
        self.model = YOLO(model_path)
        self.conf_thres = conf_thres
        self.imgsz = imgsz
        self.motion = AnonymousMotionEstimator()

    @staticmethod
    def _visible_point(kpts_xy: np.ndarray, kpts_conf: np.ndarray, idx: int) -> Optional[np.ndarray]:
        if idx >= len(kpts_xy) or float(kpts_conf[idx]) < MIN_KPT_CONF:
            return None
        return kpts_xy[idx]

    @classmethod
    def _head_forward(cls, kpts_xy: np.ndarray, kpts_conf: np.ndarray) -> bool:
        nose = cls._visible_point(kpts_xy, kpts_conf, NOSE)
        left_eye = cls._visible_point(kpts_xy, kpts_conf, LEFT_EYE)
        right_eye = cls._visible_point(kpts_xy, kpts_conf, RIGHT_EYE)
        left_ear = cls._visible_point(kpts_xy, kpts_conf, LEFT_EAR)
        right_ear = cls._visible_point(kpts_xy, kpts_conf, RIGHT_EAR)

        if nose is None:
            return False

        if left_eye is None or right_eye is None:
            if left_ear is not None and right_ear is not None:
                return abs(float(right_ear[0] - left_ear[0])) > 20.0
            return False

        eye_center_x = float((left_eye[0] + right_eye[0]) / 2.0)
        eye_span = max(abs(float(right_eye[0] - left_eye[0])), 1.0)
        nose_offset_ratio = abs(float(nose[0] - eye_center_x)) / eye_span

        eye_line_y = float((left_eye[1] + right_eye[1]) / 2.0)
        downward_ratio = float(nose[1] - eye_line_y) / eye_span

        is_centered = nose_offset_ratio <= 0.55
        not_looking_down = downward_ratio <= 1.05

        if left_ear is not None and right_ear is not None:
            ear_balance = abs(float((nose[0] - left_ear[0]) - (right_ear[0] - nose[0])))
            ear_span = max(abs(float(right_ear[0] - left_ear[0])), 1.0)
            return is_centered and not_looking_down and (ear_balance / ear_span) <= 0.7

        return is_centered and not_looking_down

    @classmethod
    def _torso_center(cls, kpts_xy: np.ndarray, kpts_conf: np.ndarray) -> Optional[Tuple[float, float]]:
        idxs = [LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP]
        valid = []
        for idx in idxs:
            pt = cls._visible_point(kpts_xy, kpts_conf, idx)
            if pt is not None:
                valid.append(pt)

        if len(valid) < 2:
            return None

        arr = np.array(valid)
        return float(arr[:, 0].mean()), float(arr[:, 1].mean())

    @staticmethod
    def _classify_activity(motion_norm: float, still_count: int) -> str:
        if motion_norm >= CHAOTIC_MOTION_NORM:
            return "chaotic"
        if motion_norm < STILL_MOTION_NORM:
            return "still_disengaged" if still_count >= STILL_FRAME_LIMIT else "still"
        if motion_norm <= ACTIVE_MOTION_NORM_MAX:
            return "active"
        return "restless"

    def analyze(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        annotated = frame.copy()
        result = self.model.predict(
            source=frame,
            conf=self.conf_thres,
            imgsz=self.imgsz,
            classes=[0],
            verbose=False,
        )[0]

        if result.boxes is None or len(result.boxes) == 0 or result.keypoints is None:
            self.motion.update([])
            metrics = {
                "timestamp": datetime.utcnow().replace(microsecond=0).isoformat(),
                "total_persons": 0,
                "engaged": 0,
                "distracted": 0,
                "engagement_percent": 0,
            }
            cv2.putText(annotated, "Engagement: Low (0%)", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            return annotated, metrics

        boxes = result.boxes.xyxy.cpu().numpy()
        keypoints_xy = result.keypoints.xy.cpu().numpy()
        keypoints_conf = result.keypoints.conf.cpu().numpy()

        torso_centers: List[Tuple[float, float]] = []
        box_diags: List[float] = []
        head_forward_list: List[bool] = []

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = [int(v) for v in box]
            kxy = keypoints_xy[i]
            kcf = keypoints_conf[i]

            head_forward_list.append(self._head_forward(kxy, kcf))
            center = self._torso_center(kxy, kcf)
            if center is None:
                center = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

            torso_centers.append(center)
            box_diags.append(max(float(np.hypot(x2 - x1, y2 - y1)), 1.0))

        motion_data = self.motion.update(torso_centers)

        engaged_count = 0
        distracted_count = 0

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = [int(v) for v in box]
            motion_px, still_count = motion_data[i]
            motion_norm = motion_px / box_diags[i]
            activity = self._classify_activity(motion_norm, still_count)

            engaged = head_forward_list[i] and activity in {"active", "still"}
            if activity in {"chaotic", "restless", "still_disengaged"}:
                engaged = False

            if engaged:
                engaged_count += 1
                color = (0, 200, 0)
                label = "Engaged"
            else:
                distracted_count += 1
                color = (0, 0, 255)
                label = "Distracted"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        total_persons = len(boxes)
        engaged_ratio = (engaged_count / total_persons) if total_persons else 0.0
        engagement_percent = int(round(engaged_ratio * 100))

        if engaged_ratio >= 0.7:
            score = "High"
            score_color = (0, 200, 0)
        elif engaged_ratio >= 0.4:
            score = "Medium"
            score_color = (0, 215, 255)
        else:
            score = "Low"
            score_color = (0, 0, 255)

        overlay = f"Engagement: {score} ({engagement_percent}%) | Persons: {total_persons}"
        cv2.putText(annotated, overlay, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, score_color, 2)

        metrics = {
            "timestamp": datetime.utcnow().replace(microsecond=0).isoformat(),
            "total_persons": total_persons,
            "engaged": engaged_count,
            "distracted": distracted_count,
            "engagement_percent": engagement_percent,
        }
        return annotated, metrics


def _parse_camera_source(raw_source: str, webcam_index: int) -> Union[int, str]:
    source = (raw_source or "").strip()
    if not source:
        return webcam_index

    if source.isdigit():
        return int(source)

    return source


def _status_from_percent(percent: float) -> str:
    if percent >= 70:
        return EngagementLog.STATUS_HIGH
    if percent >= 40:
        return EngagementLog.STATUS_MEDIUM
    return EngagementLog.STATUS_LOW


class EngagementMonitorService:
    def __init__(self) -> None:
        self.enabled = bool(getattr(settings, "ENGAGEMENT_MONITOR_ENABLED", True))
        self.camera_source = _parse_camera_source(
            raw_source=getattr(settings, "ENGAGEMENT_CAMERA_SOURCE", ""),
            webcam_index=int(getattr(settings, "ENGAGEMENT_WEBCAM_INDEX", 0)),
        )
        self.webcam_fallback_enabled = bool(getattr(settings, "ENGAGEMENT_WEBCAM_FALLBACK", True))
        self.webcam_index = int(getattr(settings, "ENGAGEMENT_WEBCAM_INDEX", 0))
        self.model_path = str(getattr(settings, "ENGAGEMENT_MODEL_PATH", ""))
        self.conf_thres = float(getattr(settings, "ENGAGEMENT_CONF_THRESHOLD", 0.3))
        self.imgsz = int(getattr(settings, "ENGAGEMENT_IMAGE_SIZE", 640))
        self.log_interval_sec = max(5, int(getattr(settings, "ENGAGEMENT_LOG_INTERVAL_SECONDS", 10)))
        self.reconnect_delay_sec = max(1.0, float(getattr(settings, "ENGAGEMENT_RECONNECT_DELAY_SECONDS", 2.0)))
        self.max_fps = max(0, int(getattr(settings, "ENGAGEMENT_MAX_FPS", 0)))
        self.show_window = bool(getattr(settings, "ENGAGEMENT_SHOW_WINDOW", False))
        self.window_title = str(getattr(settings, "ENGAGEMENT_WINDOW_TITLE", "Classroom Engagement Monitor"))
        self.class_name = str(getattr(settings, "ENGAGEMENT_CLASS_NAME", "Classroom A"))
        self.period = int(getattr(settings, "ENGAGEMENT_PERIOD", 1))

        self.snapshot_root = Path(settings.MEDIA_ROOT) / "engagement" / "snapshots"
        self.snapshot_root.mkdir(parents=True, exist_ok=True)

        self._analyzer: Optional[EngagementAnalyzer] = None
        self._window: List[float] = []
        self._last_flush = time.time()

    def _render_window(self, frame: np.ndarray) -> None:
        if not self.show_window:
            return

        try:
            cv2.imshow(self.window_title, frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                logger.info("[ENGAGEMENT_MONITOR] OpenCV window hidden after q key press")
                self.show_window = False
                cv2.destroyWindow(self.window_title)
        except Exception:
            logger.exception("[ENGAGEMENT_MONITOR] OpenCV display failed; disabling window rendering")
            self.show_window = False

    def _build_analyzer(self) -> Optional[EngagementAnalyzer]:
        model_file = Path(self.model_path)
        if not model_file.exists():
            logger.error("[ENGAGEMENT_MONITOR] Model not found at %s", model_file)
            return None
        return EngagementAnalyzer(model_path=str(model_file), conf_thres=self.conf_thres, imgsz=self.imgsz)

    def _open_capture(self, source: Union[int, str]) -> Optional[cv2.VideoCapture]:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            cap.release()
            return None

        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        return cap

    def _get_capture(self) -> Optional[cv2.VideoCapture]:
        cap = self._open_capture(self.camera_source)
        if cap is not None:
            return cap

        if self.webcam_fallback_enabled and self.camera_source != self.webcam_index:
            logger.warning(
                "[ENGAGEMENT_MONITOR] Could not open camera source %s. Falling back to webcam index %s.",
                self.camera_source,
                self.webcam_index,
            )
            return self._open_capture(self.webcam_index)

        return None

    def _save_snapshot(self, frame: np.ndarray, now: datetime) -> str:
        stamp = now.strftime("%Y%m%d_%H%M%S")
        file_name = f"engagement_{stamp}.jpg"
        abs_path = self.snapshot_root / file_name
        rel_path = Path("engagement") / "snapshots" / file_name

        ok = cv2.imwrite(str(abs_path), frame)
        if not ok:
            logger.warning("[ENGAGEMENT_MONITOR] Snapshot save failed: %s", abs_path)
            return ""

        return rel_path.as_posix()

    def _flush_window(self, frame: np.ndarray, metrics: dict) -> None:
        if not self._window:
            return

        avg_percent = round(float(np.mean(self._window)), 2)
        now = timezone.now()
        snapshot_path = self._save_snapshot(frame, now)

        close_old_connections()
        EngagementLog.objects.create(
            class_name=self.class_name,
            date=timezone.localdate(),
            period=self.period,
            timestamp=now,
            total_persons=int(metrics.get("total_persons", 0) or 0),
            engaged_count=int(metrics.get("engaged", 0) or 0),
            distracted_count=int(metrics.get("distracted", 0) or 0),
            engagement_percent=avg_percent,
            status=_status_from_percent(avg_percent),
            snapshot_path=snapshot_path,
        )
        close_old_connections()

        logger.info(
            "[ENGAGEMENT_MONITOR] Logged engagement %.2f%% (persons=%s engaged=%s distracted=%s)",
            avg_percent,
            metrics.get("total_persons", 0),
            metrics.get("engaged", 0),
            metrics.get("distracted", 0),
        )
        self._window.clear()

    def run_forever(self) -> None:
        if not self.enabled:
            logger.info("[ENGAGEMENT_MONITOR] Disabled by ENGAGEMENT_MONITOR_ENABLED=false")
            return

        self._analyzer = self._build_analyzer()
        if self._analyzer is None:
            return

        logger.info("[ENGAGEMENT_MONITOR] Starting live monitor with source=%s", self.camera_source)

        while True:
            cap = self._get_capture()
            if cap is None:
                logger.warning("[ENGAGEMENT_MONITOR] Camera unavailable, retrying in %.1fs", self.reconnect_delay_sec)
                time.sleep(self.reconnect_delay_sec)
                continue

            try:
                while True:
                    loop_start = time.time()
                    ok, frame = cap.read()
                    if not ok or frame is None:
                        logger.warning("[ENGAGEMENT_MONITOR] Frame read failed; reopening capture")
                        time.sleep(0.2)
                        break

                    annotated, metrics = self._analyzer.analyze(frame)
                    self._window.append(float(metrics.get("engagement_percent", 0)))
                    self._render_window(annotated)

                    now = time.time()
                    if now - self._last_flush >= self.log_interval_sec:
                        self._flush_window(annotated, metrics)
                        self._last_flush = now

                    if self.max_fps > 0:
                        elapsed = time.time() - loop_start
                        target = 1.0 / self.max_fps
                        if elapsed < target:
                            time.sleep(target - elapsed)
            except Exception:
                logger.exception("[ENGAGEMENT_MONITOR] Unexpected processing error")
                time.sleep(self.reconnect_delay_sec)
            finally:
                cap.release()
                if self.show_window:
                    try:
                        cv2.destroyWindow(self.window_title)
                    except Exception:
                        pass


_monitor_thread: Optional[threading.Thread] = None
_monitor_lock = threading.Lock()


def start_engagement_monitor_background() -> bool:
    global _monitor_thread
    with _monitor_lock:
        if _monitor_thread and _monitor_thread.is_alive():
            logger.debug("[ENGAGEMENT_MONITOR] Background thread already running")
            return False

        service = EngagementMonitorService()
        if not service.enabled:
            logger.info("[ENGAGEMENT_MONITOR] Not started (disabled)")
            return False

        _monitor_thread = threading.Thread(
            target=service.run_forever,
            name="engagement-monitor",
            daemon=True,
        )
        _monitor_thread.start()
        return True
