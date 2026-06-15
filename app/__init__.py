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

  with app.app_context():
    db.create_all()

  return app
