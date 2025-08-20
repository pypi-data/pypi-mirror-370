#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Literal, Optional, Callable
from urllib.parse import urlencode, quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ----------------------------
# Types & Data Models
# ----------------------------

JobStatus = Literal["success", "failed", "canceled", "skipped", "manual"]
TimeField = Literal["created_at", "started_at", "finished_at"]
JobScope = Literal["both", "main", "mrs"]

FINISHED_STATUSES: set[str] = {"success", "failed", "canceled", "skipped", "manual"}

MR_SOURCES: set[str] = {
    # GitLab emits several variants depending on settings/version
    "merge_request_event",
    "external_pull_request_event",
    "detached_merge_request_event",
    "merge_request",  # seen on some self-hosted versions
    "parent_pipeline",
    "child_pipeline",  # include child/parent if they originate from MR
}

MAIN_BRANCHES: set[str] = {"main", "master"}


@dataclass(frozen=True)
class PipelineSummary:
    id: int
    ref: Optional[str] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class Job:
    pipeline_id: int
    job_id: int
    name: str
    status: JobStatus
    duration_s: float
    created_at: Optional[str]
    started_at: Optional[str]
    finished_at: Optional[str]
    ref: Optional[str]
    stage: Optional[str]
    web_url: Optional[str]


@dataclass(frozen=True)
class Stats:
    count: int
    total_s: float
    min_s: float
    p10_s: float
    p25_s: float
    median_s: float
    p75_s: float
    p90_s: float
    max_s: float
    mean_s: float
    stdev_s: float


@dataclass(frozen=True)
class JobNameStats:
    name: str
    stats: Stats
    success_pct: float
    failed_pct: float
    total_pct: float


@dataclass(frozen=True)
class Window:
    start: str
    end: str
    time_field: TimeField


@dataclass(frozen=True)
class Counts:
    jobs_included: int


@dataclass(frozen=True)
class ResultPayload:
    window: Window
    project: str
    statuses: List[str]
    counts: Counts
    overall: Stats
    per_job_name: List[JobNameStats]


# ----------------------------
# Utilities
# ----------------------------


