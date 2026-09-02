#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _curation import load_storyboard_spec, parse_seconds, validate_beat_contract, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Allocate semantic reveal beats across each frame from narration-length proportions."
    )
    parser.add_argument("--spec", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Write allocated windows back to the spec.")
    mode.add_argument("--check", action="store_true", help="Validate existing windows without changing the spec.")
    return parser.parse_args()


def visible_units(value: str) -> int:
    return max(1, sum(not char.isspace() for char in str(value)))


def format_second(value: float) -> str:
    rounded = round(value, 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")


def allocate_frame(frame: dict) -> None:
    if frame["source_relation"] == "preserve" and not frame.get("beats"):
        return
    duration = parse_seconds(str(frame["duration"]))
    beats = frame["beats"]
    reveal_indices = [index for index, beat in enumerate(beats) if beat["kind"] == "reveal"]
    if len(reveal_indices) < 2 or beats[-1]["kind"] != "hold":
        raise ValueError(f"Frame {frame['id']} needs at least two reveal beats followed by one hold")

    hold_start = duration * 0.90
    final_reveal_start = duration * 0.65
    earlier_indices = reveal_indices[:-1]
    earlier_weights = [visible_units(beats[index].get("narration", "")) for index in earlier_indices]
    weight_total = sum(earlier_weights)
    cursor = 0.0
    for index, weight in zip(earlier_indices, earlier_weights):
        end = cursor + final_reveal_start * weight / weight_total
        beats[index]["window"] = f"{format_second(cursor)}-{format_second(end)}s"
        cursor = end
    last_reveal_index = reveal_indices[-1]
    beats[last_reveal_index]["window"] = f"{format_second(final_reveal_start)}-{format_second(hold_start)}s"
    beats[-1]["window"] = f"{format_second(hold_start)}-{format_second(duration)}s"


def main() -> int:
    args = parse_args()
    spec_path = args.spec.resolve()
    spec = load_storyboard_spec(spec_path)
    if args.write:
        for frame in spec["frames"]:
            allocate_frame(frame)
        validate_beat_contract(spec, require_windows=True)
        write_json(spec_path, spec)
        print(f"Allocated beat windows for {len(spec['frames'])} frames in {spec_path}")
    else:
        validate_beat_contract(spec, require_windows=True)
        print(f"Beat windows are valid: {spec_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
