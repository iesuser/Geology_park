from flask import Blueprint, abort, render_template

from app.models import Artifact

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
  artifacts = (
    Artifact.query.filter_by(is_active=True)
    .order_by(Artifact.id.asc())
    .all()
  )
  return render_template("main/index.html", artifacts=artifacts)


@main_bp.route("/<int:artifact_id>")
def artifact_detail(artifact_id: int):
  artifact = Artifact.query.get_or_404(artifact_id)
  if not artifact.is_active:
    abort(404)
  return render_template("main/artifact.html", artifact=artifact)
