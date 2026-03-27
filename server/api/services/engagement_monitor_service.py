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

from api.models import EngagementLog, SafetyAlert
from api.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


# COCO keypoint indices for YOLOv8 pose model.
NOSE = 0
LEFT_EYE = 1
RIGHT_EYE = 2
LEFT_EAR = 3
RIGHT_EAR = 4
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_WRIST = 9
RIGHT_WRIST = 10
LEFT_HIP = 11
RIGHT_HIP = 12

MIN_KPT_CONF = 0.35
STILL_MOTION_NORM = 0.008
ACTIVE_MOTION_NORM_MAX = 0.045
CHAOTIC_MOTION_NORM = 0.09
STILL_FRAME_LIMIT = 30

RAGGING_CLUSTER_WARNING_COLOR = (0, 255, 255)
RAGGING_CLUSTER_ALERT_COLOR = (0, 0, 255)
RAGGING_NORMAL_COLOR = (0, 255, 0)
RAGGING_AGGRESSIVE_COLOR = (0, 0, 255)
RAGGING_VULNERABLE_COLOR = (255, 0, 0)

# Standard COCO skeleton connections.
RAGGING_SKELETON = [
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 6),
    (5, 11),
    (6, 12),
    (11, 12),
    (11, 13),
    (13, 15),
    (12, 14),
    (14, 16),
]


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


