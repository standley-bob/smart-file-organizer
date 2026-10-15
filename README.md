# Smart File Organizer

Python tool that sorts a messy inbox by type: images, documents, code, archives, audio, video, and other.

Default mode is a **dry-run**. Nothing moves until you pass `--apply`.

This folder is written to become its own GitHub repo (`smart-file-organizer`) later. On the portfolio it also runs as a live page at `/apps/organizer`.

## CLI

```powershell
py -3 -m software.smart_file_organizer
py -3 -m software.smart_file_organizer --apply
```

From this folder after it is split out:

```powershell
py -3 -m smart_file_organizer --apply
```

It only touches `sandbox/inbox` in this package, never your real Downloads folder.
