from pathlib import Path

from flask import Flask

from app.config import Config
from app.extensions import csrf, db, login_manager


def create_app(config_class: type[Config] = Config) -> Flask:
  app = Flask(__name__)
  app.config.from_object(config_class)

  db.init_app(app)
  login_manager.init_app(app)
  csrf.init_app(app)

  config_class.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
  config_class.QR_FOLDER.mkdir(parents=True, exist_ok=True)
  Path(app.root_path).parent.joinpath("instance").mkdir(parents=True, exist_ok=True)

  from app.admin import admin_bp
  from app.auth import auth_bp
  from app.main import main_bp

  app.register_blueprint(main_bp)
  app.register_blueprint(auth_bp, url_prefix="/auth")
  app.register_blueprint(admin_bp, url_prefix="/admin")

  @app.context_processor
  def inject_site_config():
    return {
      "site_footer_label": app.config["SITE_FOOTER_LABEL"],
      "site_footer_url": app.config["SITE_FOOTER_URL"],
    }

  with app.app_context():
    db.create_all()
    _ensure_schema_updates()

  return app


def _ensure_schema_updates() -> None:
  """Add new columns to existing SQLite databases without Flask-Migrate."""
  from sqlalchemy import inspect, text

  inspector = inspect(db.engine)
  if "artifacts" not in inspector.get_table_names():
    return

  columns = {col["name"] for col in inspector.get_columns("artifacts")}
  if "elevation_m" not in columns:
    with db.engine.begin() as conn:
      conn.execute(text("ALTER TABLE artifacts ADD COLUMN elevation_m INTEGER"))
  if "photo3_path" not in columns:
    with db.engine.begin() as conn:
      conn.execute(text("ALTER TABLE artifacts ADD COLUMN photo3_path VARCHAR(500)"))
