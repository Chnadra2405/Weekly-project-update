from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from PIL import Image

from app.application.contracts import IncomingFile, UploadValidationError
from app.infrastructure.storage import LocalFileStorage


def test_rejects_disguised_image_and_cleans_staging(tmp_path: Path) -> None:
    storage = LocalFileStorage(tmp_path, 1024, 2048, 1000)

    with pytest.raises(UploadValidationError):
        storage.stage(uuid4(), [IncomingFile("payload.png", "image/png", BytesIO(b"MZ executable"))])

    assert list((tmp_path / ".staging").glob("*")) == []


def test_rejects_valid_image_with_mismatched_content_type(tmp_path: Path) -> None:
    image_bytes = BytesIO()
    Image.new("RGB", (2, 2), "white").save(image_bytes, format="PNG")
    image_bytes.seek(0)
    storage = LocalFileStorage(tmp_path, 1024, 2048, 1000)

    with pytest.raises(UploadValidationError, match="content, extension, and media type"):
        storage.stage(uuid4(), [IncomingFile("status.jpg", "image/jpeg", image_bytes)])

    assert list((tmp_path / ".staging").glob("*")) == []