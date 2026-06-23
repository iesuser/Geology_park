from datetime import datetime, timezone

from flask_login import UserMixin

from app.extensions import db


class AdminUser(UserMixin):
  """Simple admin user loaded from environment variables."""

  def __init__(self, user_id: str):
    self.id = user_id


class Artifact(db.Model):
  """A geological specimen / rock displayed in the museum."""

  __tablename__ = "artifacts"

  id = db.Column(db.Integer, primary_key=True)
  title_en = db.Column(db.String(200), nullable=True)
  title_ka = db.Column(db.String(200), nullable=True)
  description_en = db.Column(db.Text, nullable=True)
  description_ka = db.Column(db.Text, nullable=True)
  elevation_m = db.Column(db.Integer, nullable=True)
  photo1_path = db.Column(db.String(500), nullable=True)
  photo2_path = db.Column(db.String(500), nullable=True)
  photo3_path = db.Column(db.String(500), nullable=True)
  qr_code_path = db.Column(db.String(500), nullable=True)
  is_active = db.Column(db.Boolean, default=True, nullable=False)
  created_at = db.Column(
    db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
  )
  updated_at = db.Column(
    db.DateTime,
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
    nullable=False,
  )

  def display_title(self, lang: str = "en") -> str:
    if lang == "ka" and self.title_ka:
      return self.title_ka
    if self.title_en:
      return self.title_en
    if self.title_ka:
      return self.title_ka
    return f"Specimen #{self.id}"

  def has_content(self) -> bool:
    return any(
      [
        self.title_en,
        self.title_ka,
        self.description_en,
        self.description_ka,
        self.photo1_path,
        self.photo2_path,
        self.photo3_path,
      ]
    )

  @property
  def card_image(self) -> str | None:
    return self.photo1_path or self.photo2_path

  def __repr__(self) -> str:
    return f"<Artifact {self.id}: {self.title_en or self.title_ka or 'untitled'}>"
