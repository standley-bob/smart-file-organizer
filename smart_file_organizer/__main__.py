from __future__ import annotations

import argparse

from .organizer import apply, ensure_sandbox, plan, sandbox_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sort a sandbox inbox by file type.")
    parser.add_argument("--apply", action="store_true", help="Move files. Default is dry-run.")
    args = parser.parse_args(argv)
    inbox = ensure_sandbox(sandbox_root())
    moves = plan(inbox)
    if not moves:
        print("Nothing to sort. Inbox is clean.")
        return 0
    for move in moves:
        print(f"{move.src.name} -> {move.folder}/")
    if args.apply:
        n = apply(moves)
        print(f"Moved {n} file(s).")
    else:
        print("Dry-run. Pass --apply to move files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
