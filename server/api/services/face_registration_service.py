import logging
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class FaceRegistrationResult:
    success: bool
    message: str
    embedding_path: str = ""
    source: str = ""


class FaceRegistrationService:
    def __init__(self):
        self.script_path = (settings.BASE_DIR.parent / "models" / "attendance" / "register_face.py").resolve()
        self.face_db_path = self.script_path.parent / "face_db.pkl"

    def _resolve_image_source(self, student, image_file):
        if image_file:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                for chunk in image_file.chunks():
                    tmp_file.write(chunk)
                return tmp_file.name, tmp_file.name, "uploaded_image"

        if getattr(student, "photo", None):
            try:
                student_photo_path = Path(student.photo.path)
                if student_photo_path.exists():
                    return str(student_photo_path), None, "student_photo"
            except Exception as exc:
                logger.warning("[FACE_REGISTER] Failed to resolve student photo path: %s", exc)

        return None, None, ""

    def register_face(self, student, image_file=None):
        if not self.script_path.exists():
            return FaceRegistrationResult(
                success=False,
                message=f"Face registration script not found at {self.script_path}",
            )

        image_path = None
        temp_file_path = None
        source = ""

        try:
            image_path, temp_file_path, source = self._resolve_image_source(student, image_file)
            if not image_path:
                return FaceRegistrationResult(
                    success=False,
                    message="No image available for registration. Upload a face image or save a student photo first.",
                )

            logger.debug("[FACE_REGISTER] Using image source '%s' from path: %s", source, image_path)
            result = subprocess.run(
                [sys.executable, str(self.script_path), image_path, student.name],
                capture_output=True,
                text=True,
                timeout=120,
            )

            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()

            if stdout:
                logger.debug("[FACE_REGISTER] Script stdout: %s", stdout)
            if stderr:
                logger.warning("[FACE_REGISTER] Script stderr: %s", stderr)

            if result.returncode != 0:
                error_message = stderr or stdout or "Unknown script error"
                return FaceRegistrationResult(success=False, message=f"Face registration failed: {error_message}")

            if "no face found" in stdout.lower():
                return FaceRegistrationResult(success=False, message="No face was detected in the provided image.")

            embedding_reference = f"{self.face_db_path}:{student.name}"
            return FaceRegistrationResult(
                success=True,
                message="Face registered successfully",
                embedding_path=embedding_reference,
                source=source,
            )

        except subprocess.TimeoutExpired:
            return FaceRegistrationResult(success=False, message="Face registration timed out")
        except Exception as exc:
            logger.exception("[FACE_REGISTER] Unexpected service error")
            return FaceRegistrationResult(success=False, message=f"Face registration failed: {exc}")
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug("[FACE_REGISTER] Removed temporary image file: %s", temp_file_path)
