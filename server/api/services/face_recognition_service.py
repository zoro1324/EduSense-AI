import json
import logging
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class FaceRecognitionResult:
    success: bool
    matched: bool
    message: str
    student_name: str = ""
    similarity: float = 0.0


class FaceRecognitionService:
    def __init__(self):
        self.script_path = (settings.BASE_DIR.parent / "models" / "attendance" / "recognize_uploaded_face.py").resolve()

    def _write_temp_image(self, image_file=None, image_bytes=None):
        if image_file:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                for chunk in image_file.chunks():
                    tmp_file.write(chunk)
                return tmp_file.name, "multipart"

        if image_bytes:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                tmp_file.write(image_bytes)
                return tmp_file.name, "raw"

        return None, ""

    def _parse_json_output(self, stdout):
        if not stdout:
            return None

        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

        return None

    def recognize_face(self, image_file=None, image_bytes=None, threshold=0.6):
        if not self.script_path.exists():
            return FaceRecognitionResult(
                success=False,
                matched=False,
                message=f"Face recognition script not found at {self.script_path}",
            )

        temp_file_path = None
        try:
            temp_file_path, source = self._write_temp_image(image_file=image_file, image_bytes=image_bytes)
            if not temp_file_path:
                return FaceRecognitionResult(success=False, matched=False, message="No image provided")

            logger.debug("[FACE_RECOGNIZE] Processing image from source: %s", source)

            result = subprocess.run(
                [sys.executable, str(self.script_path), temp_file_path, str(threshold)],
                capture_output=True,
                text=True,
                timeout=180,
            )

            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()

            if stdout:
                logger.debug("[FACE_RECOGNIZE] Script stdout: %s", stdout)
            if stderr:
                logger.warning("[FACE_RECOGNIZE] Script stderr: %s", stderr)

            payload = self._parse_json_output(stdout)

            if result.returncode != 0 and not payload:
                error_message = stderr or stdout or "Unknown recognition script error"
                return FaceRecognitionResult(success=False, matched=False, message=error_message)

            if not payload:
                return FaceRecognitionResult(success=False, matched=False, message="Invalid recognition script output")

            if not payload.get("success", False):
                return FaceRecognitionResult(
                    success=False,
                    matched=False,
                    message=payload.get("message", "Face recognition failed"),
                )

            if not payload.get("matched", False):
                return FaceRecognitionResult(
                    success=True,
                    matched=False,
                    message=payload.get("message", "No matching student found"),
                    similarity=float(payload.get("similarity", 0.0) or 0.0),
                )

            student_name = str(payload.get("student_name", "")).strip()
            if not student_name:
                return FaceRecognitionResult(success=False, matched=False, message="Recognition did not return student name")

            return FaceRecognitionResult(
                success=True,
                matched=True,
                message="Face recognized successfully",
                student_name=student_name,
                similarity=float(payload.get("similarity", 0.0) or 0.0),
            )

        except subprocess.TimeoutExpired:
            return FaceRecognitionResult(success=False, matched=False, message="Face recognition timed out")
        except Exception as exc:
            logger.exception("[FACE_RECOGNIZE] Unexpected service error")
            return FaceRecognitionResult(success=False, matched=False, message=f"Face recognition failed: {exc}")
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug("[FACE_RECOGNIZE] Removed temporary image: %s", temp_file_path)