class RaggingAnalyzer:
    """Frame-level ragging scoring using person clusters + pose heuristics."""

    def __init__(
        self,
        person_model_path: str,
        pose_model_path: str,
        conf_thres: float,
        imgsz: int,
        detection_interval: int,
        cluster_distance_px: float,
        isolation_ratio: float,
        alert_cooldown_sec: int,
    ) -> None:
        self.person_model = YOLO(person_model_path)
        self.pose_model = None
        try:
            self.pose_model = YOLO(pose_model_path)
        except Exception:
            logger.exception("[RAGGING_MONITOR] Pose model failed to load; continuing with cluster-only scoring")

        self.conf_thres = conf_thres
        self.imgsz = imgsz
        self.detection_interval = max(1, detection_interval)
        self.cluster_distance_px = max(40.0, float(cluster_distance_px))
        self.isolation_ratio = max(1.05, float(isolation_ratio))
        self.alert_cooldown_sec = max(5, int(alert_cooldown_sec))

        self.frame_index = 0
        self.last_alert_epoch = 0.0

        self.person_boxes: List[Tuple[int, int, int, int]] = []
        self.person_centers: List[Tuple[int, int]] = []
        self.person_states: List[str] = []
        self.person_labels: List[str] = []
        self.cluster_membership: List[int] = []
        self.suspicious_clusters: List[dict] = []
        self.pose_draw_items: List[dict] = []

        self.cluster_score = 0
        self.pose_score = 0
        self.final_score = 0
        self.threat_level = "NORMAL"

    @staticmethod
    def _pairwise_distances(centers: np.ndarray) -> np.ndarray:
        deltas = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
        return np.sqrt(np.sum(deltas * deltas, axis=2))

    @staticmethod
    def _safe_kpt(kpts_xy: np.ndarray, kpts_conf: np.ndarray, idx: int) -> Optional[np.ndarray]:
        if idx >= kpts_xy.shape[0] or float(kpts_conf[idx]) < MIN_KPT_CONF:
            return None
        return kpts_xy[idx]

    def _find_suspicious_clusters(self) -> None:
        self.suspicious_clusters = []
        if len(self.person_centers) < 4:
            return

        centers_np = np.array(self.person_centers, dtype=np.float32)
        dist_matrix = self._pairwise_distances(centers_np)
        visited = set()
        components: List[List[int]] = []

        for idx in range(len(self.person_centers)):
            if idx in visited:
                continue

            stack = [idx]
            comp: List[int] = []

            while stack:
                node = stack.pop()
                if node in visited:
                    continue

                visited.add(node)
                comp.append(node)

                neighbors = np.where(
                    (dist_matrix[node] <= self.cluster_distance_px) & (np.arange(len(self.person_centers)) != node)
                )[0]
                for neighbor in neighbors:
                    nidx = int(neighbor)
                    if nidx not in visited:
                        stack.append(nidx)

            components.append(comp)

        for comp in components:
            if len(comp) < 4:
                continue

            comp_dist = dist_matrix[np.ix_(comp, comp)].copy()
            np.fill_diagonal(comp_dist, np.inf)
            nearest_dists = np.min(comp_dist, axis=1)
            finite_nearest = nearest_dists[np.isfinite(nearest_dists)]
            if finite_nearest.size == 0:
                continue

            median_nearest = float(np.median(finite_nearest))
            iso_local_idx = int(np.argmax(nearest_dists))
            iso_global_idx = int(comp[iso_local_idx])
            max_nearest = float(nearest_dists[iso_local_idx])

            isolated = (
                median_nearest > 0.0
                and max_nearest >= self.isolation_ratio * median_nearest
                and max_nearest > 40.0
            )

            if not isolated:
                continue

            cluster = {
                "id": len(self.suspicious_clusters) + 1,
                "members": [int(i) for i in comp],
                "isolated": iso_global_idx,
                "size": len(comp),
                "aggressive_count": 0,
                "vulnerable_count": 0,
                "aggressive_present": False,
                "vulnerable_present": False,
            }
            self.suspicious_clusters.append(cluster)

            cluster_idx = len(self.suspicious_clusters) - 1
            for person_idx in comp:
                self.cluster_membership[int(person_idx)] = cluster_idx
                if self.person_states[int(person_idx)] == "normal":
                    self.person_states[int(person_idx)] = "suspicious"

    def _run_pose_analysis(self, frame: np.ndarray) -> None:
        if not self.suspicious_clusters or self.pose_model is None or not self.person_centers:
            return

        pose_result = self.pose_model.predict(
            source=frame,
            conf=self.conf_thres,
            imgsz=self.imgsz,
            classes=[0],
            verbose=False,
        )[0]

        if pose_result.boxes is None or len(pose_result.boxes) == 0 or pose_result.keypoints is None:
            return

        pose_boxes = pose_result.boxes.xyxy.cpu().numpy()
        pose_kpts_xy = pose_result.keypoints.xy.cpu().numpy()

        if pose_result.keypoints.conf is not None:
            pose_kpts_conf = pose_result.keypoints.conf.cpu().numpy()
        else:
            pose_kpts_conf = np.ones((pose_kpts_xy.shape[0], pose_kpts_xy.shape[1]), dtype=np.float32)

        detection_centers = np.array(self.person_centers, dtype=np.float32)

        for idx in range(min(len(pose_boxes), len(pose_kpts_xy))):
            box = pose_boxes[idx]
            center = np.array([(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0], dtype=np.float32)

            deltas = detection_centers - center
            dists = np.sqrt(np.sum(deltas * deltas, axis=1))
            matched_person_idx = int(np.argmin(dists))
            if float(dists[matched_person_idx]) > 120.0:
                continue

            cluster_idx = self.cluster_membership[matched_person_idx]
            if cluster_idx < 0:
                continue

            kpts = pose_kpts_xy[idx]
            kconf = pose_kpts_conf[idx]

            nose = self._safe_kpt(kpts, kconf, NOSE)
            left_shoulder = self._safe_kpt(kpts, kconf, LEFT_SHOULDER)
            right_shoulder = self._safe_kpt(kpts, kconf, RIGHT_SHOULDER)
            left_wrist = self._safe_kpt(kpts, kconf, LEFT_WRIST)
            right_wrist = self._safe_kpt(kpts, kconf, RIGHT_WRIST)
            left_hip = self._safe_kpt(kpts, kconf, LEFT_HIP)
            right_hip = self._safe_kpt(kpts, kconf, RIGHT_HIP)

            torso_points = []
            if left_shoulder is not None:
                torso_points.append(left_shoulder)
            if right_shoulder is not None:
                torso_points.append(right_shoulder)
            if left_hip is not None:
                torso_points.append(left_hip)
            if right_hip is not None:
                torso_points.append(right_hip)

            hip_points = []
            if left_hip is not None:
                hip_points.append(left_hip)
            if right_hip is not None:
                hip_points.append(right_hip)

            torso_center = np.mean(np.array(torso_points), axis=0) if torso_points else None
            hip_center = np.mean(np.array(hip_points), axis=0) if hip_points else None

            aggressive_flags = []
            arms_raised = False
            if left_wrist is not None and left_shoulder is not None and float(left_wrist[1]) < float(left_shoulder[1]) - 30.0:
                arms_raised = True
            if right_wrist is not None and right_shoulder is not None and float(right_wrist[1]) < float(right_shoulder[1]) - 30.0:
                arms_raised = True
            aggressive_flags.append(arms_raised)

            leaning_forward = False
            if nose is not None and hip_center is not None and abs(float(nose[0]) - float(hip_center[0])) > 35.0:
                leaning_forward = True
            aggressive_flags.append(leaning_forward)

            pointing = False
            if torso_center is not None and hip_center is not None and left_wrist is not None and right_wrist is not None:
                left_torso_dist = float(np.linalg.norm(left_wrist - torso_center))
                right_torso_dist = float(np.linalg.norm(right_wrist - torso_center))
                left_hip_dist = float(np.linalg.norm(left_wrist - hip_center))
                right_hip_dist = float(np.linalg.norm(right_wrist - hip_center))
                if left_torso_dist > 90.0 and right_hip_dist < 70.0:
                    pointing = True
                if right_torso_dist > 90.0 and left_hip_dist < 70.0:
                    pointing = True
            aggressive_flags.append(pointing)

            aggressive_count = int(sum(1 for flag in aggressive_flags if flag))

            vulnerable_flags = []
            shoulder_points = []
            if left_shoulder is not None:
                shoulder_points.append(left_shoulder)
            if right_shoulder is not None:
                shoulder_points.append(right_shoulder)

            hunched = False
            if shoulder_points and hip_points:
                shoulder_center = np.mean(np.array(shoulder_points), axis=0)
                shoulder_y = float(shoulder_center[1])
                hip_y = float(np.mean(np.array(hip_points)[:, 1]))
                if (hip_y - shoulder_y) < 35.0:
                    hunched = True
            vulnerable_flags.append(hunched)

            crossed = False
            if torso_center is not None and left_wrist is not None and right_wrist is not None:
                torso_x = float(torso_center[0])
                if float(left_wrist[0]) > torso_x + 5.0 and float(right_wrist[0]) < torso_x - 5.0:
                    crossed = True
            vulnerable_flags.append(crossed)

            vulnerable_count = int(sum(1 for flag in vulnerable_flags if flag))

            if aggressive_count > 0:
                self.person_states[matched_person_idx] = "aggressive"
                self.person_labels[matched_person_idx] = "Aggressive"
            elif vulnerable_count > 0:
                self.person_states[matched_person_idx] = "vulnerable"
                self.person_labels[matched_person_idx] = "Vulnerable"

            cluster = self.suspicious_clusters[cluster_idx]
            cluster["aggressive_count"] += aggressive_count
            cluster["vulnerable_count"] += vulnerable_count
            if aggressive_count > 0:
                cluster["aggressive_present"] = True
            if vulnerable_count > 0:
                cluster["vulnerable_present"] = True

            self.pose_draw_items.append(
                {
                    "kpts": kpts,
                    "valid": (kconf > MIN_KPT_CONF),
                    "aggressive": aggressive_count > 0,
                }
            )

    def _run_inference(self, frame: np.ndarray) -> None:
        self.person_boxes = []
        self.person_centers = []
        self.person_states = []
        self.person_labels = []
        self.cluster_membership = []
        self.suspicious_clusters = []
        self.pose_draw_items = []
        self.cluster_score = 0
        self.pose_score = 0
        self.final_score = 0
        self.threat_level = "NORMAL"

        result = self.person_model.predict(
            source=frame,
            conf=self.conf_thres,
            imgsz=self.imgsz,
            classes=[0],
            verbose=False,
        )[0]

        if result.boxes is None or len(result.boxes) == 0:
            return

        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy().astype(int)
        confs = result.boxes.conf.cpu().numpy()

        for idx in range(len(boxes)):
            if classes[idx] != 0:
                continue
            if float(confs[idx]) < self.conf_thres:
                continue

            x1, y1, x2, y2 = boxes[idx]
            xi1, yi1, xi2, yi2 = int(x1), int(y1), int(x2), int(y2)
            if xi2 <= xi1 or yi2 <= yi1:
                continue

            self.person_boxes.append((xi1, yi1, xi2, yi2))
            self.person_centers.append(((xi1 + xi2) // 2, (yi1 + yi2) // 2))

        person_count = len(self.person_boxes)
        self.person_states = ["normal"] * person_count
        self.person_labels = ["Normal"] * person_count
        self.cluster_membership = [-1] * person_count

        if person_count == 0:
            return

        self._find_suspicious_clusters()

        if self.suspicious_clusters:
            max_cluster_size = max(cluster["size"] for cluster in self.suspicious_clusters)
            self.cluster_score = 60 if max_cluster_size >= 5 else 40

        self._run_pose_analysis(frame)

        self.pose_score = 0
        for cluster in self.suspicious_clusters:
            self.pose_score += int(cluster["aggressive_count"]) * 15
            self.pose_score += int(cluster["vulnerable_count"]) * 10
            if cluster["aggressive_present"] and cluster["vulnerable_present"]:
                self.pose_score += 20

        self.final_score = int(self.cluster_score + self.pose_score)
        if self.final_score == 0:
            self.threat_level = "NORMAL"
        elif self.final_score <= 49:
            self.threat_level = "WARNING"
        elif self.final_score <= 79:
            self.threat_level = "ALERT"
        else:
            self.threat_level = "CRITICAL"

    def _draw_cluster_overlay(self, annotated: np.ndarray) -> None:
        if not self.suspicious_clusters:
            return

        overlay = annotated.copy()
        for cluster in self.suspicious_clusters:
            points = np.array([self.person_centers[idx] for idx in cluster["members"]], dtype=np.int32)
            color = RAGGING_CLUSTER_ALERT_COLOR if self.final_score >= 50 else RAGGING_CLUSTER_WARNING_COLOR

            if len(points) >= 3:
                hull = cv2.convexHull(points)
                cv2.fillPoly(overlay, [hull], color)
                cv2.polylines(annotated, [hull], True, color, 2)
            elif len(points) == 2:
                cv2.line(annotated, tuple(points[0]), tuple(points[1]), color, 2)

            iso_idx = int(cluster["isolated"])
            if 0 <= iso_idx < len(self.person_boxes):
                x1, y1, x2, y2 = self.person_boxes[iso_idx]
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                radius = int(max(24, 0.6 * max(x2 - x1, y2 - y1)))
                for angle in range(0, 360, 24):
                    if (angle // 24) % 2 == 0:
                        a1 = np.deg2rad(angle)
                        a2 = np.deg2rad(angle + 12)
                        p1 = (int(center_x + radius * np.cos(a1)), int(center_y + radius * np.sin(a1)))
                        p2 = (int(center_x + radius * np.cos(a2)), int(center_y + radius * np.sin(a2)))
                        cv2.line(annotated, p1, p2, (255, 255, 255), 2)

        blended = cv2.addWeighted(overlay, 0.22, annotated, 0.78, 0)
        annotated[:, :] = blended

    def _draw_pose_overlay(self, annotated: np.ndarray) -> None:
        for pose_item in self.pose_draw_items:
            kpts = pose_item["kpts"]
            valid = pose_item["valid"]
            color = RAGGING_AGGRESSIVE_COLOR if pose_item["aggressive"] else RAGGING_NORMAL_COLOR

            for edge in RAGGING_SKELETON:
                a, b = edge
                if bool(valid[a]) and bool(valid[b]):
                    p1 = (int(kpts[a][0]), int(kpts[a][1]))
                    p2 = (int(kpts[b][0]), int(kpts[b][1]))
                    cv2.line(annotated, p1, p2, color, 2)

            for kidx in range(kpts.shape[0]):
                if bool(valid[kidx]):
                    cv2.circle(annotated, (int(kpts[kidx][0]), int(kpts[kidx][1])), 3, color, -1)

    def _draw_person_boxes(self, annotated: np.ndarray) -> None:
        for idx, box in enumerate(self.person_boxes):
            x1, y1, x2, y2 = box
            state = self.person_states[idx] if idx < len(self.person_states) else "normal"
            label = self.person_labels[idx] if idx < len(self.person_labels) else "Normal"

            color = RAGGING_NORMAL_COLOR
            if state == "suspicious":
                color = RAGGING_CLUSTER_WARNING_COLOR
                label = "Normal"
            elif state == "aggressive":
                color = RAGGING_AGGRESSIVE_COLOR
                label = "Aggressive"
            elif state == "vulnerable":
                color = RAGGING_VULNERABLE_COLOR
                label = "Vulnerable"

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
            ly1 = max(0, y1 - text_size[1] - 10)
            ly2 = max(0, y1)
            cv2.rectangle(annotated, (x1, ly1), (x1 + text_size[0] + 8, ly2), color, -1)
            cv2.putText(
                annotated,
                label,
                (x1 + 4, max(12, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 0, 0),
                2,
                cv2.LINE_AA,
            )

    def _draw_header(self, annotated: np.ndarray) -> None:
        panel_x1, panel_y1, panel_x2, panel_y2 = 10, 10, 360, 130
        panel = annotated.copy()
        cv2.rectangle(panel, (panel_x1, panel_y1), (panel_x2, panel_y2), (0, 0, 0), -1)
        blended = cv2.addWeighted(panel, 0.45, annotated, 0.55, 0)
        annotated[:, :] = blended
        cv2.rectangle(annotated, (panel_x1, panel_y1), (panel_x2, panel_y2), (255, 255, 255), 1)

        status_color = (0, 200, 0)
        if self.threat_level == "WARNING":
            status_color = (0, 215, 255)
        elif self.threat_level in {"ALERT", "CRITICAL"}:
            status_color = (0, 0, 255)

        cv2.putText(annotated, "Ragging Monitor", (20, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.putText(
            annotated,
            f"Persons: {len(self.person_boxes)}",
            (20, 58),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            annotated,
            f"Suspicious Clusters: {len(self.suspicious_clusters)}",
            (20, 82),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            annotated,
            f"Threat Score: {self.final_score}",
            (20, 106),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            annotated,
            f"Status: {self.threat_level}",
            (20, 128),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            status_color,
            2,
        )

    def _draw_alert_banner(self, annotated: np.ndarray) -> None:
        if self.threat_level not in {"ALERT", "CRITICAL"}:
            return

        if int(time.time() * 2) % 2 == 0:
            cv2.rectangle(annotated, (0, 0), (annotated.shape[1] - 1, annotated.shape[0] - 1), (0, 0, 255), 12)

        message = "RAGGING ALERT DETECTED"
        size = cv2.getTextSize(message, cv2.FONT_HERSHEY_DUPLEX, 0.9, 2)[0]
        cx = max(10, (annotated.shape[1] - size[0]) // 2)
        cy = annotated.shape[0] // 2

        cv2.rectangle(annotated, (cx - 12, cy - size[1] - 14), (cx + size[0] + 12, cy + 10), (0, 0, 0), -1)
        cv2.putText(annotated, message, (cx, cy), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 255), 2, cv2.LINE_AA)

    def analyze(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        self.frame_index += 1

        if self.frame_index % self.detection_interval == 0:
            try:
                self._run_inference(frame)
            except Exception:
                logger.exception("[RAGGING_MONITOR] Inference failed")

        annotated = frame.copy()
        try:
            self._draw_cluster_overlay(annotated)
            self._draw_pose_overlay(annotated)
            self._draw_person_boxes(annotated)
            self._draw_header(annotated)
            self._draw_alert_banner(annotated)
        except Exception:
            logger.exception("[RAGGING_MONITOR] Overlay rendering failed")

        total_aggressive = sum(int(cluster.get("aggressive_count", 0)) for cluster in self.suspicious_clusters)
        largest_cluster = max([int(cluster.get("size", 0)) for cluster in self.suspicious_clusters], default=0)

        should_alert = False
        now_epoch = time.time()
        if self.threat_level in {"ALERT", "CRITICAL"}:
            if now_epoch - self.last_alert_epoch >= self.alert_cooldown_sec:
                should_alert = True
                self.last_alert_epoch = now_epoch

        metrics = {
            "persons": len(self.person_boxes),
            "clusters": len(self.suspicious_clusters),
            "threat_score": int(self.final_score),
            "threat_level": self.threat_level,
            "aggressive_count": int(total_aggressive),
            "largest_cluster": int(largest_cluster),
            "should_alert": should_alert,
            "description": (
                f"Cluster of {largest_cluster} persons detected with {total_aggressive} aggressive poses"
                if largest_cluster > 0
                else "Suspicious ragging pattern detected"
            ),
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
        self.window_title = str(getattr(settings, "ENGAGEMENT_WINDOW_TITLE", "Classroom Safety and Engagement Monitor"))
        self.class_name = str(getattr(settings, "ENGAGEMENT_CLASS_NAME", "Classroom A"))
        self.period = int(getattr(settings, "ENGAGEMENT_PERIOD", 1))

        self.ragging_enabled = bool(getattr(settings, "RAGGING_MONITOR_ENABLED", True))
        self.ragging_person_model_path = str(getattr(settings, "RAGGING_PERSON_MODEL_PATH", "yolov8n.pt"))
        self.ragging_pose_model_path = str(getattr(settings, "RAGGING_POSE_MODEL_PATH", "yolov8n-pose.pt"))
        self.ragging_conf_thres = float(getattr(settings, "RAGGING_CONF_THRESHOLD", 0.3))
        self.ragging_imgsz = int(getattr(settings, "RAGGING_IMAGE_SIZE", 640))
        self.ragging_detection_interval = int(getattr(settings, "RAGGING_DETECTION_INTERVAL", 2))
        self.ragging_cluster_distance = float(getattr(settings, "RAGGING_CLUSTER_DISTANCE", 150.0))
        self.ragging_isolation_ratio = float(getattr(settings, "RAGGING_ISOLATION_RATIO", 1.35))
        self.ragging_alert_cooldown = int(getattr(settings, "RAGGING_ALERT_COOLDOWN_SECONDS", 30))
        self.ragging_location = str(getattr(settings, "RAGGING_LOCATION", "Classroom"))

        self.snapshot_root = Path(settings.MEDIA_ROOT) / "engagement" / "snapshots"
        self.snapshot_root.mkdir(parents=True, exist_ok=True)
        self.safety_snapshot_root = Path(settings.MEDIA_ROOT) / "safety" / "snapshots"
        self.safety_snapshot_root.mkdir(parents=True, exist_ok=True)

        self._analyzer: Optional[EngagementAnalyzer] = None
        self._ragging_analyzer: Optional[RaggingAnalyzer] = None
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

    def _build_ragging_analyzer(self) -> Optional[RaggingAnalyzer]:
        if not self.ragging_enabled:
            logger.info("[RAGGING_MONITOR] Disabled by RAGGING_MONITOR_ENABLED=false")
            return None

        try:
            return RaggingAnalyzer(
                person_model_path=self.ragging_person_model_path,
                pose_model_path=self.ragging_pose_model_path,
                conf_thres=self.ragging_conf_thres,
                imgsz=self.ragging_imgsz,
                detection_interval=self.ragging_detection_interval,
                cluster_distance_px=self.ragging_cluster_distance,
                isolation_ratio=self.ragging_isolation_ratio,
                alert_cooldown_sec=self.ragging_alert_cooldown,
            )
        except Exception:
            logger.exception("[RAGGING_MONITOR] Failed to initialize ragging analyzer")
            return None

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

    def _save_safety_snapshot(self, frame: np.ndarray, now: datetime) -> str:
        stamp = now.strftime("%Y%m%d_%H%M%S")
        file_name = f"ragging_{stamp}.jpg"
        abs_path = self.safety_snapshot_root / file_name
        rel_path = Path("safety") / "snapshots" / file_name

        ok = cv2.imwrite(str(abs_path), frame)
        if not ok:
            logger.warning("[RAGGING_MONITOR] Snapshot save failed: %s", abs_path)
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

    def _emit_ragging_alert(self, ragging_frame: np.ndarray, ragging_metrics: dict) -> None:
        try:
            now = timezone.now()
            snapshot_path = self._save_safety_snapshot(ragging_frame, now)

            close_old_connections()
            alert = SafetyAlert.objects.create(
                alert_type=SafetyAlert.TYPE_RAGGING,
                threat_level=SafetyAlert.THREAT_HIGH,
                class_name=self.class_name,
                location=self.ragging_location,
                person_count=int(ragging_metrics.get("persons", 0) or 0),
                description=str(ragging_metrics.get("description", "")),
                snapshot=snapshot_path or None,
            )
            close_old_connections()

            try:
                NotificationService().send_safety_alert_admin(alert)
            except Exception:
                logger.exception("[RAGGING_MONITOR] Alert created but notification send failed")

            logger.info(
                "[RAGGING_MONITOR] Alert saved (score=%s level=%s persons=%s)",
                ragging_metrics.get("threat_score", 0),
                ragging_metrics.get("threat_level", "UNKNOWN"),
                ragging_metrics.get("persons", 0),
            )
        except Exception:
            logger.exception("[RAGGING_MONITOR] Failed to persist ragging alert")

    def run_forever(self) -> None:
        if not self.enabled:
            logger.info("[ENGAGEMENT_MONITOR] Disabled by ENGAGEMENT_MONITOR_ENABLED=false")
            return

        self._analyzer = self._build_analyzer()
        if self._analyzer is None:
            return

        self._ragging_analyzer = self._build_ragging_analyzer()
        if self.ragging_enabled and self._ragging_analyzer is None:
            logger.warning("[RAGGING_MONITOR] Running in engagement-only mode due to ragging initialization failure")

        logger.info("[ENGAGEMENT_MONITOR] Starting live monitor with source=%s", self.camera_source)
        if self._ragging_analyzer is not None:
            logger.info("[RAGGING_MONITOR] Ragging monitor enabled in side-by-side mode")

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

                    try:
                        engagement_frame, metrics = self._analyzer.analyze(frame)
                    except Exception:
                        logger.exception("[ENGAGEMENT_MONITOR] Engagement inference failed")
                        continue

                    ragging_frame = frame.copy()
                    ragging_metrics = {
                        "should_alert": False,
                        "threat_score": 0,
                        "threat_level": "NORMAL",
                    }

                    if self._ragging_analyzer is not None:
                        try:
                            ragging_frame, ragging_metrics = self._ragging_analyzer.analyze(frame)
                        except Exception:
                            logger.exception("[RAGGING_MONITOR] Ragging inference failed")

                        if bool(ragging_metrics.get("should_alert", False)):
                            self._emit_ragging_alert(ragging_frame, ragging_metrics)
                    else:
                        cv2.putText(
                            ragging_frame,
                            "Ragging monitor disabled",
                            (20, 35),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 0, 255),
                            2,
                        )

                    if ragging_frame.shape[:2] != engagement_frame.shape[:2]:
                        ragging_frame = cv2.resize(
                            ragging_frame,
                            (engagement_frame.shape[1], engagement_frame.shape[0]),
                            interpolation=cv2.INTER_LINEAR,
                        )

                    combined_frame = np.hstack((engagement_frame, ragging_frame))
                    cv2.line(
                        combined_frame,
                        (engagement_frame.shape[1], 0),
                        (engagement_frame.shape[1], combined_frame.shape[0]),
                        (255, 255, 255),
                        2,
                    )

                    self._window.append(float(metrics.get("engagement_percent", 0)))
                    self._render_window(combined_frame)

                    now = time.time()
                    if now - self._last_flush >= self.log_interval_sec:
                        self._flush_window(engagement_frame, metrics)
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
