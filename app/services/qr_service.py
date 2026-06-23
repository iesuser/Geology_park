from flask import current_app
from qrcode import QRCode
from qrcode.constants import ERROR_CORRECT_M
from qrcode.image.pil import PilImage

from app.models import Artifact
from app.services.file_service import delete_file


def generate_qr_code(artifact: Artifact) -> str:
  """
  Generate a QR code pointing to the artifact's public page.
  Returns the relative static path to the saved QR image.
  """
  base_url = current_app.config["BASE_URL"]
  target_url = f"{base_url}/{artifact.id}"
  fill_color = current_app.config.get("QR_FILL_COLOR", "white")
  back_color = current_app.config.get("QR_BACK_COLOR", "transparent")

  qr = QRCode(
    version=1,
    error_correction=ERROR_CORRECT_M,
    box_size=10,
    border=4,
    image_factory=PilImage,
  )
  qr.add_data(target_url)
  qr.make(fit=True)

  img = qr.make_image(fill_color=fill_color, back_color=back_color)

  qr_dir = current_app.config["QR_FOLDER"]
  qr_dir.mkdir(parents=True, exist_ok=True)
  filename = f"artifact_{artifact.id}.png"
  file_path = qr_dir / filename
  img.save(str(file_path))

  return f"uploads/qrcodes/{filename}"


def regenerate_qr_code(artifact: Artifact) -> str:
  """Replace an artifact QR image with a freshly generated file."""
  if artifact.qr_code_path:
    delete_file(artifact.qr_code_path)
  return generate_qr_code(artifact)


def regenerate_all_qr_codes() -> int:
  """Regenerate QR images for every specimen. Returns the number updated."""
  artifacts = Artifact.query.order_by(Artifact.id.asc()).all()
  for artifact in artifacts:
    artifact.qr_code_path = regenerate_qr_code(artifact)
  return len(artifacts)