def parse_iso8601(s: str) -> datetime.datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def to_iso8601(dt: datetime.datetime) -> str:
    return dt.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def percentile(data: List[float], p: float) -> float:
    if not data:
        return float("nan")
    if p <= 0:
        return min(data)
    if p >= 100:
        return max(data)
    xs = sorted(data)
    k = (len(xs) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return xs[int(k)]
    d0 = xs[f] * (c - k)
    d1 = xs[c] * (k - f)
    return d0 + d1


def mean(data: List[float]) -> float:
    return sum(data) / len(data) if data else float("nan")


def stdev(data: List[float]) -> float:
    n = len(data)
    if n < 2:
        return float("nan")
    m = mean(data)
    return math.sqrt(sum((x - m) ** 2 for x in data) / (n - 1))


def fmt_seconds(sec: float) -> str:
    if math.isnan(sec):
        return "nan"
    sec_i = int(round(sec))
    h, r = divmod(sec_i, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def table(rows: List[List[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(str(cell)) for cell in col) for col in zip(*rows)]
    lines: List[str] = []
    for i, row in enumerate(rows):
        line = " ".join(
            str(cell).ljust(widths[j])
            if j == 0
            else ("| " + str(cell).ljust(widths[j]))
            for j, cell in enumerate(row)
        )
        lines.append(line)
        if i == 0:
            lines.append("-+-".join("-" * w for w in widths))
    return "\n".join(lines)


# ----------------------------
# Lightweight HTTP client (stdlib)
# ----------------------------


class HttpClient:
    def __init__(
        self,
        base_url: str,
        headers: Dict[str, str],
        timeout: int = 30,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.headers = dict(headers)
        self.timeout = timeout
        self.max_retries = max_retries

    def _absolute(self, path_or_url: str) -> str:
        if path_or_url.startswith(("http://", "https://")):
            return path_or_url
        return f"{self.base_url}{path_or_url}"

    def get(
        self, path_or_url: str, params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Dict[str, str], bytes]:
        url = self._absolute(path_or_url)
        if params:
            q_items: list[tuple[str, str]] = []
            for k, v in params.items():
                if isinstance(v, list):
                    for item in v:
                        q_items.append((k, str(item)))
                else:
                    q_items.append((k, str(v)))
            qs = urlencode(q_items, doseq=True)
            parts = list(urlsplit(url))
            parts[3] = f"{parts[3]}&{qs}" if parts[3] else qs
            url = urlunsplit(parts)

        req = Request(url, headers=self.headers, method="GET")
        attempt = 0
        while True:
            attempt += 1
            try:
                with urlopen(req, timeout=self.timeout) as resp:
                    code = resp.getcode() or 0
                    raw = resp.read()
                    hdrs = {k: v for k, v in resp.getheaders()}
                    return code, hdrs, raw
            except HTTPError as e:
                if e.code == 429:
                    retry_after = e.headers.get("Retry-After")
                    wait = (
                        int(retry_after) if retry_after and retry_after.isdigit() else 2
                    )
                    time.sleep(wait)
                    continue
                if 500 <= e.code < 600 and attempt < self.max_retries:
                    time.sleep(1.5 * attempt)
                    continue
                raise
            except URLError:
                if attempt < self.max_retries:
                    time.sleep(1.5 * attempt)
                    continue
                raise


# ----------------------------
# GitLab API helpers (using stdlib HTTP)
# ----------------------------


class GitLabClient:
    def __init__(
        self, base_url: str, token: str, timeout: int = 30, max_retries: int = 3
    ):
        self.base_url = base_url.rstrip("/")
        self.http = HttpClient(
            self.base_url,
            headers={
                "PRIVATE-TOKEN": token,
                "Accept": "application/json",
                "User-Agent": "glci-stats",
            },
            timeout=timeout,
            max_retries=max_retries,
        )

    def _paginate(self, path: str, params: Dict[str, Any]) -> Iterable[dict]:
        params = dict(params)
        params.setdefault("per_page", 100)

        next_url: Optional[str] = path
        next_params: Dict[str, Any] = params

        while next_url:
            code, hdrs, raw = self.http.get(next_url, params=next_params)
            if not (200 <= code < 300):
                raise RuntimeError(f"Unexpected status {code} for {next_url}")
            try:
                data = json.loads(raw.decode("utf-8"))
            except Exception as e:
                raise RuntimeError(f"Failed to decode JSON: {e}") from e
            if not isinstance(data, list):
                raise RuntimeError(f"Expected list from {next_url}, got {type(data)}")
            for item in data:
                yield item

            link = hdrs.get("Link", "")
            found_next: Optional[str] = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    lt = part.split(";")[0].strip()
                    if lt.startswith("<") and lt.endswith(">"):
                        found_next = lt[1:-1]
                    break

            if found_next:
                next_url = found_next
                next_params = {}
            else:
                next_url = None

    def list_pipelines(
        self,
        project: str,
        created_after: datetime.datetime,
        created_before: datetime.datetime,
    ) -> List[PipelineSummary]:
        proj = quote(project, safe="")
        params = {
            "created_after": to_iso8601(created_after),
            "created_before": to_iso8601(created_before),
            "updated_after": to_iso8601(created_after),
            "updated_before": to_iso8601(created_before),
            "order_by": "updated_at",
            "sort": "desc",
        }
        out: List[PipelineSummary] = []
        for item in self._paginate(f"/api/v4/projects/{proj}/pipelines", params):
            pid = item.get("id")
            if isinstance(pid, int):
                out.append(
                    PipelineSummary(
                        id=pid, ref=item.get("ref"), source=item.get("source")
                    )
                )
        return out

    def list_pipeline_jobs(self, project: str, pipeline_id: int) -> List[Job]:
        proj = quote(project, safe="")
        jobs: List[Job] = []
        for j in self._paginate(
            f"/api/v4/projects/{proj}/pipelines/{pipeline_id}/jobs",
            params={},
        ):
            status_raw = (j.get("status") or "").lower()
            duration = j.get("duration")
            if duration is None:
                st = j.get("started_at")
                fi = j.get("finished_at")
                if st and fi:
                    try:
                        duration = (
                            parse_iso8601(fi) - parse_iso8601(st)
                        ).total_seconds()
                    except Exception:
                        duration = None
            duration_val = (
                float(duration) if isinstance(duration, (int, float)) else float("nan")
            )

            try:
                jobs.append(
                    Job(
                        pipeline_id=pipeline_id,
                        job_id=int(j.get("id")),
                        name=str(j.get("name") or "unknown"),
                        status=status_raw,  # type: ignore[arg-type]
                        duration_s=duration_val,
                        created_at=j.get("created_at"),
                        started_at=j.get("started_at"),
                        finished_at=j.get("finished_at"),
                        ref=j.get("ref"),
                        stage=j.get("stage"),
                        web_url=j.get("web_url"),
                    )
                )
            except Exception:
                continue
        return jobs


# ----------------------------
# Core logic
# ----------------------------


def _pipeline_matches_scope(p: PipelineSummary, scope: JobScope) -> bool:
    if scope == "both":
        return True
    if scope == "main":
        return (p.ref or "").lower() in MAIN_BRANCHES
    if scope == "mrs":
        src = (p.source or "").lower()
        return src in MR_SOURCES
    return True  # fallback


def collect_jobs_pipeline_concurrent(
    client: GitLabClient,
    project: str,
    start: datetime.datetime,
    end: datetime.datetime,
    include_statuses: set[str],
    only_in_range_by: TimeField,
    job_scope: JobScope = "both",
    concurrency: int = 8,
    progress_cb: Optional[Callable[[int, int, int], None]] = None,
) -> List[Job]:
    results: List[Job] = []
    pipelines = [
        p
        for p in client.list_pipelines(project, start, end)
        if _pipeline_matches_scope(p, job_scope)
    ]

    def fetch(pid: int) -> List[Job]:
        out: List[Job] = []
        for j in client.list_pipeline_jobs(project, pid):
            if j.status not in include_statuses:
                continue
            ts_str: Optional[str] = (
                getattr(j, only_in_range_by) or j.created_at or j.started_at
            )
            if not ts_str:
                continue
            ts = parse_iso8601(ts_str)
            if start <= ts <= end and not math.isnan(j.duration_s):
                out.append(j)
        return out

    total = len(pipelines)
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as ex:
        futs = [ex.submit(fetch, p.id) for p in pipelines]
        for fut in as_completed(futs):
            batch = fut.result()
            results.extend(batch)
            done += 1
            if progress_cb:
                # args: pipelines_done, pipelines_total, jobs_so_far
                progress_cb(done, total, len(results))
    return results


def compute_stats(durations: List[float]) -> Stats:
    d = durations
    total = float(sum(d)) if d else float("nan")
    return Stats(
        count=len(d),
        total_s=total,
        min_s=min(d) if d else float("nan"),
        p10_s=percentile(d, 10),
        p25_s=percentile(d, 25),
        median_s=percentile(d, 50),
        p75_s=percentile(d, 75),
        p90_s=percentile(d, 90),
        max_s=max(d) if d else float("nan"),
        mean_s=mean(d),
        stdev_s=stdev(d),
    )


def group_by_name(jobs: List[Job]) -> List[JobNameStats]:
    name_to_jobs: Dict[str, List[Job]] = {}
    for j in jobs:
        name_to_jobs.setdefault(j.name, []).append(j)

    duration_all = sum(job.duration_s for jobs in name_to_jobs.values() for job in jobs)
    out: List[JobNameStats] = []
    for name, js in name_to_jobs.items():
        durations = [j.duration_s for j in js]
        s = compute_stats(durations)

        denom = len(js)
        if denom > 0:
            succ = sum(1 for j in js if j.status == "success")
            fail = sum(1 for j in js if j.status == "failed")
            succ_pct = 100.0 * succ / denom
            fail_pct = 100.0 * fail / denom
        else:
            succ_pct = float("nan")
            fail_pct = float("nan")
        if duration_all > 0:
            total_pct = 100.0 * s.total_s / duration_all
        else:
            total_pct = float("nan")

        out.append(
            JobNameStats(
                name=name,
                stats=s,
                success_pct=succ_pct,
                failed_pct=fail_pct,
                total_pct=total_pct,
            )
        )

    out.sort(
        key=lambda x: (x.stats.total_s if not math.isnan(x.stats.total_s) else -1),
        reverse=True,
    )
    return out


def print_human(overall: Stats, per_name: List[JobNameStats]) -> None:
    def hdr(title: str) -> None:
        print("\n" + title)
        print("=" * len(title))

    def fmt_pct(v: float) -> str:
        return "nan" if math.isnan(v) else f"{v:.1f}%"

    hdr("Overall job duration statistics")
    metric2value = [
        ("count", str(overall.count)),
        ("total", fmt_seconds(overall.total_s)),
        ("min", fmt_seconds(overall.min_s)),
        ("p10", fmt_seconds(overall.p10_s)),
        ("p25", fmt_seconds(overall.p25_s)),
        ("median", fmt_seconds(overall.median_s)),
        ("p75", fmt_seconds(overall.p75_s)),
        ("p90", fmt_seconds(overall.p90_s)),
        ("max", fmt_seconds(overall.max_s)),
        ("mean", fmt_seconds(overall.mean_s)),
        ("stdev", fmt_seconds(overall.stdev_s)),
    ]
    rows = [
        ["metric"] + [name for name, _ in metric2value],
        ["value"] + [value for _, value in metric2value],
    ]
    print(table(rows))

    hdr("Per-job-name counts and time")
    rows2 = [
        [
            "job name",
            "count",
            "total",
            "total%",
            "median",
            "p90",
            "mean",
            "stdev",
            "succ%",
            "fail%",
        ]
    ]
    for item in per_name:
        s = item.stats
        rows2.append(
            [
                item.name,
                str(int(s.count)),
                fmt_seconds(s.total_s),
                fmt_pct(item.total_pct),
                fmt_seconds(s.median_s),
                fmt_seconds(s.p90_s),
                fmt_seconds(s.mean_s),
                fmt_seconds(s.stdev_s),
                fmt_pct(item.success_pct),
                fmt_pct(item.failed_pct),
            ]
        )
    print(table(rows2))


# ----------------------------
# CLI
# ----------------------------


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Fetch GitLab jobs in a time window and compute duration statistics (overall and per job name)."
    )
    ap.add_argument(
        "--gitlab-url",
        required=True,
        help="Base URL of GitLab, e.g. https://gitlab.com or your self-hosted URL",
    )
    ap.add_argument(
        "--project",
        required=True,
        help="Project ID or full path (e.g. 12345 or group/subgroup/project)",
    )
    ap.add_argument(
        "--start",
        required=True,
        help="Start time (ISO 8601, e.g. 2025-08-01T00:00:00Z)",
    )
    ap.add_argument(
        "--end", required=True, help="End time (ISO 8601, e.g. 2025-08-14T23:59:59Z)"
    )
    ap.add_argument(
        "--token",
        help="GitLab Personal Access Token. If omitted, taken from GITLAB_TOKEN env var.",
    )
    ap.add_argument(
        "--statuses",
        default="success,failed",
        help=f"Comma-separated statuses to include (default: success). Options: {','.join(sorted(FINISHED_STATUSES))}",
    )
    ap.add_argument(
        "--time-field",
        default="finished_at",
        choices=["created_at", "started_at", "finished_at"],
        help="Which job timestamp to use for filtering into [start,end] (default: finished_at)",
    )
    ap.add_argument(
        "--job-scope",
        choices=["both", "main", "mrs"],
        default="both",
        help="Which pipelines/jobs to count: 'main' (only main/master branch), 'mrs' (only merge request pipelines), or 'both' (default).",
    )
    ap.add_argument(
        "--format",
        dest="out_format",
        default="table",
        choices=["table", "json"],
        help="Output format (table/json). Default: table",
    )
    ap.add_argument(
        "--concurrency", type=int, default=8, help="Max parallel requests (default: 8)."
    )
    ap.add_argument(
        "--progress",
        action="store_true",
        help="Print live progress while collecting data.",
    )
    ap.add_argument(
        "--debug", action="store_true", help="Print some debug info to stderr"
    )
    args = ap.parse_args()

    token = args.token or os.getenv("GITLAB_TOKEN")
    if not token:
        print(
            "Error: provide --token or set GITLAB_TOKEN environment variable.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        start = parse_iso8601(args.start)
        end = parse_iso8601(args.end)
    except Exception as e:
        print(f"Failed to parse start/end: {e}", file=sys.stderr)
        sys.exit(2)
    if end < start:
        print("Error: --end must be >= --start", file=sys.stderr)
        sys.exit(2)

    include_statuses: set[str] = {
        s.strip().lower() for s in args.statuses.split(",") if s.strip()
    }
    unknown = include_statuses - FINISHED_STATUSES
    if unknown:
        print(
            f"Warning: some statuses are not typical finished statuses: {sorted(unknown)}",
            file=sys.stderr,
        )

    progress_cb: Optional[Callable[[int, int, int], None]] = None
    if args.progress:

        def _progress(p_done: int, p_total: int, jobs_so_far: int) -> None:
            sys.stderr.write(
                f"\r[progress] pipelines: {p_done}/{p_total} | jobs so far: {jobs_so_far}"
            )
            sys.stderr.flush()

        progress_cb = _progress

    client = GitLabClient(args.gitlab_url, token)
    scope: JobScope = args.job_scope  # type: ignore[assignment]

    if args.debug:
        print(
            f"[debug] listing pipelines for {args.project} between {to_iso8601(start)} and {to_iso8601(end)} (scope={scope})",
            file=sys.stderr,
        )

    jobs = collect_jobs_pipeline_concurrent(
        client=client,
        project=args.project,
        start=start,
        end=end,
        include_statuses=include_statuses,
        only_in_range_by=args.time_field,  # type: ignore[arg-type]
        job_scope=scope,
        concurrency=args.concurrency,
        progress_cb=progress_cb,
    )
    if args.progress:
        sys.stderr.write("\n")
        sys.stderr.flush()

    if not jobs:
        print("No matching jobs found in the specified window.", file=sys.stderr)
        empty_stats = Stats(*(0,) + (float("nan"),) * 10)
        if args.out_format == "json":
            payload = ResultPayload(
                window=Window(
                    start=to_iso8601(start),
                    end=to_iso8601(end),
                    time_field=args.time_field,
                ),  # type: ignore[arg-type]
                project=args.project,
                statuses=sorted(include_statuses),
                counts=Counts(jobs_included=0),
                overall=empty_stats,
                per_job_name=[],
            )
            print(json.dumps(asdict(payload), indent=2))
        else:
            print_human(empty_stats, [])
        sys.exit(0)

    durations_all = [j.duration_s for j in jobs]
    overall = compute_stats(durations_all)
    per_name = group_by_name(jobs)

    if args.out_format == "json":
        payload = ResultPayload(
            window=Window(
                start=to_iso8601(start), end=to_iso8601(end), time_field=args.time_field
            ),  # type: ignore[arg-type]
            project=args.project,
            statuses=sorted(include_statuses),
            counts=Counts(jobs_included=len(jobs)),
            overall=overall,
            per_job_name=per_name,
        )
        print(json.dumps(asdict(payload), indent=2))
    else:
        print_human(overall, per_name)


if __name__ == "__main__":
    main()
