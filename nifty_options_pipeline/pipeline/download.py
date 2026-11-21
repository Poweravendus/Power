"""Download NSE F&O bhavcopies (both formats) and daily index close files, with caching.

Resumable: every (kind, date) outcome is recorded in a manifest. On re-run, cached 'ok'
files are skipped, and 404s are skipped unless they are recent (NSE sometimes publishes
late) or --recheck-404 is given.
"""
from __future__ import annotations

import datetime as dt
import io
import logging
import zipfile
from pathlib import Path

from . import config
from .manifest import Manifest
from .nse_session import DownloadError, NSEClient

log = logging.getLogger(__name__)

KIND_FO_OLD = "fo_old"
KIND_FO_UDIFF = "fo_udiff"
KIND_FO_MKT = "fo_mkt"      # gap filler, see config.mkt_report_path
KIND_INDEX = "index"

MANIFEST_FO = config.RAW_DIR / "manifest_fo.csv"
MANIFEST_INDEX = config.RAW_DIR / "manifest_index.csv"


def fo_kinds_for(d: dt.date) -> list[str]:
    """Which F&O file format(s) to request for a date.

    Both formats are requested inside the overlap/probe window so the cutover is observed
    from the data on every run and the overlap can be reconciled in the validation report.
    """
    if d < config.UDIFF_BACKFILL_START:
        return [KIND_FO_OLD]
    if d <= config.CUTOVER_PROBE_END:
        return [KIND_FO_OLD, KIND_FO_UDIFF]
    return [KIND_FO_UDIFF]


def url_path_for(kind: str, d: dt.date) -> str:
    if kind == KIND_FO_OLD:
        return config.old_fo_path(d)
    if kind == KIND_FO_UDIFF:
        return config.udiff_fo_path(d)
    if kind == KIND_FO_MKT:
        return config.mkt_report_path(d)
    if kind == KIND_INDEX:
        return config.index_close_path(d)
    raise ValueError(kind)


def local_path_for(kind: str, d: dt.date) -> Path:
    name = Path(url_path_for(kind, d)).name
    if kind == KIND_INDEX:
        return config.RAW_INDEX_DIR / str(d.year) / name
    return config.RAW_FO_DIR / str(d.year) / name


def _content_ok(kind: str, content: bytes) -> str | None:
    """Return None if the payload looks right, else a reason string."""
    if kind == KIND_INDEX:
        head = content[:200].lstrip().lower()
        if not head.startswith(b"index name"):
            return "not an index csv (header missing)"
        return None
    if not zipfile.is_zipfile(io.BytesIO(content)):
        return "not a zip file"
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        names = z.namelist()
        if kind == KIND_FO_MKT:
            if not any(n.lower().startswith("op") and n.lower().endswith(".csv") for n in names):
                return f"market report zip without an op*.csv member: {names}"
            return None
        if len(names) != 1 or not names[0].lower().endswith(".csv"):
            return f"unexpected zip members {names}"
    return None


def daterange(start: dt.date, end: dt.date):
    d = start
    while d <= end:
        yield d
        d += dt.timedelta(days=1)


def should_skip(manifest: Manifest, kind: str, d: dt.date, today: dt.date,
                recheck_404: bool, recheck_window_days: int) -> str | None:
    e = manifest.get(kind, d)
    if e is None:
        return None
    if e.status == "ok":
        p = config.ROOT / e.path
        if p.exists() and p.stat().st_size == e.bytes:
            return "cached"
        return None  # file vanished or changed; re-download
    if e.status == "404":
        if recheck_404:
            return None
        if (today - d).days <= recheck_window_days:
            return None  # recent date, NSE may have published since
        return "404-cached"
    return None  # previous error -> retry


def download_range(what: str, start: dt.date, end: dt.date, delay: float = 1.0,
                   recheck_404: bool = False, recheck_window_days: int = 7) -> dict[str, int]:
    """what: 'fo' | 'indices'. Returns counts by outcome."""
    today = dt.date.today()
    if what == "fo":
        manifest = Manifest(MANIFEST_FO)
        kinds_for = fo_kinds_for
    elif what == "indices":
        manifest = Manifest(MANIFEST_INDEX)
        kinds_for = lambda d: [KIND_INDEX]  # noqa: E731
    else:
        raise ValueError(what)

    client = NSEClient(delay=delay)
    counts = {"ok": 0, "404": 0, "error": 0, "cached": 0, "404-cached": 0}
    for d in daterange(start, end):
        kinds = list(kinds_for(d))
        if what == "fo" and d.weekday() < 5:
            # Gap filler: when every bhavcopy format is a 404 on a weekday, also ask for the
            # market-activity report so a real archive hole can still be filled (no settle there).
            primary = [manifest.get(k, d) for k in kinds]
            if primary and all(e is not None and e.status == "404" for e in primary):
                kinds.append(KIND_FO_MKT)
        for kind in kinds:
            skip = should_skip(manifest, kind, d, today, recheck_404, recheck_window_days)
            if skip:
                counts[skip] += 1
                continue
            path = url_path_for(kind, d)
            status, content = None, None
            for host in config.HOSTS:
                try:
                    status, content = client.get(host + path)
                except DownloadError as e:
                    log.error("%s", e)
                    status = None
                    continue
                if status in (200, 404):
                    break  # a 404 is a definitive answer; only errors fall through to the other host
            if status == 200 and content is not None:
                reason = _content_ok(kind, content)
                if reason:
                    log.error("%s %s: 200 but %s", kind, d, reason)
                    manifest.record(kind, d, "error")
                    counts["error"] += 1
                    continue
                local = local_path_for(kind, d)
                local.parent.mkdir(parents=True, exist_ok=True)
                local.write_bytes(content)
                manifest.record(kind, d, "ok", str(local.relative_to(config.ROOT)), len(content))
                counts["ok"] += 1
                log.info("%s %s ok (%d bytes)", kind, d, len(content))
            elif status == 404:
                manifest.record(kind, d, "404")
                counts["404"] += 1
                log.info("%s %s 404 (%s)", kind, d, "weekend" if d.weekday() >= 5 else "weekday - holiday or not published")
            else:
                manifest.record(kind, d, "error")
                counts["error"] += 1
                log.error("%s %s failed (status=%s)", kind, d, status)
    log.info("download %s %s..%s finished: %s", what, start, end, counts)
    return counts
