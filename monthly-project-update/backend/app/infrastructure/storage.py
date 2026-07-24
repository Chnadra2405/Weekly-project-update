from __future__ import annotations

import hashlib
import shutil
from pathlib import Path, PurePath
from uuid import UUID, uuid4

from PIL import Image, UnidentifiedImageError

from app.application.contracts import IncomingFile, StagedUpload, UploadValidationError
from app.domain import Attachment, AttachmentKind

EMAIL_TYPES = {"message/rfc822", "application/vnd.ms-outlook", "application/octet-stream"}
IMAGE_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
IMAGE_FORMAT_TYPES = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}
OLE_SIGNATURE = bytes.fromhex("D0CF11E0A1B11AE1")


class LocalFileStorage:
    def __init__(self, root: Path, max_file_bytes: int, max_total_bytes: int, max_image_pixels: int) -> None:
        self.root = root.resolve()
        self.max_file_bytes = max_file_bytes
        self.max_total_bytes = max_total_bytes
        self.max_image_pixels = max_image_pixels

    def stage(self, submission_id: UUID, files: list[IncomingFile]) -> list[StagedUpload]:
        staging = self.root / ".staging" / str(submission_id)
        staging.mkdir(parents=True, exist_ok=False)
        results: list[StagedUpload] = []
        total = 0
        try:
            for incoming in files:
                filename = PurePath(incoming.filename.replace("\\", "/")).name[:255]
                extension = Path(filename).suffix.lower()
                kind = AttachmentKind.IMAGE if extension in {".png", ".jpg", ".jpeg", ".webp"} else AttachmentKind.REFERENCE_EMAIL
                destination = staging / f"{kind.value.lower()}{extension}"
                digest = hashlib.sha256()
                size = 0
                with destination.open("xb") as output:
                    while chunk := incoming.stream.read(64 * 1024):
                        size += len(chunk)
                        total += len(chunk)
                        if size > self.max_file_bytes or total > self.max_total_bytes:
                            raise UploadValidationError("Each file must be 10 MiB or smaller.")
                        digest.update(chunk)
                        output.write(chunk)
                media_type = self._inspect(destination, extension, incoming.media_type, kind)
                relative = Path("submissions") / str(submission_id) / destination.name
                attachment = Attachment(uuid4(), kind, filename, relative.as_posix(), media_type, size, digest.hexdigest())
                results.append(StagedUpload(attachment, staging))
            if len({item.attachment.kind for item in results}) != len(results):
                raise UploadValidationError("Only one reference email and one image are allowed.")
            return results
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise

    def _inspect(self, path: Path, extension: str, media_type: str, kind: AttachmentKind) -> str:
        if kind is AttachmentKind.IMAGE:
            expected_type = IMAGE_TYPES.get(media_type)
            if expected_type is None or extension not in {expected_type, ".jpeg" if expected_type == ".jpg" else expected_type}:
                raise UploadValidationError("Image extension and media type do not match.")
            try:
                with Image.open(path) as image:
                    image.verify()
                with Image.open(path) as image:
                    if image.width * image.height > self.max_image_pixels:
                        raise UploadValidationError("Image dimensions are too large.")
                    actual = image.format
            except (UnidentifiedImageError, OSError) as error:
                raise UploadValidationError("Image content is invalid.") from error
            actual_type = IMAGE_FORMAT_TYPES.get(actual or "")
            if actual_type is None:
                raise UploadValidationError("Image format is not supported.")
            if actual_type != media_type:
                raise UploadValidationError("Image content, extension, and media type do not match.")
            return media_type
        if extension not in {".eml", ".msg"} or media_type not in EMAIL_TYPES:
            raise UploadValidationError("Reference email must be an EML or MSG file.")
        header = path.read_bytes()[:8]
        if extension == ".msg" and header != OLE_SIGNATURE:
            raise UploadValidationError("MSG content is invalid.")
        if extension == ".eml":
            from email import policy
            from email.parser import BytesParser

            try:
                parsed = BytesParser(policy=policy.default).parse(path.open("rb"), headersonly=True)
                if not parsed.keys():
                    raise UploadValidationError("EML content has no message headers.")
            except OSError as error:
                raise UploadValidationError("EML content is invalid.") from error
        return "message/rfc822" if extension == ".eml" else "application/vnd.ms-outlook"

    def commit(self, submission_id: UUID, staged: list[StagedUpload]) -> None:
        if not staged:
            (self.root / "submissions" / str(submission_id)).mkdir(parents=True, exist_ok=False)
            shutil.rmtree(self.root / ".staging" / str(submission_id), ignore_errors=True)
            return
        source = staged[0].staging_directory
        target = self.root / "submissions" / str(submission_id)
        target.parent.mkdir(parents=True, exist_ok=True)
        source.replace(target)

    def discard(self, submission_id: UUID) -> None:
        shutil.rmtree(self.root / ".staging" / str(submission_id), ignore_errors=True)

    def absolute_path(self, attachment: Attachment) -> Path:
        candidate = (self.root / attachment.stored_relative_path).resolve()
        if self.root not in candidate.parents:
            raise ValueError("Stored attachment path is outside the managed root.")
        return candidate

    def is_ready(self) -> bool:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            probe = self.root / ".ready"
            probe.write_text("ready", encoding="ascii")
            probe.unlink()
            return True
        except OSError:
            return False