import qrcode
from flask import current_app
from qrcode.image.pure import PyPNGImage

from app.models import Artifact


def generate_qr_code(artifact: Artifact) -> str:
  """
  Generate a QR code pointing to the artifact's public page.
  Returns the relative static path to the saved QR image.
  Uses pypng (pure Python) instead of Pillow — no system libs required.
  """
  base_url = current_app.config["BASE_URL"]
  target_url = f"{base_url}/{artifact.id}"

  qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=4,
    image_factory=PyPNGImage,
  )
  qr.add_data(target_url)
  qr.make(fit=True)

  img = qr.make_image(fill_color="black", back_color="white")

  qr_dir = current_app.config["QR_FOLDER"]
  qr_dir.mkdir(parents=True, exist_ok=True)
  filename = f"artifact_{artifact.id}.png"
  file_path = qr_dir / filename
  img.save(str(file_path))

  return f"uploads/qrcodes/{filename}"
