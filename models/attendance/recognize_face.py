import os
import cv2
import pickle
import numpy as np
from mtcnn import MTCNN
from deepface import DeepFace

MODEL_NAME = "SFace"
WEIGHTS_FILE = "face_recognition_sface_2021dec.onnx"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "face_db.pkl")

print("Starting real-time face recognition...")

try:
    # Section 1: Load registered embeddings from local pickle file
    print("Step 1: Loading local face database...")
    db_path = DB_PATH
    weights_path = os.path.join(os.path.expanduser("~"), ".deepface", "weights", WEIGHTS_FILE)

    # Section 1B: Pre-check model weights cache file
    print(f"Step 1B: Checking {MODEL_NAME} weights cache...")
    try:
        if os.path.exists(weights_path):
            weights_size = os.path.getsize(weights_path)
            if weights_size < 1024 * 1024:
                print(f"Warning: {MODEL_NAME} weights file looks corrupted, deleting cached file")
                os.remove(weights_path)
    except Exception as weights_error:
        print(f"Warning: Could not validate {MODEL_NAME} weights cache: {weights_error}")

    if not os.path.exists(db_path):
        print("No faces registered yet")
        raise SystemExit(0)

    try:
        with open(db_path, "rb") as f:
            face_db = pickle.load(f)
    except Exception as load_error:
        print(f"Error loading face_db.pkl: {load_error}")
        raise SystemExit(1)

    if not isinstance(face_db, dict) or len(face_db) == 0:
        print("No faces registered yet")
        raise SystemExit(0)

    normalized_db = {}
    for person_name, emb in face_db.items():
        try:
            emb_np = np.array(emb, dtype=np.float32)
            emb_norm = np.linalg.norm(emb_np)
            if emb_norm == 0:
                print(f"Warning: Skipping invalid embedding for {person_name}")
                continue
            normalized_db[person_name] = emb_np / emb_norm
        except Exception as norm_error:
            print(f"Warning: Failed to normalize embedding for {person_name}: {norm_error}")

    if len(normalized_db) == 0:
        print("No valid registered faces found in face_db.pkl")
        raise SystemExit(0)

    # Section 2: Initialize detector and open webcam
    print("Step 2: Initializing MTCNN detector and webcam...")
    detector = MTCNN()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam (index 0)")
        raise SystemExit(1)

    print("Webcam started. Press Q to quit.")

    frame_count = 0
    latest_results = []
    weights_recovery_attempted = False

    # Section 3: Read webcam frames continuously
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Warning: Failed to read frame from webcam")
            break

        frame_count += 1

        # Section 4: Process every 10th frame for detection + recognition
        if frame_count % 10 == 0:
            print("Processing frame for detection and recognition...")
            latest_results = []

            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                detected_faces = detector.detect_faces(rgb_frame)
                if detected_faces is None:
                    detected_faces = []
            except Exception as detect_error:
                print(f"Error during face detection: {detect_error}")
                detected_faces = []

            # Section 5: Generate face embedding and compare with database
            for face in detected_faces:
                try:
                    x, y, w, h = face["box"]
                    x = max(0, x)
                    y = max(0, y)
                    w = max(1, w)
                    h = max(1, h)
                    x2 = min(frame.shape[1], x + w)
                    y2 = min(frame.shape[0], y + h)

                    face_crop = frame[y:y2, x:x2]
                    if face_crop.size == 0:
                        print("Warning: Skipping empty face crop")
                        continue

                    embedding_result = None
                    embedding_success = False
                    embedding_attempt = 0
                    while not embedding_success and embedding_attempt < 2:
                        embedding_attempt += 1
                        try:
                            embedding_result = DeepFace.represent(
                                img_path=face_crop,
                                model_name=MODEL_NAME,
                                enforce_detection=False,
                            )
                            embedding_success = True
                        except Exception as embed_error:
                            embed_error_text = str(embed_error)
                            if WEIGHTS_FILE in embed_error_text and not weights_recovery_attempted:
                                weights_recovery_attempted = True
                                print(f"Warning: {MODEL_NAME} weight load failed, deleting cache and retrying once")
                                try:
                                    if os.path.exists(weights_path):
                                        os.remove(weights_path)
                                except Exception as delete_error:
                                    print(f"Warning: Could not delete {MODEL_NAME} cache file: {delete_error}")
                                continue
                            print(f"Warning: {MODEL_NAME} embedding failed: {embed_error}")
                            break

                    if not embedding_success or embedding_result is None:
                        continue

                    if (
                        isinstance(embedding_result, list)
                        and len(embedding_result) > 0
                        and isinstance(embedding_result[0], dict)
                        and "embedding" in embedding_result[0]
                    ):
                        query_emb = np.array(embedding_result[0]["embedding"], dtype=np.float32)
                    elif isinstance(embedding_result, dict):
                        embedding_values = embedding_result.get("embedding")
                        if embedding_values is None:
                            print("Warning: Could not parse query embedding")
                            continue
                        query_emb = np.array(embedding_values, dtype=np.float32)
                    else:
                        print("Warning: Could not parse query embedding")
                        continue

                    query_norm = np.linalg.norm(query_emb)
                    if query_norm == 0:
                        print("Warning: Query embedding has zero norm")
                        continue
                    query_emb = query_emb / query_norm

                    best_name = "Unknown"
                    best_similarity = -1.0

                    for person_name, db_emb in normalized_db.items():
                        if db_emb.shape != query_emb.shape:
                            continue
                        similarity = float(np.dot(query_emb, db_emb))
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_name = person_name

                    if best_similarity > 0.6:
                        label = best_name
                        color = (0, 255, 0)
                    else:
                        label = "Unknown"
                        color = (0, 0, 255)

                    latest_results.append({
                        "box": (x, y, x2, y2),
                        "label": label,
                        "color": color,
                    })

                except Exception as face_error:
                    print(f"Error processing a detected face: {face_error}")

        # Section 6: Draw bounding boxes and labels on frame
        for result in latest_results:
            try:
                x1, y1, x2, y2 = result["box"]
                label = result["label"]
                color = result["color"]

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(
                    frame,
                    label,
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                )
            except Exception as draw_error:
                print(f"Error drawing annotation: {draw_error}")

        # Section 7: Show output frame and quit on Q
        cv2.imshow("Face Recognition Attendance", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == ord("Q"):
            print("Quit signal received. Exiting...")
            break

    # Section 8: Release resources
    cap.release()
    cv2.destroyAllWindows()

except SystemExit:
    pass
except Exception as e:
    print(f"Unexpected error in recognition: {e}")
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
