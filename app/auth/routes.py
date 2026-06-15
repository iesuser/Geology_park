from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from app.extensions import login_manager
from app.models import AdminUser

auth_bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id: str):
  if user_id == current_app.config["ADMIN_USERNAME"]:
    return AdminUser(user_id)
  return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if (
      username == current_app.config["ADMIN_USERNAME"]
      and password == current_app.config["ADMIN_PASSWORD"]
    ):
      login_user(AdminUser(username))
      flash("Logged in successfully.", "success")
      next_page = request.args.get("next")
      return redirect(next_page or url_for("admin.dashboard"))

    flash("Invalid username or password.", "danger")

  return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
  logout_user()
  flash("You have been logged out.", "info")
  return redirect(url_for("main.index"))
