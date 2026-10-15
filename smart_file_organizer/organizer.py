from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

RULES: dict[str, set[str]] = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".csv"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Audio": {".mp3", ".wav", ".flac", ".m4a"},
    "Video": {".mp4", ".mov", ".mkv", ".avi"},
}

SAMPLES = {
    "holiday.jpg": "Images",
    "resume.pdf": "Documents",
    "notes.txt": "Documents",
    "demo.py": "Code",
    "pack.zip": "Archives",
    "theme.mp3": "Audio",
    "clip.mp4": "Video",
    "mystery.bin": "Other",
}


@dataclass(frozen=True)
class Move:
    src: Path
    dest: Path
    folder: str

    def as_dict(self) -> dict:
        return {
            "from": self.src.name,
            "to": f"{self.folder}/{self.dest.name}",
            "folder": self.folder,
        }


def package_dir() -> Path:
    return Path(__file__).resolve().parent


def sandbox_root() -> Path:
    return package_dir() / "sandbox"


def _inside(parent: Path, child: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def folder_for(path: Path) -> str:
    ext = path.suffix.lower()
    for name, suffixes in RULES.items():
        if ext in suffixes:
            return name
    return "Other"


def ensure_sandbox(root: Path | None = None) -> Path:
    root = (root or sandbox_root()).resolve()
    inbox = root / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    if not any(inbox.iterdir()):
        for name in SAMPLES:
            (inbox / name).write_text("sample\n", encoding="utf-8")
    return inbox


def plan(inbox: Path) -> list[Move]:
    inbox = inbox.resolve()
    root = inbox.parent
    if inbox.name != "inbox" or not _inside(root, inbox):
        raise ValueError("Organizer only plans an inbox/ folder inside its sandbox.")
    moves: list[Move] = []
    for item in sorted(inbox.iterdir()):
        if not item.is_file():
            continue
        folder = folder_for(item)
        dest = (root / folder / item.name).resolve()
        if not _inside(root, dest):
            continue
        if dest.exists():
            continue
        moves.append(Move(src=item, dest=dest, folder=folder))
    return moves


def apply(moves: list[Move]) -> int:
    count = 0
    for move in moves:
        move.dest.parent.mkdir(parents=True, exist_ok=True)
        if move.dest.exists():
            continue
        shutil.move(str(move.src), str(move.dest))
        count += 1
    return count


def inventory(root: Path) -> dict[str, list[str]]:
    root = root.resolve()
    folders: dict[str, list[str]] = {}
    if not root.exists():
        return folders
    for folder in sorted(path for path in root.iterdir() if path.is_dir() and path.name != "inbox"):
        names = sorted(item.name for item in folder.iterdir() if item.is_file())
        if names:
            folders[folder.name] = names
    return folders


def live_check(root: Path) -> dict:
    """Sort a throwaway copy of the sample inbox and report pass/fail for each file."""
    root = root.resolve()
    if root.exists():
        shutil.rmtree(root)
    inbox = ensure_sandbox(root)
    planned = {move.src.name: move.folder for move in plan(inbox)}
    plan_rows = []
    for name, folder in SAMPLES.items():
        got = planned.get(name)
        plan_rows.append({"file": name, "expect": folder, "got": got, "ok": got == folder})
    moved = apply(plan(inbox))
    apply_rows = []
    for name, folder in SAMPLES.items():
        dest = (root / folder / name).resolve()
        apply_rows.append(
            {
                "file": name,
                "expect": f"{folder}/{name}",
                "ok": dest.is_file() and _inside(root, dest),
            }
        )
    leftover = sorted(path.name for path in inbox.iterdir() if path.is_file())
    ok = all(row["ok"] for row in plan_rows) and all(row["ok"] for row in apply_rows) and not leftover
    return {
        "ok": ok,
        "moved": moved,
        "expected": len(SAMPLES),
        "leftover": leftover,
        "plan": plan_rows,
        "apply": apply_rows,
        "folders": inventory(root),
    }
