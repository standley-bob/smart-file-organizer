from pathlib import Path
from tempfile import TemporaryDirectory

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from data.projects import get_project
from data.site import NAME, ROLE
from software.smart_file_organizer.organizer import (
    SAMPLES,
    apply,
    ensure_sandbox,
    inventory,
    live_check,
    plan,
    sandbox_root,
)

bp = Blueprint(
    "organizer",
    __name__,
    url_prefix="/apps/organizer",
    template_folder="templates",
    static_folder="static",
)


@bp.route("/", methods=["GET", "POST"])
def home():
    root = sandbox_root()
    inbox = root / "inbox"
    if not inbox.exists():
        inbox = ensure_sandbox()
    message = None
    check = None
    if request.method == "POST" and request.form.get("action") == "apply":
        moved = apply(plan(inbox))
        message = f"Moved {moved} file(s)." if moved else "Nothing to move."
        inbox = root / "inbox"
    if request.method == "POST" and request.form.get("action") == "live-check":
        with TemporaryDirectory(prefix="sfo-check-") as tmp:
            check = live_check(Path(tmp))
    moves = [m.as_dict() for m in plan(inbox)]
    folders = sorted({p.name for p in root.iterdir() if p.is_dir() and p.name != "inbox"})
    project = get_project("smart-file-organizer")
    return render_template(
        "sfo.html",
        name=NAME,
        role=ROLE,
        project=project,
        moves=moves,
        folders=folders,
        shelf=inventory(root),
        samples=SAMPLES,
        check=check,
        inbox_count=sum(1 for p in inbox.iterdir() if p.is_file()),
        message=message,
    )


@bp.get("/check.json")
def check_json():
    with TemporaryDirectory(prefix="sfo-check-") as tmp:
        return jsonify(live_check(Path(tmp)))


@bp.post("/reset")
def reset():
    import shutil

    root = sandbox_root()
    if root.exists():
        shutil.rmtree(root)
    ensure_sandbox()
    return redirect(url_for("organizer.home"))
