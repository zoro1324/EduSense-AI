import sys
import os
import cv2
import pickle
import numpy as np
import albumentations as A
from mtcnn import MTCNN
from deepface import DeepFace

MODEL_NAME = "SFace"
WEIGHTS_FILE = "face_recognition_sface_2021dec.onnx"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "face_db.pkl")

print("Starting face registration...")

try:
    # Section 1: Read command line inputs
    print("Step 0: Reading command line arguments...")
    if len(sys.argv) < 3:
        print("Usage: python register_face.py \"image_path\" \"name\"")
        sys.exit(1)
    image_path = sys.argv[1]
    name = sys.argv[2]
    weights_path = os.path.join(os.path.expanduser("~"), ".deepface", "weights", WEIGHTS_FILE)

    # Section 1B: Pre-check model weights cache file
    print(f"Step 0B: Checking {MODEL_NAME} weights cache...")
    try:
        if os.path.exists(weights_path):
            weights_size = os.path.getsize(weights_path)
            if weights_size < 1024 * 1024:
                print(f"Warning: {MODEL_NAME} weights file looks corrupted, deleting cached file")
                os.remove(weights_path)
    except Exception as weights_error:
        print(f"Warning: Could not validate {MODEL_NAME} weights cache: {weights_error}")

    # Section 2: Load image with OpenCV
    print("Step 1: Loading image with OpenCV...")
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load the input image")
        sys.exit(1)

    # Section 3: Detect and crop face using MTCNN
    print("Step 2: Detecting and cropping face using MTCNN...")
    detector = MTCNN()
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(rgb_image)
    if not faces:
        print("No face found")
        sys.exit(0)

    largest_face = max(faces, key=lambda f: f["box"][2] * f["box"][3])
    x, y, w, h = largest_face["box"]
    x = max(0, x)
    y = max(0, y)
    w = max(1, w)
    h = max(1, h)
    x2 = min(image.shape[1], x + w)
    y2 = min(image.shape[0], y + h)
    cropped_face = image[y:y2, x:x2]
    if cropped_face.size == 0:
        print("Error: Face crop is empty")
        sys.exit(1)

    # Section 4: Build exact 10 augmentations using albumentations
    print("Step 3: Creating 10 augmented face samples...")
    augmentations = [
        (
            "Grayscale (gray->BGR)",
            A.Compose([
                A.Lambda(
                    image=lambda img, **kwargs: cv2.cvtColor(
                        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
                        cv2.COLOR_GRAY2BGR,
                    )
                )
            ]),
        ),
        (
            "Brightness increase (+40%)",
            A.Compose([
                A.RandomBrightnessContrast(
                    brightness_limit=(0.4, 0.4),
                    contrast_limit=(0.0, 0.0),
                    p=1.0,
                )
            ]),
        ),
        (
            "Brightness decrease (-40%)",
            A.Compose([
                A.RandomBrightnessContrast(
                    brightness_limit=(-0.4, -0.4),
                    contrast_limit=(0.0, 0.0),
                    p=1.0,
                )
            ]),
        ),
        ("Horizontal flip", A.Compose([A.HorizontalFlip(p=1.0)])),
        ("Gaussian blur (3x3)", A.Compose([A.GaussianBlur(blur_limit=(3, 3), p=1.0)])),
        ("Gaussian noise", A.Compose([A.GaussNoise(p=1.0)])),
        (
            "Rotation +15",
            A.Compose([A.Rotate(limit=(15, 15), border_mode=cv2.BORDER_REFLECT_101, p=1.0)]),
        ),
        (
            "Rotation -15",
            A.Compose([A.Rotate(limit=(-15, -15), border_mode=cv2.BORDER_REFLECT_101, p=1.0)]),
        ),
        ("Contrast stretch (CLAHE)", A.Compose([A.CLAHE(clip_limit=2.0, tile_grid_size=(8, 8), p=1.0)])),
        (
            "Histogram equalization",
            A.Compose([
                A.Lambda(
                    image=lambda img, **kwargs: cv2.cvtColor(
                        cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)),
                        cv2.COLOR_GRAY2BGR,
                    )
                )
            ]),
        ),
    ]

    # Section 5: Generate face embeddings for augmented samples
    print(f"Step 4: Generating {MODEL_NAME} embeddings for each augmented image...")
    all_embeddings = []
    weights_recovery_attempted = False
    for aug_name, aug_transform in augmentations:
        embed_created = False
        attempt_count = 0
        while not embed_created and attempt_count < 2:
            attempt_count += 1
            try:
                augmented = aug_transform(image=cropped_face)
                aug_face = augmented["image"]
                if len(aug_face.shape) == 2:
                    aug_face = cv2.cvtColor(aug_face, cv2.COLOR_GRAY2BGR)

                embedding_result = DeepFace.represent(
                    img_path=aug_face,
                    model_name=MODEL_NAME,
                    enforce_detection=False,
                )

                if (
                    isinstance(embedding_result, list)
                    and len(embedding_result) > 0
                    and isinstance(embedding_result[0], dict)
                    and "embedding" in embedding_result[0]
                ):
                    emb = np.array(embedding_result[0]["embedding"], dtype=np.float32)
                elif isinstance(embedding_result, dict):
                    embedding_values = embedding_result.get("embedding")
                    if embedding_values is None:
                        print(f"Error: Invalid embedding format for augmentation {aug_name}")
                        break
                    emb = np.array(embedding_values, dtype=np.float32)
                else:
                    print(f"Error: Invalid embedding format for augmentation {aug_name}")
                    break

                all_embeddings.append(emb)
                print(f"Embedding generated: {aug_name}")
                embed_created = True
            except Exception as aug_error:
                error_text = str(aug_error)
                if WEIGHTS_FILE in error_text and not weights_recovery_attempted:
                    weights_recovery_attempted = True
                    print(f"Warning: {MODEL_NAME} weight load failed, deleting cache and retrying once")
                    try:
                        if os.path.exists(weights_path):
                            os.remove(weights_path)
                    except Exception as delete_error:
                        print(f"Warning: Could not delete {MODEL_NAME} cache file: {delete_error}")
                    continue
                print(f"Error generating embedding for {aug_name}: {aug_error}")
                break

    if len(all_embeddings) == 0:
        print("Error: No embeddings generated")
        sys.exit(1)

    # Section 6: Average embeddings and apply L2 normalization
    print("Step 5: Averaging 10 embeddings and applying L2 normalization...")
    master_embedding = np.mean(np.array(all_embeddings), axis=0)
    master_norm = np.linalg.norm(master_embedding)
    if master_norm == 0:
        print("Error: Master embedding norm is zero")
        sys.exit(1)
    master_embedding = master_embedding / master_norm

    # Section 7: Load existing pickle database (if present)
    print("Step 6: Loading existing face_db.pkl if available...")
    db_path = DB_PATH
    face_db = {}
    try:
        with open(db_path, "rb") as db_file:
            loaded_data = pickle.load(db_file)
            if isinstance(loaded_data, dict):
                face_db = loaded_data
            else:
                print("Warning: Existing face_db.pkl content is not a dictionary, using empty dictionary")
    except FileNotFoundError:
        print("face_db.pkl not found, creating a new one")
    except Exception as load_error:
        print(f"Error loading face_db.pkl, using empty dictionary: {load_error}")

    # Section 8: Save updated local database
    print("Step 7: Saving updated entry to face_db.pkl...")
    face_db[name] = master_embedding
    try:
        with open(db_path, "wb") as db_file:
            pickle.dump(face_db, db_file)
    except Exception as save_error:
        print(f"Error saving face_db.pkl: {save_error}")
        sys.exit(1)

    # Section 9: Final success message
    print(f"Registered: {name} successfully")

except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)
