#!/usr/bin/env python3
"""Crawl and index the online Pathfinder documentation.

The crawler stays inside one versioned Pathfinder documentation prefix, extracts
titles, headings, compact text summaries, code snippets, and internal links, and
writes JSON, CSV, or Markdown indexes for later skill-grounded lookup.

Exit codes:
  0: crawl completed and requested outputs were written
  1: crawl, parse, network, or filesystem error
  2: command-line usage error, raised by argparse
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen


SCRIPT_TAGS = {"script", "style", "noscript"}
TEXT_BREAK_TAGS = {"p", "div", "br", "li", "tr", "td", "th", "pre", "h1", "h2", "h3", "h4"}
SKIP_EXTENSIONS = {
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".pdf",
    ".zip",
}


@dataclass(frozen=True)
class DocPageRecord:
    title: str
    url: str
    headings: list[str]
    summary: str
    code_blocks: list[str]
    links: list[str]
    matched_queries: list[str]


@dataclass(frozen=True)
class CrawlResult:
    ok: bool
    scanned_pages: int
    matched_pages: int
    failed_pages: int
    message: str


class PathfinderDocParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.headings: list[str] = []
        self.links: list[str] = []
        self.text_parts: list[str] = []
        self.code_blocks: list[str] = []
        self._in_title = False
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []
        self._skip_depth = 0
        self._pre_depth = 0
        self._pre_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in SCRIPT_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag in {"h1", "h2", "h3", "h4"}:
            self._heading_tag = tag
            self._heading_parts = []
        if tag == "a" and attrs_dict.get("href"):
            self.links.append(attrs_dict["href"] or "")
        if tag in {"pre", "code"}:
            self._pre_depth += 1
            if self._pre_depth == 1:
                self._pre_parts = []
        if tag in TEXT_BREAK_TAGS:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SCRIPT_TAGS:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag == "title":
            self._in_title = False
        if tag == self._heading_tag:
            heading = clean_inline(" ".join(self._heading_parts))
            if heading:
                self.headings.append(heading)
            self._heading_tag = None
            self._heading_parts = []
        if tag in {"pre", "code"} and self._pre_depth:
            self._pre_depth -= 1
            if self._pre_depth == 0:
                code = clean_code("".join(self._pre_parts))
                if code and code not in self.code_blocks:
                    self.code_blocks.append(code)
        if tag in TEXT_BREAK_TAGS:
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self.title_parts.append(data)
        if self._heading_tag:
            self._heading_parts.append(data)
        if self._pre_depth:
            self._pre_parts.append(data)
        self.text_parts.append(data)


def clean_inline(value: str) -> str:
    value = html.unescape(value).replace("\ufeff", "")
    return re.sub(r"\s+", " ", value).strip()


def clean_code(value: str, limit: int = 900) -> str:
    value = html.unescape(value).replace("\r\n", "\n").replace("\r", "\n")
    value = "\n".join(line.rstrip() for line in value.splitlines()).strip()
    return value if len(value) <= limit else value[: limit - 3].rstrip() + "..."


def clean_body(value: str) -> list[str]:
    value = html.unescape(value).replace("\ufeff", "")
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n\s*\n+", "\n", value)
    lines = [line.strip() for line in value.splitlines()]
    skip = {"next", "previous", "table of contents", "search", "pathfinder"}
    return [line for line in lines if line and line.lower() not in skip]


def normalize_url(url: str, base: str) -> str:
    joined = urljoin(base, url)
    joined, _fragment = urldefrag(joined)
    parsed = urlparse(joined)
    path = parsed.path
    if not Path(path).suffix and not path.endswith("/"):
        path = f"{path}/"
    return parsed._replace(path=path, query="").geturl()


def should_visit(url: str, prefix: str) -> bool:
    if not url.startswith(prefix):
        return False
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    return suffix not in SKIP_EXTENSIONS


def fetch_url(url: str, timeout: int, user_agent: str) -> str:
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def parse_page(url: str, raw_html: str, prefix: str) -> DocPageRecord:
    parser = PathfinderDocParser()
    parser.feed(raw_html)
    title = clean_inline(" ".join(parser.title_parts))
    if not title:
        title = parser.headings[0] if parser.headings else url
    lines = clean_body(" ".join(parser.text_parts))
    summary = infer_summary(lines, parser.headings)
    links = sorted(
        {
            normalize_url(link, url)
            for link in parser.links
            if link and should_visit(normalize_url(link, url), prefix)
        }
    )
    return DocPageRecord(
        title=title,
        url=url,
        headings=dedupe(parser.headings)[:40],
        summary=summary,
        code_blocks=parser.code_blocks[:12],
        links=links,
        matched_queries=[],
    )


def infer_summary(lines: list[str], headings: list[str], limit: int = 360) -> str:
    heading_set = {heading.lower() for heading in headings}
    candidates = [line for line in lines if line.lower() not in heading_set]
    summary = " ".join(candidates[:4])
    return summary if len(summary) <= limit else summary[: limit - 3].rstrip() + "..."


def dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(value.strip())
    return result


def record_matches(record: DocPageRecord, queries: list[str]) -> DocPageRecord | None:
    if not queries:
        return record
    haystack = " ".join(
        [
            record.title,
            record.url,
            record.summary,
            " ".join(record.headings),
            " ".join(record.code_blocks),
        ]
    ).lower()
    matches = [query for query in queries if query.lower() in haystack]
    if not matches:
        return None
    return DocPageRecord(
        title=record.title,
        url=record.url,
        headings=record.headings,
        summary=record.summary,
        code_blocks=record.code_blocks,
        links=record.links,
        matched_queries=matches,
    )


def crawl(args: argparse.Namespace) -> tuple[list[DocPageRecord], CrawlResult]:
    prefix = normalize_url(args.prefix, args.prefix)
    queue = [normalize_url(args.start, prefix)]
    visited: set[str] = set()
    records: list[DocPageRecord] = []
    failures: list[str] = []

    while queue and len(visited) < args.max_pages:
        url = queue.pop(0)
        if url in visited or not should_visit(url, prefix):
            continue
        visited.add(url)
        try:
            raw_html = fetch_url(url, args.timeout, args.user_agent)
            record = parse_page(url, raw_html, prefix)
            matched = record_matches(record, args.query)
            if matched:
                records.append(matched)
            for link in record.links:
                if link not in visited and link not in queue and should_visit(link, prefix):
                    queue.append(link)
            if args.delay > 0:
                time.sleep(args.delay)
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeError) as exc:
            failures.append(f"{url}: {exc}")

    result = CrawlResult(
        ok=not failures or bool(records),
        scanned_pages=len(visited),
        matched_pages=len(records),
        failed_pages=len(failures),
        message=f"Scanned {len(visited)} pages; matched {len(records)} pages; failed {len(failures)} pages",
    )
    if args.show_failures:
        for failure in failures:
            print(f"warning: {failure}", file=sys.stderr)
    return records, result


def write_json(path: Path, records: list[DocPageRecord], result: CrawlResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"result": asdict(result), "pages": [asdict(record) for record in records]}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv(path: Path, records: list[DocPageRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "url", "summary", "headings", "matched_queries"],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "title": record.title,
                    "url": record.url,
                    "summary": record.summary,
                    "headings": " | ".join(record.headings),
                    "matched_queries": " | ".join(record.matched_queries),
                }
            )


def write_markdown(path: Path, records: list[DocPageRecord], result: CrawlResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Pathfinder Documentation Index", "", result.message, ""]
    for record in records:
        lines.extend([f"## {record.title}", "", record.url, ""])
        if record.summary:
            lines.extend([record.summary, ""])
        if record.headings:
            lines.extend(["Headings:", ""])
            lines.extend([f"- {heading}" for heading in record.headings[:20]])
            lines.append("")
        if record.code_blocks:
            lines.extend(["Code snippets:", ""])
            for code in record.code_blocks[:3]:
                lines.extend(["```text", code, "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def print_table(records: list[DocPageRecord], result: CrawlResult, limit: int) -> None:
    print(result.message)
    for record in records[:limit]:
        print(f"- {record.title}")
        print(f"  {record.url}")
        if record.summary:
            print(f"  {record.summary}")
    if len(records) > limit:
        print(f"... {len(records) - limit} more matches not shown")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl versioned online Pathfinder docs.")
    parser.add_argument(
        "--start",
        default="https://www.thunderheadeng.com/docs/2026-1/pathfinder/introduction/",
        help="first Pathfinder documentation page to crawl",
    )
    parser.add_argument(
        "--prefix",
        default="https://www.thunderheadeng.com/docs/2026-1/pathfinder/",
        help="URL prefix that constrains the crawl",
    )
    parser.add_argument("--query", action="append", default=[], help="case-insensitive term to match")
    parser.add_argument("--max-pages", type=int, default=80)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--limit", type=int, default=20, help="number of matches to print")
    parser.add_argument("--out", type=Path, help="write JSON index")
    parser.add_argument("--csv", type=Path, help="write CSV index")
    parser.add_argument("--markdown", type=Path, help="write Markdown index")
    parser.add_argument("--show-failures", action="store_true")
    parser.add_argument(
        "--user-agent",
        default="CrowdSkillPathfinderIndexer/1.0",
        help="HTTP user agent string",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_pages <= 0:
        print("--max-pages must be positive")
        return 1
    if args.timeout <= 0:
        print("--timeout must be positive")
        return 1
    if args.delay < 0:
        print("--delay must be non-negative")
        return 1

    try:
        records, result = crawl(args)
        if args.out:
            write_json(args.out, records, result)
        if args.csv:
            write_csv(args.csv, records)
        if args.markdown:
            write_markdown(args.markdown, records, result)
        print_table(records, result, args.limit)
        return 0 if result.ok else 1
    except Exception as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
