from app.extensions import db
from app.models import Artifact
from app.services.file_service import delete_file, remove_photo
from app.services.qr_service import generate_qr_code


def delete_artifact(artifact: Artifact) -> None:
  """Delete specimen photos, QR code file, and database record."""
  remove_photo(artifact, 1)
  remove_photo(artifact, 2)
  remove_photo(artifact, 3)
  if artifact.qr_code_path:
    delete_file(artifact.qr_code_path)
  db.session.delete(artifact)


def change_artifact_id(artifact: Artifact, new_id: int) -> Artifact:
  """
  Assign a new ID to a specimen and regenerate its QR code.
  Replaces the row so the old ID is freed for reuse.
  """
  if new_id == artifact.id:
    return artifact

  if db.session.get(Artifact, new_id):
    raise ValueError(f"Specimen #{new_id} already exists. Choose a different ID.")

  old_qr = artifact.qr_code_path
  if old_qr:
    delete_file(old_qr)

  replacement = Artifact(
    id=new_id,
    title_en=artifact.title_en,
    title_ka=artifact.title_ka,
    elevation_m=artifact.elevation_m,
    description_en=artifact.description_en,
    description_ka=artifact.description_ka,
    photo1_path=artifact.photo1_path,
    photo2_path=artifact.photo2_path,
    photo3_path=artifact.photo3_path,
    is_active=artifact.is_active,
    created_at=artifact.created_at,
  )

  db.session.delete(artifact)
  db.session.flush()
  db.session.add(replacement)
  db.session.flush()
  replacement.qr_code_path = generate_qr_code(replacement)

  return replacement
