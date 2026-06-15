import uuid
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Artifact


def allowed_file(filename: str) -> bool:
  return (
    "." in filename
    and filename.rsplit(".", 1)[1].lower()
    in current_app.config["ALLOWED_EXTENSIONS"]
  )


def save_upload(file: FileStorage, subfolder: str = "photos") -> str | None:
  """Save an uploaded file and return the relative static path."""
  if not file or not file.filename:
    return None
  if not allowed_file(file.filename):
    raise ValueError("File type not allowed. Use PNG, JPG, JPEG, WEBP, or GIF.")

  ext = file.filename.rsplit(".", 1)[1].lower()
  unique_name = f"{uuid.uuid4().hex}.{ext}"
  upload_dir = current_app.config["UPLOAD_FOLDER"] / subfolder
  upload_dir.mkdir(parents=True, exist_ok=True)
  file_path = upload_dir / unique_name
  file.save(file_path)

  return f"uploads/{subfolder}/{unique_name}"


def delete_file(relative_path: str | None) -> None:
  """Delete a file from the static uploads folder."""
  if not relative_path:
    return
  full_path = Path(current_app.root_path) / "static" / relative_path
  if full_path.is_file():
    full_path.unlink()


def remove_photo(artifact: Artifact, slot: int) -> None:
  """Remove a photo from an artifact and delete the file from disk."""
  field = f"photo{slot}_path"
  current_path = getattr(artifact, field)
  if current_path:
    delete_file(current_path)
    setattr(artifact, field, None)


def handle_photo_update(
  artifact: Artifact,
  file: FileStorage | None,
  slot: int,
  remove_flag: bool,
) -> None:
  """Update a photo slot: upload new, remove existing, or leave unchanged."""
  field = f"photo{slot}_path"

  if remove_flag:
    remove_photo(artifact, slot)
    return

  if file and file.filename:
    old_path = getattr(artifact, field)
    new_path = save_upload(file)
    setattr(artifact, field, new_path)
    if old_path:
      delete_file(old_path)
