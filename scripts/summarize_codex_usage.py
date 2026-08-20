#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class UsageSummary:
    path: str
    input_tokens: int
    cached_input_tokens: int
    non_cached_input_tokens: int
    output_tokens: int
    reasoning_output_tokens: int
    total_tokens: int
    wall_seconds: float | None


def parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def usage_from_event(event: dict[str, object]) -> dict[str, object] | None:
    payload = event.get("payload")
    if isinstance(payload, dict) and payload.get("type") == "token_count":
        info = payload.get("info")
        if isinstance(info, dict) and isinstance(info.get("total_token_usage"), dict):
            return info["total_token_usage"]
    if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
        return event["usage"]
    return None


def nonnegative_int(usage: dict[str, object], key: str) -> int:
    value = usage.get(key, 0)
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"invalid {key}: {value!r}")
    return value


def summarize(path: Path) -> UsageSummary:
    latest_usage: dict[str, object] | None = None
    timestamps: list[datetime] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {error.msg}") from error
            timestamp = parse_timestamp(event.get("timestamp"))
            if timestamp is not None:
                timestamps.append(timestamp)
            candidate = usage_from_event(event)
            if candidate is not None:
                latest_usage = candidate

    if latest_usage is None:
        raise ValueError(f"{path}: no token usage event found")
    input_tokens = nonnegative_int(latest_usage, "input_tokens")
    cached_input_tokens = nonnegative_int(latest_usage, "cached_input_tokens")
    output_tokens = nonnegative_int(latest_usage, "output_tokens")
    reasoning_output_tokens = nonnegative_int(latest_usage, "reasoning_output_tokens")
    total_tokens = latest_usage.get("total_tokens")
    if total_tokens is None:
        total_tokens = input_tokens + output_tokens
    if not isinstance(total_tokens, int) or total_tokens < 0:
        raise ValueError(f"invalid total_tokens: {total_tokens!r}")
    wall_seconds = None
    if len(timestamps) >= 2:
        wall_seconds = round((max(timestamps) - min(timestamps)).total_seconds(), 3)
    return UsageSummary(
        path=str(path),
        input_tokens=input_tokens,
        cached_input_tokens=cached_input_tokens,
        non_cached_input_tokens=max(input_tokens - cached_input_tokens, 0),
        output_tokens=output_tokens,
        reasoning_output_tokens=reasoning_output_tokens,
        total_tokens=total_tokens,
        wall_seconds=wall_seconds,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize token and elapsed-time data from Codex JSONL.")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summaries = [summarize(path.expanduser().resolve()) for path in args.paths]
    if args.json:
        print(json.dumps([asdict(summary) for summary in summaries], indent=2))
        return 0

    print("path\tinput\tcached\tnon_cached\toutput\treasoning\ttotal\twall_s")
    for summary in summaries:
        wall = "" if summary.wall_seconds is None else str(summary.wall_seconds)
        print(
            f"{summary.path}\t{summary.input_tokens}\t{summary.cached_input_tokens}\t"
            f"{summary.non_cached_input_tokens}\t{summary.output_tokens}\t"
            f"{summary.reasoning_output_tokens}\t{summary.total_tokens}\t{wall}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
