from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

from app.admin import ArtifactForm
from app.extensions import db
from app.models import Artifact
from app.services import (
  change_artifact_id,
  delete_artifact,
  generate_qr_code,
  handle_photo_update,
  regenerate_all_qr_codes,
  remove_photo,
)

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def dashboard():
  artifacts = Artifact.query.order_by(Artifact.id.asc()).all()
  return render_template("admin/dashboard.html", artifacts=artifacts)


@admin_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
  form = ArtifactForm()
  if form.validate_on_submit():
    requested_id = form.specimen_id.data

    try:
      if requested_id and db.session.get(Artifact, requested_id):
        raise ValueError(f"Specimen #{requested_id} already exists.")

      artifact = Artifact(
        title_en=form.title_en.data or None,
        title_ka=form.title_ka.data or None,
        elevation_m=form.elevation_m.data,
        description_en=form.description_en.data or None,
        description_ka=form.description_ka.data or None,
        is_active=form.is_active.data,
      )
      if requested_id:
        artifact.id = requested_id
      db.session.add(artifact)
      db.session.flush()

      artifact.qr_code_path = generate_qr_code(artifact)
      db.session.commit()
      flash(f"Specimen #{artifact.id} created. You can now upload photos.", "success")
      return redirect(url_for("admin.edit", artifact_id=artifact.id))
    except ValueError as exc:
      db.session.rollback()
      flash(str(exc), "danger")

  return render_template("admin/form.html", form=form, artifact=None)


@admin_bp.route("/edit/<int:artifact_id>", methods=["GET", "POST"])
@login_required
def edit(artifact_id: int):
  artifact = Artifact.query.get_or_404(artifact_id)
  form = ArtifactForm(obj=artifact)

  if request.method == "GET":
    form.specimen_id.data = artifact.id

  if form.validate_on_submit():
    try:
      requested_id = form.specimen_id.data
      if not requested_id:
        raise ValueError("Specimen ID is required.")

      if requested_id != artifact.id:
        artifact = change_artifact_id(artifact, requested_id)

      artifact.title_en = form.title_en.data or None
      artifact.title_ka = form.title_ka.data or None
      artifact.elevation_m = form.elevation_m.data
      artifact.description_en = form.description_en.data or None
      artifact.description_ka = form.description_ka.data or None
      artifact.is_active = form.is_active.data

      db.session.commit()
      flash(f"Specimen #{artifact.id} updated.", "success")
      return redirect(url_for("admin.edit", artifact_id=artifact.id))
    except ValueError as exc:
      db.session.rollback()
      flash(str(exc), "danger")

  return render_template("admin/form.html", form=form, artifact=artifact)


@admin_bp.route("/edit/<int:artifact_id>/photos/<int:slot>", methods=["POST"])
@login_required
def upload_artifact_photo(artifact_id: int, slot: int):
  if slot not in (1, 2, 3):
    return jsonify({"ok": False, "error": "Invalid photo slot."}), 400

  artifact = Artifact.query.get_or_404(artifact_id)
  file = request.files.get("photo")
  if not file or not file.filename:
    return jsonify({"ok": False, "error": "No file selected."}), 400

  try:
    handle_photo_update(artifact, file, slot, False)
    db.session.commit()
    photo_path = getattr(artifact, f"photo{slot}_path")
    return jsonify({
      "ok": True,
      "photo_url": url_for("static", filename=photo_path),
    })
  except ValueError as exc:
    db.session.rollback()
    return jsonify({"ok": False, "error": str(exc)}), 400
  except Exception:
    db.session.rollback()
    return jsonify({"ok": False, "error": "Upload failed."}), 500


@admin_bp.route("/edit/<int:artifact_id>/photos/<int:slot>/remove", methods=["POST"])
@login_required
def remove_artifact_photo(artifact_id: int, slot: int):
  if slot not in (1, 2, 3):
    return jsonify({"ok": False, "error": "Invalid photo slot."}), 400

  artifact = Artifact.query.get_or_404(artifact_id)

  try:
    remove_photo(artifact, slot)
    db.session.commit()
    return jsonify({"ok": True})
  except Exception:
    db.session.rollback()
    return jsonify({"ok": False, "error": "Could not remove photo."}), 500


@admin_bp.route("/delete/<int:artifact_id>", methods=["POST"])
@login_required
def delete(artifact_id: int):
  artifact = Artifact.query.get_or_404(artifact_id)
  deleted_id = artifact.id

  try:
    delete_artifact(artifact)
    db.session.commit()
    flash(f"Specimen #{deleted_id} deleted (photos and QR removed).", "success")
  except Exception:
    db.session.rollback()
  return redirect(url_for("admin.dashboard"))


@admin_bp.route("/regenerate-qr-codes", methods=["POST"])
@login_required
def regenerate_qr_codes():
  try:
    count = regenerate_all_qr_codes()
    db.session.commit()
    flash(f"Regenerated {count} QR code{'s' if count != 1 else ''}.", "success")
  except Exception:
    db.session.rollback()
    flash("Could not regenerate QR codes.", "danger")

  return redirect(url_for("admin.dashboard"))
