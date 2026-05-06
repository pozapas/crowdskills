#!/usr/bin/env python3
"""Decompile and index the Vissim COM CHM help file.

The script accepts either a .chm file or an already extracted CHM directory.
When given a .chm file on Windows, it uses hh.exe -decompile and then builds a
compact JSON/CSV index of HTML topics. It does not copy full manual text into
the skill.

Exit codes:
  0: index created or matches printed
  1: extraction, indexing, or filesystem error
  2: command-line usage error, raised by argparse
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


SCRIPT_TAGS = {"script", "style"}


@dataclass(frozen=True)
class TopicRecord:
    title: str
    file: str
    kind: str
    interface: str
    member: str
    summary: str
    terms: list[str]


@dataclass(frozen=True)
class IndexResult:
    ok: bool
    scanned_topics: int
    indexed_topics: int
    matched_topics: int
    message: str


class TopicTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in SCRIPT_TAGS:
            self.skip_depth += 1
            return
        if tag == "title":
            self.in_title = True
        if tag in {"p", "div", "tr", "td", "th", "li", "br", "pre", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SCRIPT_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "title":
            self.in_title = False
        if tag in {"p", "div", "tr", "li", "table", "pre", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_title:
            self.title_parts.append(data)
        self.parts.append(data)


def clean_text(value: str) -> str:
    value = html.unescape(value).replace("\ufeff", "")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s*\n+", "\n", value)
    return "\n".join(line.strip() for line in value.splitlines() if line.strip())


def parse_html(path: Path, root: Path) -> TopicRecord:
    parser = TopicTextParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    text = clean_text(" ".join(parser.parts))
    title = clean_text(" ".join(parser.title_parts)) or path.stem

    rel_file = str(path.relative_to(root))
    interface, member = infer_interface_member(path.name)
    kind = infer_kind(title, path.name)
    summary = infer_summary(text, title)
    terms = sorted(set(re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", f"{title} {path.stem} {summary}")))

    return TopicRecord(
        title=title,
        file=rel_file,
        kind=kind,
        interface=interface,
        member=member,
        summary=summary,
        terms=terms[:40],
    )


def infer_interface_member(filename: str) -> tuple[str, str]:
    stem = filename.rsplit(".", 1)[0]
    if "~" not in stem:
        return "", ""
    after = stem.split("~", 1)[1]
    if "_" in after:
        interface, suffix = after.split("_", 1)
        return interface, suffix
    if "~" in after:
        interface, member = after.split("~", 1)
        return interface, member
    return after, ""


def infer_kind(title: str, filename: str) -> str:
    lowered = f"{title} {filename}".lower()
    if " attributes" in lowered or "_attributes" in lowered:
        return "attributes"
    if " relations" in lowered or "_relations" in lowered:
        return "relations"
    if " method" in lowered:
        return "method"
    if " property" in lowered:
        return "property"
    if "collection" in lowered:
        return "collection"
    if "container" in lowered:
        return "container"
    return "interface"


def infer_summary(text: str, title: str) -> str:
    lines = [line for line in text.splitlines() if line and line != title]
    for index, line in enumerate(lines):
        if line.lower() == "summary" and index + 1 < len(lines):
            return truncate(lines[index + 1])
    for line in lines:
        if not line.startswith((">>", "Collapse All", "Expand All", "Vissim - COM")):
            return truncate(line)
    return ""


def truncate(value: str, limit: int = 260) -> str:
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def locate_hh() -> Path | None:
    windir = os.environ.get("WINDIR")
    candidates = []
    if windir:
        candidates.append(Path(windir) / "hh.exe")
    found = shutil.which("hh.exe")
    if found:
        candidates.append(Path(found))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def decompile_chm(source: Path, extract_dir: Path, *, force: bool) -> Path:
    hh = locate_hh()
    if hh is None:
        raise RuntimeError("hh.exe was not found; CHM extraction requires Windows HTML Help")
    if extract_dir.exists() and any(extract_dir.iterdir()):
        if not force:
            raise RuntimeError(f"{extract_dir} is not empty; pass --force to reuse it")
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    local_source = source
    if source.parent != Path(os.environ.get("TEMP", source.parent)):
        local_source = Path(os.environ.get("TEMP", str(source.parent))) / source.name
        shutil.copy2(source, local_source)

    subprocess.run(
        [str(hh), "-decompile", str(extract_dir), str(local_source)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 30
    while time.time() < deadline:
        if any(extract_dir.glob("*.html")):
            return extract_dir
        time.sleep(1)
    raise RuntimeError(f"decompile finished but no HTML files were found in {extract_dir}")


def file_matches_queries(path: Path, queries: list[str], *, body_search: bool) -> bool:
    if not queries:
        return True
    query_terms = [query.lower() for query in queries]
    filename = path.name.lower()
    if all(term in filename for term in query_terms):
        return True
    if not body_search:
        return False
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False
    return all(term in raw for term in query_terms)


def build_index(root: Path, queries: list[str], *, body_search: bool) -> tuple[int, list[TopicRecord]]:
    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        raise RuntimeError(f"no HTML files found under {root}")
    candidate_files = [
        path for path in html_files if file_matches_queries(path, queries, body_search=body_search)
    ]
    return len(html_files), [parse_html(path, root) for path in candidate_files]


def filter_records(records: Iterable[TopicRecord], queries: list[str]) -> list[TopicRecord]:
    if not queries:
        return list(records)
    query_terms = [query.lower() for query in queries]
    matches: list[TopicRecord] = []
    for record in records:
        haystack = " ".join(
            [
                record.title,
                record.file,
                record.kind,
                record.interface,
                record.member,
                record.summary,
                " ".join(record.terms),
            ]
        ).lower()
        if all(term in haystack for term in query_terms):
            matches.append(record)
    return matches


def write_json(path: Path, records: list[TopicRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([asdict(record) for record in records], indent=2), encoding="utf-8")


def write_csv(path: Path, records: list[TopicRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "file", "kind", "interface", "member", "summary"],
        )
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row.pop("terms", None)
            writer.writerow(row)


def print_table(records: list[TopicRecord], *, limit: int) -> None:
    shown = records[:limit]
    for record in shown:
        print(f"{record.kind:10} {record.interface:45} {record.member:35} {record.title}")
        if record.summary:
            print(f"  {record.summary}")
        print(f"  {record.file}")
    if len(records) > limit:
        print(f"... {len(records) - limit} more matches not shown")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index Vissim COM CHM help topics.")
    parser.add_argument("source", type=Path, help=".chm file or extracted CHM directory")
    parser.add_argument("--extract-dir", type=Path, help="where to decompile CHM HTML")
    parser.add_argument("--query", action="append", default=[], help="term that must match indexed fields")
    parser.add_argument("--body-search", action="store_true", help="search full HTML text before indexing")
    parser.add_argument("--limit", type=int, default=80)
    parser.add_argument("--out", type=Path, help="write matching records to JSON")
    parser.add_argument("--csv", type=Path, help="write matching records to CSV")
    parser.add_argument("--force", action="store_true", help="overwrite/reuse a non-empty extract directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source
    if not source.exists():
        print(f"source does not exist: {source}")
        return 1
    if args.limit <= 0:
        print("--limit must be positive")
        return 1

    try:
        if source.is_dir():
            root = source
        elif source.suffix.lower() == ".chm":
            extract_dir = args.extract_dir or (Path.cwd() / f"{source.stem}_extracted")
            root = decompile_chm(source, extract_dir, force=args.force)
        else:
            raise RuntimeError("source must be a .chm file or extracted directory")

        scanned_count, records = build_index(root, args.query, body_search=args.body_search)
        matches = records if args.query else filter_records(records, args.query)
        if args.out:
            write_json(args.out, matches)
        if args.csv:
            write_csv(args.csv, matches)
        print(f"Scanned {scanned_count} topics from {root}")
        print(f"Indexed {len(records)} candidate topics")
        print(f"Matched {len(matches)} topics")
        print_table(matches, limit=args.limit)
        return 0
    except Exception as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
