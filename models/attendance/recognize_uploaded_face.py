import json
import os
import pickle
import sys

# Reduce TensorFlow console noise for subprocess logs.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import cv2
import numpy as np
from deepface import DeepFace
from mtcnn import MTCNN

MODEL_NAME = "SFace"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "face_db.pkl")


def emit(payload, exit_code=0):
    print(json.dumps(payload))
    raise SystemExit(exit_code)


def normalize_embedding(embedding):
    emb = np.array(embedding, dtype=np.float32)
    norm = np.linalg.norm(emb)
    if norm == 0:
        return None
    return emb / norm


def parse_embedding(result):
    if (
        isinstance(result, list)
        and len(result) > 0
        and isinstance(result[0], dict)
        and "embedding" in result[0]
    ):
        return result[0]["embedding"]

    if isinstance(result, dict):
        return result.get("embedding")

    return None


def rotate_image(image, angle):
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    if angle == -90:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    return image


def extract_largest_face_mtcnn(detector, image):
    if image is None or image.size == 0:
        return None

    if image.shape[0] < 48 or image.shape[1] < 48:
        return None

    try:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        detected_faces = detector.detect_faces(rgb_image) or []
    except Exception:
        return None

    if not detected_faces:
        return None

    largest_face = max(detected_faces, key=lambda face: face["box"][2] * face["box"][3])
    x, y, w, h = largest_face["box"]
    x = max(0, x)
    y = max(0, y)
    w = max(1, w)
    h = max(1, h)
    x2 = min(image.shape[1], x + w)
    y2 = min(image.shape[0], y + h)

    face_crop = image[y:y2, x:x2]
    if face_crop.size == 0:
        return None
    return face_crop


def extract_largest_face_haar(image):
    if image is None or image.size == 0:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        return None

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40, 40),
    )

    if len(faces) == 0:
        return None

    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    x = max(0, x)
    y = max(0, y)
    x2 = min(image.shape[1], x + w)
    y2 = min(image.shape[0], y + h)
    face_crop = image[y:y2, x:x2]
    if face_crop.size == 0:
        return None
    return face_crop


def main():
    if len(sys.argv) < 2:
        emit({"success": False, "message": "Usage: python recognize_uploaded_face.py <image_path> [threshold]"}, 1)

    image_path = sys.argv[1]
    threshold = 0.6
    if len(sys.argv) >= 3:
        try:
            threshold = float(sys.argv[2])
        except ValueError:
            emit({"success": False, "message": "Invalid threshold value"}, 1)

    if not os.path.exists(DB_PATH):
        emit({"success": False, "message": "No face database found. Register student faces first."}, 1)

    try:
        with open(DB_PATH, "rb") as db_file:
            face_db = pickle.load(db_file)
    except Exception as exc:
        emit({"success": False, "message": f"Failed to read face database: {exc}"}, 1)

    if not isinstance(face_db, dict) or not face_db:
        emit({"success": False, "message": "Face database is empty. Register student faces first."}, 1)

    normalized_db = {}
    for person_name, embedding in face_db.items():
        normalized = normalize_embedding(embedding)
        if normalized is not None:
            normalized_db[person_name] = normalized

    if not normalized_db:
        emit({"success": False, "message": "No valid face embeddings found in database."}, 1)

    image = cv2.imread(image_path)
    if image is None:
        emit({"success": False, "message": "Could not load uploaded image"}, 1)

    detector = MTCNN()
    face_crop = None

    # Try multiple orientations because ESP32 camera mounting differs across setups.
    for angle in [0, 90, -90, 180]:
        candidate = rotate_image(image, angle)
        face_crop = extract_largest_face_mtcnn(detector, candidate)
        if face_crop is not None:
            break

    # Fallback detector when MTCNN misses noisy/low-light captures.
    if face_crop is None:
        for angle in [0, 90, -90, 180]:
            candidate = rotate_image(image, angle)
            face_crop = extract_largest_face_haar(candidate)
            if face_crop is not None:
                break

    if face_crop is None:
        emit({"success": True, "matched": False, "message": "No face found in image"})

    try:
        embedding_result = DeepFace.represent(
            img_path=face_crop,
            model_name=MODEL_NAME,
            enforce_detection=False,
        )
    except Exception as exc:
        emit({"success": False, "message": f"Failed to create face embedding: {exc}"}, 1)

    query_values = parse_embedding(embedding_result)
    if query_values is None:
        emit({"success": False, "message": "Could not parse query embedding"}, 1)

    query_embedding = normalize_embedding(query_values)
    if query_embedding is None:
        emit({"success": False, "message": "Query embedding norm is zero"}, 1)

    best_name = ""
    best_similarity = -1.0

    for person_name, db_embedding in normalized_db.items():
        if db_embedding.shape != query_embedding.shape:
            continue

        similarity = float(np.dot(query_embedding, db_embedding))
        if similarity > best_similarity:
            best_similarity = similarity
            best_name = person_name

    if best_name and best_similarity >= threshold:
        emit(
            {
                "success": True,
                "matched": True,
                "student_name": best_name,
                "similarity": best_similarity,
                "threshold": threshold,
            }
        )

    emit(
        {
            "success": True,
            "matched": False,
            "similarity": max(best_similarity, 0.0),
            "threshold": threshold,
            "message": "No matching student found",
        }
    )


if __name__ == "__main__":
    main()
