"""
Provenance and audit utilities.

Captures run metadata (config hash, git SHA, timing, endpoints,
rate-limit events, errors) and writes to structured logs and/or sidecar
JSON files for reproducibility and audit.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


def _safe_now_ms() -> int:
    return int(time.time() * 1000)


def compute_sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def try_get_git_sha(cwd: Optional[str] = None) -> Optional[str]:
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=cwd or os.getcwd()
        )
        return sha.decode("utf-8").strip()
    except Exception:
        return None


@dataclass
class RateLimitEvent:
    timestamp_ms: int
    endpoint: str
    remaining: Optional[int] = None
    limit: Optional[int] = None
    reset_epoch_s: Optional[int] = None
    retry_after_s: Optional[int] = None


@dataclass
class ErrorEvent:
    timestamp_ms: int
    message: str
    category: Optional[str] = None
    status_code: Optional[int] = None
    endpoint: Optional[str] = None


@dataclass
class RunProvenance:
    correlation_id: str
    started_ms: int = field(default_factory=_safe_now_ms)
    finished_ms: Optional[int] = None
    duration_ms: Optional[int] = None
    config_hash: Optional[str] = None
    config_path: Optional[str] = None
    git_sha: Optional[str] = None
    source_endpoint: Optional[str] = None
    target_endpoint: Optional[str] = None
    success: Optional[bool] = None
    transferred_count: Optional[int] = None
    details: Dict[str, Any] = field(default_factory=dict)
    rate_limit_events: List[RateLimitEvent] = field(default_factory=list)
    error_events: List[ErrorEvent] = field(default_factory=list)


class ProvenanceRecorder:
    def __init__(
        self, output_dir: Optional[str] = None, jsonl_log_path: Optional[str] = None
    ) -> None:
        self.output_dir = Path(output_dir) if output_dir else None
        self.jsonl_log_path = Path(jsonl_log_path) if jsonl_log_path else None
        self._run: Optional[RunProvenance] = None

    def start_run(
        self,
        correlation_id: str,
        config_path: Optional[str],
        source_endpoint: Optional[str],
        target_endpoint: Optional[str],
    ) -> None:
        config_hash: Optional[str] = None
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_text = f.read()
                config_hash = compute_sha256_of_text(config_text)
            except Exception:
                config_hash = None
        self._run = RunProvenance(
            correlation_id=correlation_id,
            config_hash=config_hash,
            config_path=config_path,
            git_sha=try_get_git_sha(),
            source_endpoint=source_endpoint,
            target_endpoint=target_endpoint,
        )
        self._emit_jsonl({"event": "run_started", **asdict(self._run)})

    def record_rate_limit(self, endpoint: str, info: Dict[str, Any]) -> None:
        if not self._run:
            return
        ev = RateLimitEvent(
            timestamp_ms=_safe_now_ms(),
            endpoint=endpoint,
            remaining=info.get("remaining"),
            limit=info.get("limit"),
            reset_epoch_s=info.get("reset_epoch_s"),
            retry_after_s=info.get("retry_after_s"),
        )
        self._run.rate_limit_events.append(ev)
        self._emit_jsonl({"event": "ratelimit", **asdict(ev)})

    def record_error(
        self,
        message: str,
        *,
        category: Optional[str] = None,
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        if not self._run:
            return
        ev = ErrorEvent(
            timestamp_ms=_safe_now_ms(),
            message=message,
            category=category,
            status_code=status_code,
            endpoint=endpoint,
        )
        self._run.error_events.append(ev)
        self._emit_jsonl({"event": "error", **asdict(ev)})

    def complete_run(
        self, success: bool, transferred_count: Optional[int], details: Dict[str, Any]
    ) -> None:
        if not self._run:
            return
        self._run.finished_ms = _safe_now_ms()
        self._run.duration_ms = self._run.finished_ms - self._run.started_ms
        self._run.success = success
        self._run.transferred_count = transferred_count
        self._run.details = details
        # Write sidecar JSON if requested
        if self.output_dir:
            try:
                self.output_dir.mkdir(parents=True, exist_ok=True)
                sidecar = self.output_dir / f"run_{self._run.correlation_id}.json"
                with open(sidecar, "w", encoding="utf-8") as f:
                    json.dump(asdict(self._run), f, indent=2)
            except Exception:
                pass
        self._emit_jsonl({"event": "run_finished", **asdict(self._run)})

    def _emit_jsonl(self, obj: Dict[str, Any]) -> None:
        if not self.jsonl_log_path:
            return
        try:
            self.jsonl_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.jsonl_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(obj) + "\n")
        except Exception:
            pass
