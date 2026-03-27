import cv2
import numpy as np
import requests
import time
from datetime import datetime
import os
import json
import math
from scipy.spatial.distance import cdist
from ultralytics import YOLO

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
DETECTION_MODEL_PATH = "yolov8n.pt"
POSE_MODEL_PATH = "yolov8n-pose.pt"
WEBCAM_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DETECTION_INTERVAL = 2
PERSON_CONFIDENCE_THRESHOLD = 0.30
CLUSTER_DISTANCE_THRESHOLD = 150.0
ISOLATION_RATIO_THRESHOLD = 1.35
ALERT_COOLDOWN_SECONDS = 30
API_URL = "http://localhost:8000/api/safety/alerts/"
LOCATION_NAME = "Classroom"

# Standard COCO skeleton connections
COCO_SKELETON = [
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

# Runtime status to keep the latest inference state while skipping alternate frames
person_boxes = []
person_centers = []
person_states = []
person_labels = []
cluster_membership = []
suspicious_clusters = []
pose_draw_items = []
final_threat_score = 0
cluster_score = 0
pose_score = 0
threat_level = "NORMAL"
threat_icon = "🟢"

save_alert_snapshot = False
manual_snapshot_request = False
last_alert_send_time = 0.0
alert_sent_recently = False

frame_counter = 0
fps_counter = 0
fps_value = 0.0
fps_tick = time.time()
console_tick = 0.0
previous_threat_level = "NORMAL"

# ------------------------------------------------------------
# Startup: snapshots directory
# ------------------------------------------------------------
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    snapshot_dir = os.path.join(script_dir, "snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)
    print(f"[INFO] Snapshot directory ready: {snapshot_dir}")
except Exception as startup_err:
    print(f"[ERROR] Failed to create snapshot directory: {startup_err}")
    snapshot_dir = "snapshots"

# ------------------------------------------------------------
# Startup: load YOLO models (auto-download on first run)
# ------------------------------------------------------------
person_model = None
pose_model = None

try:
    print("[INFO] Loading person detection model (yolov8n.pt)...")
    person_model = YOLO(DETECTION_MODEL_PATH)
    print("[INFO] Person model loaded.")
except Exception as model_err:
    print(f"[ERROR] Could not load person detection model: {model_err}")

try:
    print("[INFO] Loading pose model (yolov8n-pose.pt)...")
    pose_model = YOLO(POSE_MODEL_PATH)
    print("[INFO] Pose model loaded.")
except Exception as pose_model_err:
    print(f"[ERROR] Could not load pose model: {pose_model_err}")
    print("[WARN] Continuing with clustering-only mode if pose model is unavailable.")

if person_model is None:
    print("[FATAL] Person model is required. Exiting.")
    raise SystemExit(1)

# ------------------------------------------------------------
# Startup: webcam initialization
# ------------------------------------------------------------
try:
    cap = cv2.VideoCapture(WEBCAM_INDEX)
    if not cap.isOpened():
        print(f"[ERROR] Webcam index {WEBCAM_INDEX} not available.")
        raise SystemExit(1)
    print(f"[INFO] Webcam opened successfully at index {WEBCAM_INDEX}.")
except Exception as cam_err:
    print(f"[FATAL] Webcam initialization failed: {cam_err}")
    raise SystemExit(1)

print("[INFO] Press Q to quit, S to save snapshot.")

# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------
try:
    while True:
        alert_sent_recently = False

        # ----------------------------------------------------
        # 1) Read frame
        # ----------------------------------------------------
        try:
            ok, frame = cap.read()
            if not ok or frame is None:
                print("[WARN] Failed to read frame from webcam. Retrying...")
                time.sleep(0.05)
                continue
        except Exception as read_err:
            print(f"[ERROR] Frame read failed: {read_err}")
            continue

        # ----------------------------------------------------
        # 2) Resize frame for faster inference
        # ----------------------------------------------------
        try:
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        except Exception as resize_err:
            print(f"[ERROR] Frame resize failed: {resize_err}")
            continue

        frame_counter += 1
        fps_counter += 1

        # ----------------------------------------------------
        # 3) Every 2nd frame: detect + cluster + pose + score
        # ----------------------------------------------------
        if frame_counter % DETECTION_INTERVAL == 0:
            try:
                # Reset per-inference caches
                person_boxes = []
                person_centers = []
                person_states = []
                person_labels = []
                cluster_membership = []
                suspicious_clusters = []
                pose_draw_items = []
                cluster_score = 0
                pose_score = 0

                # --------------------------------------------
                # 3a) YOLOv8 person detection
                # --------------------------------------------
                try:
                    det_results = person_model(frame, imgsz=640, verbose=False)
                    if len(det_results) > 0 and det_results[0].boxes is not None and len(det_results[0].boxes) > 0:
                        det_boxes_xyxy = det_results[0].boxes.xyxy.cpu().numpy()
                        det_boxes_cls = det_results[0].boxes.cls.cpu().numpy().astype(int)
                        det_boxes_conf = det_results[0].boxes.conf.cpu().numpy()

                        for i in range(len(det_boxes_xyxy)):
                            if det_boxes_cls[i] != 0:
                                continue
                            if float(det_boxes_conf[i]) < PERSON_CONFIDENCE_THRESHOLD:
                                continue

                            x1, y1, x2, y2 = det_boxes_xyxy[i]
                            x1 = int(max(0, min(FRAME_WIDTH - 1, x1)))
                            y1 = int(max(0, min(FRAME_HEIGHT - 1, y1)))
                            x2 = int(max(0, min(FRAME_WIDTH - 1, x2)))
                            y2 = int(max(0, min(FRAME_HEIGHT - 1, y2)))
                            if x2 <= x1 or y2 <= y1:
                                continue

                            person_boxes.append((x1, y1, x2, y2))
                            person_centers.append(((x1 + x2) // 2, (y1 + y2) // 2))
                except Exception as det_err:
                    print(f"[ERROR] Person detection failed: {det_err}")

                person_count = len(person_boxes)
                person_states = ["normal"] * person_count
                person_labels = ["Normal"] * person_count
                cluster_membership = [-1] * person_count

                # --------------------------------------------
                # 3b) Clustering logic (distance graph)
                # --------------------------------------------
                try:
                    if person_count >= 4:
                        centers_np = np.array(person_centers, dtype=np.float32)
                        dist_matrix = cdist(centers_np, centers_np)
                        visited = set()
                        all_clusters = []

                        for idx in range(person_count):
                            if idx in visited:
                                continue
                            stack = [idx]
                            component = []
                            while stack:
                                node = stack.pop()
                                if node in visited:
                                    continue
                                visited.add(node)
                                component.append(node)
                                near_nodes = np.where(
                                    (dist_matrix[node] <= CLUSTER_DISTANCE_THRESHOLD)
                                    & (np.arange(person_count) != node)
                                )[0]
                                for n in near_nodes:
                                    if int(n) not in visited:
                                        stack.append(int(n))
                            all_clusters.append(component)

                        for comp in all_clusters:
                            if len(comp) < 4:
                                continue

                            comp_dist = dist_matrix[np.ix_(comp, comp)].copy()
                            np.fill_diagonal(comp_dist, np.inf)
                            nearest_dists = np.min(comp_dist, axis=1)
                            finite_nearest = nearest_dists[np.isfinite(nearest_dists)]
                            if finite_nearest.size == 0:
                                continue

                            median_nearest = float(np.median(finite_nearest))
                            isolated_local_index = int(np.argmax(nearest_dists))
                            isolated_global_index = int(comp[isolated_local_index])
                            max_nearest = float(nearest_dists[isolated_local_index])

                            isolated_condition = (
                                median_nearest > 0
                                and max_nearest >= ISOLATION_RATIO_THRESHOLD * median_nearest
                                and max_nearest > 40.0
                            )

                            if isolated_condition:
                                suspicious_clusters.append(
                                    {
                                        "id": len(suspicious_clusters) + 1,
                                        "members": [int(v) for v in comp],
                                        "isolated": isolated_global_index,
                                        "size": len(comp),
                                        "aggressive_count": 0,
                                        "vulnerable_count": 0,
                                        "aggressive_present": False,
                                        "vulnerable_present": False,
                                    }
                                )
                                cluster_index = len(suspicious_clusters) - 1
                                for member in comp:
                                    cluster_membership[int(member)] = cluster_index
                                    if person_states[int(member)] == "normal":
                                        person_states[int(member)] = "suspicious"
                except Exception as cluster_err:
                    print(f"[ERROR] Clustering logic failed: {cluster_err}")

                # Cluster score from suspicious clusters
                try:
                    if len(suspicious_clusters) > 0:
                        max_cluster_size = max(c["size"] for c in suspicious_clusters)
                        cluster_score = 60 if max_cluster_size >= 5 else 40
                    else:
                        cluster_score = 0
                except Exception as score_err:
                    print(f"[ERROR] Cluster score calculation failed: {score_err}")
                    cluster_score = 0

                # --------------------------------------------
                # 3c) Run pose only when suspicious cluster exists
                # --------------------------------------------
                if len(suspicious_clusters) > 0 and pose_model is not None and person_count > 0:
                    try:
                        pose_results = pose_model(frame, imgsz=640, verbose=False)
                        if (
                            len(pose_results) > 0
                            and pose_results[0].boxes is not None
                            and pose_results[0].keypoints is not None
                            and len(pose_results[0].boxes) > 0
                        ):
                            pose_boxes_xyxy = pose_results[0].boxes.xyxy.cpu().numpy()
                            pose_keypoints_xy = pose_results[0].keypoints.xy.cpu().numpy()

                            if pose_results[0].keypoints.conf is not None:
                                pose_keypoints_conf = pose_results[0].keypoints.conf.cpu().numpy()
                            else:
                                pose_keypoints_conf = np.ones(
                                    (pose_keypoints_xy.shape[0], pose_keypoints_xy.shape[1]),
                                    dtype=np.float32,
                                )

                            detection_centers_np = np.array(person_centers, dtype=np.float32)

                            for p_idx in range(min(len(pose_boxes_xyxy), len(pose_keypoints_xy))):
                                px1, py1, px2, py2 = pose_boxes_xyxy[p_idx]
                                pose_center_x = (px1 + px2) / 2.0
                                pose_center_y = (py1 + py2) / 2.0

                                center_deltas = detection_centers_np - np.array([pose_center_x, pose_center_y], dtype=np.float32)
                                center_dists = np.sqrt(np.sum(center_deltas * center_deltas, axis=1))
                                matched_person_idx = int(np.argmin(center_dists))
                                if float(center_dists[matched_person_idx]) > 120.0:
                                    continue

                                matched_cluster_idx = cluster_membership[matched_person_idx]
                                if matched_cluster_idx < 0:
                                    continue

                                kpts = pose_keypoints_xy[p_idx]
                                kconf = pose_keypoints_conf[p_idx]
                                valid = kconf > 0.35

                                # Required keypoints
                                nose = kpts[0] if valid[0] else None
                                left_shoulder = kpts[5] if valid[5] else None
                                right_shoulder = kpts[6] if valid[6] else None
                                left_wrist = kpts[9] if valid[9] else None
                                right_wrist = kpts[10] if valid[10] else None
                                left_hip = kpts[11] if valid[11] else None
                                right_hip = kpts[12] if valid[12] else None

                                # Build torso and hip references
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

                                torso_center = None
                                if len(torso_points) > 0:
                                    torso_center = np.mean(np.array(torso_points, dtype=np.float32), axis=0)

                                hip_center = None
                                if len(hip_points) > 0:
                                    hip_center = np.mean(np.array(hip_points, dtype=np.float32), axis=0)

                                # Aggressive posture indicators
                                aggressive_flags = []

                                # Arms raised above shoulders by > 30 px
                                arms_raised = False
                                if left_wrist is not None and left_shoulder is not None:
                                    if float(left_wrist[1]) < float(left_shoulder[1]) - 30.0:
                                        arms_raised = True
                                if right_wrist is not None and right_shoulder is not None:
                                    if float(right_wrist[1]) < float(right_shoulder[1]) - 30.0:
                                        arms_raised = True
                                aggressive_flags.append(arms_raised)

                                # Leaning forward aggressively: nose significantly ahead of hips
                                leaning_forward = False
                                if nose is not None and hip_center is not None:
                                    if abs(float(nose[0]) - float(hip_center[0])) > 35.0:
                                        leaning_forward = True
                                aggressive_flags.append(leaning_forward)

                                # Pointing gesture: one wrist extended while the other near hip
                                pointing_gesture = False
                                if torso_center is not None:
                                    if left_wrist is not None and right_wrist is not None:
                                        left_torso_dist = float(np.linalg.norm(left_wrist - torso_center))
                                        right_torso_dist = float(np.linalg.norm(right_wrist - torso_center))
                                        if hip_center is not None:
                                            left_hip_dist = float(np.linalg.norm(left_wrist - hip_center))
                                            right_hip_dist = float(np.linalg.norm(right_wrist - hip_center))
                                            if left_torso_dist > 90.0 and right_hip_dist < 70.0:
                                                pointing_gesture = True
                                            if right_torso_dist > 90.0 and left_hip_dist < 70.0:
                                                pointing_gesture = True
                                aggressive_flags.append(pointing_gesture)

                                aggressive_indicator_count = int(sum(1 for f in aggressive_flags if f))

                                # Vulnerable posture indicators
                                vulnerable_flags = []

                                # Hunched/cowering: collapsed shoulder-to-hip gap
                                hunched_posture = False
                                shoulder_points = []
                                if left_shoulder is not None:
                                    shoulder_points.append(left_shoulder)
                                if right_shoulder is not None:
                                    shoulder_points.append(right_shoulder)

                                if len(shoulder_points) > 0 and len(hip_points) > 0:
                                    shoulder_center = np.mean(np.array(shoulder_points, dtype=np.float32), axis=0)
                                    hip_center_y = float(np.mean(np.array(hip_points, dtype=np.float32)[:, 1]))
                                    shoulder_center_y = float(shoulder_center[1])
                                    if (hip_center_y - shoulder_center_y) < 35.0:
                                        hunched_posture = True
                                vulnerable_flags.append(hunched_posture)

                                # Arms crossed defensively over torso centerline
                                defensive_cross = False
                                if left_wrist is not None and right_wrist is not None and torso_center is not None:
                                    torso_center_x = float(torso_center[0])
                                    if float(left_wrist[0]) > torso_center_x + 5.0 and float(right_wrist[0]) < torso_center_x - 5.0:
                                        defensive_cross = True
                                vulnerable_flags.append(defensive_cross)

                                vulnerable_indicator_count = int(sum(1 for f in vulnerable_flags if f))

                                # Update per-person state for box color/label
                                if aggressive_indicator_count > 0:
                                    person_states[matched_person_idx] = "aggressive"
                                    person_labels[matched_person_idx] = "Aggressive"
                                elif vulnerable_indicator_count > 0:
                                    person_states[matched_person_idx] = "vulnerable"
                                    person_labels[matched_person_idx] = "Vulnerable"

                                # Update cluster posture counters
                                suspicious_clusters[matched_cluster_idx]["aggressive_count"] += aggressive_indicator_count
                                suspicious_clusters[matched_cluster_idx]["vulnerable_count"] += vulnerable_indicator_count
                                if aggressive_indicator_count > 0:
                                    suspicious_clusters[matched_cluster_idx]["aggressive_present"] = True
                                if vulnerable_indicator_count > 0:
                                    suspicious_clusters[matched_cluster_idx]["vulnerable_present"] = True

                                # Cache keypoints for visualization
                                pose_draw_items.append(
                                    {
                                        "kpts": kpts,
                                        "valid": valid,
                                        "aggressive": aggressive_indicator_count > 0,
                                    }
                                )
                    except Exception as pose_err:
                        print(f"[ERROR] Pose estimation/analysis failed: {pose_err}")

                # --------------------------------------------
                # 3d) Pose score + final threat score + level
                # --------------------------------------------
                try:
                    pose_score = 0
                    for c in suspicious_clusters:
                        pose_score += int(c["aggressive_count"]) * 15
                        pose_score += int(c["vulnerable_count"]) * 10
                        if c["aggressive_present"] and c["vulnerable_present"]:
                            pose_score += 20

                    final_threat_score = int(cluster_score + pose_score)

                    if final_threat_score == 0:
                        threat_level = "NORMAL"
                        threat_icon = "🟢"
                    elif 1 <= final_threat_score <= 49:
                        threat_level = "WARNING"
                        threat_icon = "🟡"
                    elif 50 <= final_threat_score <= 79:
                        threat_level = "ALERT"
                        threat_icon = "🔴"
                    else:
                        threat_level = "CRITICAL"
                        threat_icon = "🚨"
                except Exception as final_score_err:
                    print(f"[ERROR] Final score/level calculation failed: {final_score_err}")
                    final_threat_score = 0
                    threat_level = "NORMAL"
                    threat_icon = "🟢"

                # Snapshot trigger when level changes into ALERT/CRITICAL
                try:
                    if threat_level in ["ALERT", "CRITICAL"] and threat_level != previous_threat_level:
                        save_alert_snapshot = True
                except Exception as level_change_err:
                    print(f"[ERROR] Threat level transition check failed: {level_change_err}")

                previous_threat_level = threat_level

            except Exception as inference_err:
                print(f"[ERROR] Inference block failed: {inference_err}")

        # ----------------------------------------------------
        # 4) Visualization overlays
        # ----------------------------------------------------
        annotated_frame = frame.copy()
        try:
            # Draw suspicious cluster polygons with transparency
            if len(suspicious_clusters) > 0:
                overlay = annotated_frame.copy()
                for c in suspicious_clusters:
                    cluster_pts = np.array([person_centers[idx] for idx in c["members"]], dtype=np.int32)
                    polygon_color = (0, 255, 255)
                    if final_threat_score >= 50:
                        polygon_color = (0, 0, 255)

                    if len(cluster_pts) >= 3:
                        hull = cv2.convexHull(cluster_pts)
                        cv2.fillPoly(overlay, [hull], polygon_color)
                        cv2.polylines(annotated_frame, [hull], True, polygon_color, 2)
                    elif len(cluster_pts) == 2:
                        cv2.line(annotated_frame, tuple(cluster_pts[0]), tuple(cluster_pts[1]), polygon_color, 2)

                    # White dashed circle around isolated person
                    isolated_idx = int(c["isolated"])
                    if 0 <= isolated_idx < len(person_boxes):
                        bx1, by1, bx2, by2 = person_boxes[isolated_idx]
                        icx = int((bx1 + bx2) / 2)
                        icy = int((by1 + by2) / 2)
                        radius = int(max(24, 0.6 * max(bx2 - bx1, by2 - by1)))
                        for ang in range(0, 360, 24):
                            if (ang // 24) % 2 == 0:
                                a1 = math.radians(ang)
                                a2 = math.radians(ang + 12)
                                p1 = (int(icx + radius * math.cos(a1)), int(icy + radius * math.sin(a1)))
                                p2 = (int(icx + radius * math.cos(a2)), int(icy + radius * math.sin(a2)))
                                cv2.line(annotated_frame, p1, p2, (255, 255, 255), 2)

                annotated_frame = cv2.addWeighted(overlay, 0.22, annotated_frame, 0.78, 0)

            # Draw pose skeleton/keypoints
            for item in pose_draw_items:
                kpts = item["kpts"]
                valid = item["valid"]
                kp_color = (0, 0, 255) if item["aggressive"] else (0, 255, 0)

                for edge in COCO_SKELETON:
                    a, b = edge
                    if bool(valid[a]) and bool(valid[b]):
                        pa = (int(kpts[a][0]), int(kpts[a][1]))
                        pb = (int(kpts[b][0]), int(kpts[b][1]))
                        cv2.line(annotated_frame, pa, pb, kp_color, 2)

                for kp_idx in range(kpts.shape[0]):
                    if bool(valid[kp_idx]):
                        px = int(kpts[kp_idx][0])
                        py = int(kpts[kp_idx][1])
                        cv2.circle(annotated_frame, (px, py), 3, kp_color, -1)

            # Draw person boxes and labels
            for i in range(len(person_boxes)):
                x1, y1, x2, y2 = person_boxes[i]
                state = person_states[i] if i < len(person_states) else "normal"
                label = person_labels[i] if i < len(person_labels) else "Normal"

                color = (0, 255, 0)
                if state == "suspicious":
                    color = (0, 255, 255)
                    label = "Normal"
                elif state == "aggressive":
                    color = (0, 0, 255)
                    label = "Aggressive"
                elif state == "vulnerable":
                    color = (255, 0, 0)
                    label = "Vulnerable"

                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
                text_y1 = max(0, y1 - text_size[1] - 10)
                text_y2 = max(0, y1)
                cv2.rectangle(
                    annotated_frame,
                    (x1, text_y1),
                    (x1 + text_size[0] + 8, text_y2),
                    color,
                    -1,
                )
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1 + 4, max(12, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 0),
                    2,
                    cv2.LINE_AA,
                )

            # Top-left status panel
            panel_x1, panel_y1, panel_x2, panel_y2 = 10, 10, 370, 120
            panel_overlay = annotated_frame.copy()
            cv2.rectangle(panel_overlay, (panel_x1, panel_y1), (panel_x2, panel_y2), (0, 0, 0), -1)
            annotated_frame = cv2.addWeighted(panel_overlay, 0.45, annotated_frame, 0.55, 0)
            cv2.rectangle(annotated_frame, (panel_x1, panel_y1), (panel_x2, panel_y2), (255, 255, 255), 1)

            cv2.putText(
                annotated_frame,
                f"Persons Detected: {len(person_boxes)}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                annotated_frame,
                f"Suspicious Clusters: {len(suspicious_clusters)}",
                (20, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                annotated_frame,
                f"Threat Score: {final_threat_score}",
                (20, 85),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                annotated_frame,
                f"Status: {threat_level} {threat_icon}",
                (20, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Top-right timestamp and FPS
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(
                annotated_frame,
                now_str,
                (FRAME_WIDTH - 255, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                annotated_frame,
                f"FPS: {fps_value:.1f}",
                (FRAME_WIDTH - 120, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # ALERT/CRITICAL visual emergency indicators
            if threat_level in ["ALERT", "CRITICAL"]:
                if int(time.time() * 2) % 2 == 0:
                    cv2.rectangle(annotated_frame, (0, 0), (FRAME_WIDTH - 1, FRAME_HEIGHT - 1), (0, 0, 255), 12)

                alert_text = "⚠️ RAGGING ALERT DETECTED"
                alert_size = cv2.getTextSize(alert_text, cv2.FONT_HERSHEY_DUPLEX, 0.9, 2)[0]
                tx = max(10, (FRAME_WIDTH - alert_size[0]) // 2)
                ty = FRAME_HEIGHT // 2
                cv2.rectangle(
                    annotated_frame,
                    (tx - 12, ty - alert_size[1] - 14),
                    (tx + alert_size[0] + 12, ty + 10),
                    (0, 0, 0),
                    -1,
                )
                cv2.putText(
                    annotated_frame,
                    alert_text,
                    (tx, ty),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.9,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

        except Exception as draw_err:
            print(f"[ERROR] Drawing overlays failed: {draw_err}")

        # ----------------------------------------------------
        # 5) Snapshot + backend alert (with cooldown)
        # ----------------------------------------------------
        try:
            if save_alert_snapshot and threat_level in ["ALERT", "CRITICAL"]:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                auto_snapshot_path = os.path.join(snapshot_dir, f"alert_{ts}.jpg")
                ok_save = cv2.imwrite(auto_snapshot_path, annotated_frame)
                if ok_save:
                    print(f"[INFO] Alert snapshot saved: {auto_snapshot_path}")
                else:
                    print("[ERROR] Failed to save alert snapshot.")
                save_alert_snapshot = False
        except Exception as snapshot_err:
            print(f"[ERROR] Automatic snapshot save failed: {snapshot_err}")
            save_alert_snapshot = False

        try:
            if threat_level in ["ALERT", "CRITICAL"]:
                now_time = time.time()
                if now_time - last_alert_send_time >= ALERT_COOLDOWN_SECONDS:
                    ts_send = datetime.now().strftime("%Y%m%d_%H%M%S")
                    send_snapshot_path = os.path.join(snapshot_dir, f"alert_{ts_send}.jpg")
                    send_snapshot_ok = cv2.imwrite(send_snapshot_path, annotated_frame)
                    if send_snapshot_ok:
                        print(f"[INFO] Alert snapshot saved: {send_snapshot_path}")
                    else:
                        print("[ERROR] Failed to save alert snapshot before backend send.")

                    total_aggressive = 0
                    largest_cluster_size = 0
                    for c in suspicious_clusters:
                        total_aggressive += int(c.get("aggressive_count", 0))
                        largest_cluster_size = max(largest_cluster_size, int(c.get("size", 0)))

                    payload = {
                        "alert_type": "ragging",
                        "threat_level": "high",
                        "location": LOCATION_NAME,
                        "person_count": len(person_boxes),
                        "description": (
                            f"Cluster of {largest_cluster_size} persons detected "
                            f"with {total_aggressive} aggressive poses"
                        ),
                    }

                    try:
                        response = requests.post(API_URL, json=payload, timeout=3)
                        if 200 <= response.status_code < 300:
                            alert_sent_recently = True
                            print(f"[INFO] Alert payload sent: {json.dumps(payload)}")
                        else:
                            print(
                                f"[WARN] Backend alert request returned status {response.status_code}: "
                                f"{response.text[:200]}"
                            )
                    except Exception as api_err:
                        print(f"[WARN] Backend connection failed (continuing detection): {api_err}")

                    # Cooldown updates regardless of request success to avoid spam
                    last_alert_send_time = now_time
        except Exception as alert_logic_err:
            print(f"[ERROR] Alert sending block failed: {alert_logic_err}")

        # ----------------------------------------------------
        # 6) Console output every second
        # ----------------------------------------------------
        try:
            now_console = time.time()
            if now_console - console_tick >= 1.0:
                timestamp = datetime.now().strftime("%H:%M:%S")
                level_text = f"{threat_level} {threat_icon}"
                print(
                    f"[{timestamp}] Persons: {len(person_boxes)} | Clusters: {len(suspicious_clusters)} | "
                    f"Threat Score: {final_threat_score} | Level: {level_text}"
                )
                for c in suspicious_clusters:
                    print(
                        f"[{timestamp}] Cluster {c['id']}: {c['size']} persons, "
                        f"{c['aggressive_count']} aggressive, {c['vulnerable_count']} vulnerable"
                    )
                if alert_sent_recently:
                    print(f"[{timestamp}] Alert sent to backend ✅")
                console_tick = now_console
        except Exception as console_err:
            print(f"[ERROR] Console logging failed: {console_err}")

        # ----------------------------------------------------
        # 7) FPS update and display frame
        # ----------------------------------------------------
        try:
            now_fps = time.time()
            elapsed = now_fps - fps_tick
            if elapsed >= 1.0:
                fps_value = fps_counter / elapsed
                fps_counter = 0
                fps_tick = now_fps
        except Exception as fps_err:
            print(f"[ERROR] FPS update failed: {fps_err}")

        try:
            cv2.imshow("Real-Time Ragging Detection (YOLOv8)", annotated_frame)
        except Exception as show_err:
            print(f"[ERROR] Display failed: {show_err}")
            break

        # ----------------------------------------------------
        # 8) Keyboard controls
        # ----------------------------------------------------
        try:
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                print("[INFO] Quit key pressed. Exiting...")
                break
            if key == ord("s"):
                manual_snapshot_request = True

            if manual_snapshot_request:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                manual_path = os.path.join(snapshot_dir, f"alert_{ts}.jpg")
                ok_save = cv2.imwrite(manual_path, annotated_frame)
                if ok_save:
                    print(f"[INFO] Manual snapshot saved: {manual_path}")
                else:
                    print("[ERROR] Manual snapshot save failed.")
                manual_snapshot_request = False
        except Exception as key_err:
            print(f"[ERROR] Keyboard handling failed: {key_err}")

except KeyboardInterrupt:
    print("[INFO] Interrupted by user.")
except Exception as main_err:
    print(f"[FATAL] Unexpected error in main loop: {main_err}")
finally:
    try:
        cap.release()
    except Exception:
        pass
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
    print("[INFO] Resources released. Goodbye.")
