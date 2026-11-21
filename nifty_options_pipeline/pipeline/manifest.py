"""Append-only CSV manifest of every (kind, date) the downloader has checked.

A row per attempt; the latest row per (kind, date) wins. Appending one short line per
request means a crash loses at most the request in flight, which makes re-runs resumable.
"""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

FIELDS = ["kind", "date", "status", "path", "bytes", "checked_at"]


@dataclass
class Entry:
    kind: str
    date: dt.date
    status: str          # "ok" | "404" | "error"
    path: str            # relative path of the cached file ("" for 404/error)
    bytes: int
    checked_at: str


class Manifest:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.entries: dict[tuple[str, dt.date], Entry] = {}
        self._load()

    def _load(self) -> None:
        if not self.csv_path.exists():
            return
        with self.csv_path.open(newline="") as f:
            for row in csv.DictReader(f):
                try:
                    d = dt.date.fromisoformat(row["date"])
                except (KeyError, ValueError):
                    continue  # partial line from an interrupted write
                self.entries[(row["kind"], d)] = Entry(
                    row["kind"], d, row["status"], row.get("path", ""),
                    int(row["bytes"] or 0), row.get("checked_at", ""))

    def get(self, kind: str, d: dt.date) -> Entry | None:
        return self.entries.get((kind, d))

    def record(self, kind: str, d: dt.date, status: str, path: str = "", nbytes: int = 0) -> Entry:
        e = Entry(kind, d, status, path, nbytes, dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
        self.entries[(kind, d)] = e
        new = not self.csv_path.exists()
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(FIELDS)
            w.writerow([e.kind, e.date.isoformat(), e.status, e.path, e.bytes, e.checked_at])
            f.flush()
        return e

    def ok_entries(self, kind: str) -> list[Entry]:
        return sorted((e for (k, _), e in self.entries.items() if k == kind and e.status == "ok"),
                      key=lambda e: e.date)

    def entries_for(self, kind: str) -> list[Entry]:
        return sorted((e for (k, _), e in self.entries.items() if k == kind), key=lambda e: e.date)
