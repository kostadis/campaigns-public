#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-api-python-client>=2.100",
#     "google-auth-oauthlib>=1.0",
# ]
# ///
"""Mirror this repo's markdown into Google Drive as Google Docs, for NotebookLM.

Creates a "campaigns-public" folder at the root of My Drive and mirrors the
repo's directory tree under it. Each .md file becomes a Google Doc (Drive
converts the markdown on import), named after the file without ".md" --
except SKILL.md, which takes its skill directory's name.

Re-runs update existing Docs in place rather than recreating them, so the
file IDs stay stable and NotebookLM sources pointing at them keep working.
Unchanged files are skipped (source md5 is kept in the Doc's appProperties).
Docs whose source file no longer exists are reported; --prune trashes them.

Uses the drive.file scope: the script only sees and touches files it created
itself, never the rest of your Drive. A "campaigns-public" folder you made by
hand is invisible to it and a second one will be created.

Auth: an OAuth Desktop client JSON at ~/.config/gdrive-cli/credentials.json
(Drive API enabled). First run opens a browser for consent; the token is
cached at ~/.config/gdrive-cli/token-campaigns-public.json.

Usage:
    scripts/sync-to-gdrive.py --dry-run
    scripts/sync-to-gdrive.py
    scripts/sync-to-gdrive.py --prune
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

REPO = Path(__file__).resolve().parent.parent
ROOT_FOLDER = "campaigns-public"
# Repo paths that are tooling, not content.
EXCLUDE = {"CLAUDE.md", "scripts"}

CONFIG_DIR = Path.home() / ".config" / "gdrive-cli"
CREDENTIALS_PATH = CONFIG_DIR / "credentials.json"
TOKEN_PATH = CONFIG_DIR / "token-campaigns-public.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

FOLDER_MIME = "application/vnd.google-apps.folder"
DOC_MIME = "application/vnd.google-apps.document"


def drive_service():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not (creds and creds.valid):
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                sys.exit(
                    f"missing {CREDENTIALS_PATH}\n"
                    "create an OAuth Desktop client in a GCP project with the "
                    "Drive API enabled, download the JSON, and save it there."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def q_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def list_children(svc, parent_id: str) -> list[dict]:
    files, token = [], None
    while True:
        resp = svc.files().list(
            q=f"'{parent_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType, appProperties)",
            pageSize=1000,
            pageToken=token,
        ).execute()
        files.extend(resp.get("files", []))
        token = resp.get("nextPageToken")
        if not token:
            return files


class Mirror:
    def __init__(self, svc, dry_run: bool):
        self.svc = svc
        self.dry_run = dry_run
        self.children: dict[str, list[dict]] = {}
        self.counts = {"created": 0, "updated": 0, "unchanged": 0}

    def kids(self, parent_id: str) -> list[dict]:
        if parent_id not in self.children:
            self.children[parent_id] = (
                [] if parent_id.startswith("dry-run:") else list_children(self.svc, parent_id)
            )
        return self.children[parent_id]

    def root(self) -> str:
        resp = self.svc.files().list(
            q=f"name = '{ROOT_FOLDER}' and mimeType = '{FOLDER_MIME}' "
              "and 'root' in parents and trashed = false",
            fields="files(id)",
        ).execute()
        found = resp.get("files", [])
        if found:
            return found[0]["id"]
        return self.create_folder(ROOT_FOLDER, "root", ROOT_FOLDER)

    def create_folder(self, name: str, parent_id: str, label: str) -> str:
        print(f"  mkdir   {label}/")
        if self.dry_run:
            fid = f"dry-run:{label}"
        else:
            fid = self.svc.files().create(
                body={"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]},
                fields="id",
            ).execute()["id"]
        self.kids(parent_id).append({"id": fid, "name": name, "mimeType": FOLDER_MIME})
        return fid

    def folder(self, rel_dir: Path, root_id: str) -> str:
        fid = root_id
        for i, part in enumerate(rel_dir.parts):
            match = next(
                (f for f in self.kids(fid) if f["name"] == part and f["mimeType"] == FOLDER_MIME),
                None,
            )
            label = "/".join((ROOT_FOLDER, *rel_dir.parts[: i + 1]))
            fid = match["id"] if match else self.create_folder(part, fid, label)
        return fid

    def doc(self, path: Path, parent_id: str) -> str | None:
        rel = path.relative_to(REPO).as_posix()
        data = path.read_bytes()
        md5 = hashlib.md5(data).hexdigest()
        # NotebookLM lists sources by title alone; twelve Docs called "SKILL"
        # would be indistinguishable, so skills take their directory's name.
        name = path.parent.name if path.name == "SKILL.md" else path.stem
        existing = next(
            (f for f in self.kids(parent_id) if f["name"] == name and f["mimeType"] == DOC_MIME),
            None,
        )
        if existing and (existing.get("appProperties") or {}).get("source_md5") == md5:
            self.counts["unchanged"] += 1
            return existing["id"]

        props = {"source_md5": md5, "source_path": rel}
        media = MediaInMemoryUpload(data, mimetype="text/markdown", resumable=False)
        if existing:
            print(f"  update  {rel}")
            self.counts["updated"] += 1
            if not self.dry_run:
                self.svc.files().update(
                    fileId=existing["id"], body={"appProperties": props}, media_body=media,
                ).execute()
            return existing["id"]

        print(f"  create  {rel}")
        self.counts["created"] += 1
        if self.dry_run:
            return None
        fid = self.svc.files().create(
            body={"name": name, "mimeType": DOC_MIME, "parents": [parent_id],
                  "appProperties": props},
            media_body=media,
            fields="id",
        ).execute()["id"]
        self.kids(parent_id).append({"id": fid, "name": name, "mimeType": DOC_MIME})
        return fid

    def stale(self, root_id: str, wanted: set[str]) -> list[tuple[str, str]]:
        """Docs under root_id (recursively) that no source file maps to."""
        out, stack = [], [(root_id, ROOT_FOLDER)]
        while stack:
            fid, label = stack.pop()
            for f in self.kids(fid):
                if f["mimeType"] == FOLDER_MIME:
                    stack.append((f["id"], f"{label}/{f['name']}"))
                elif f["id"] not in wanted:
                    out.append((f["id"], f"{label}/{f['name']}"))
        return sorted(out, key=lambda t: t[1])


def sources() -> list[Path]:
    return sorted(
        p for p in REPO.rglob("*.md")
        if not any(part.startswith(".") for part in p.relative_to(REPO).parts)
        and p.relative_to(REPO).parts[0] not in EXCLUDE
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="report changes without writing")
    ap.add_argument("--prune", action="store_true",
                    help="trash Docs whose source file no longer exists")
    args = ap.parse_args()
    # Uploads take seconds each; show progress even when piped or redirected.
    sys.stdout.reconfigure(line_buffering=True)

    m = Mirror(drive_service(), args.dry_run)
    root_id = m.root()
    wanted: set[str] = set()
    for path in sources():
        parent = m.folder(path.parent.relative_to(REPO), root_id)
        fid = m.doc(path, parent)
        if fid:
            wanted.add(fid)

    stale = [] if args.dry_run and root_id.startswith("dry-run:") else m.stale(root_id, wanted)
    for fid, label in stale:
        if args.prune:
            print(f"  trash   {label}")
            if not args.dry_run:
                m.svc.files().update(fileId=fid, body={"trashed": True}).execute()
        else:
            print(f"  stale   {label}  (no source file; --prune to trash)")

    c = m.counts
    print(f"\n{'[dry run] ' if args.dry_run else ''}"
          f"{c['created']} created, {c['updated']} updated, {c['unchanged']} unchanged, "
          f"{len(stale)} stale{' (trashed)' if args.prune and stale else ''}")


if __name__ == "__main__":
    main()
