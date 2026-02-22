#!/usr/bin/env python3
"""
@file cli.py
@brief Module implementation for HtmlDownloader runtime.
@details Contains executable logic and internal helpers used by the CLI workflow.
@module_symbols functions=28 classes=12 variables=4
@functions _parse_version_tuple, _is_version_newer, _get_latest_version_from_github, check_for_new_version, safe_filename, positive_int, is_http_url, normalize_url, ensure_parent, local_path_for_url, download_one, escape_html, limit_toc_nodes, ensure_heading_ids, strip_styles, toc_from_headings, toc_from_nav_html, nav_outline_from_html, iter_asset_urls, rewrite_asset_links_inplace, normalize_document_links_inplace, build_toc_html, build_frameset_index, minimal_readable_wrapper, guess_ext_from_content_type, build_arg_parser, print_strict_help, main
@classes TocNode, Logger, UpgradeAction, VersionedArgumentParser, BaseDownloader, DownloaderRegistry, NetworkImageRecorder, DocumentViewerDownloader, DoxygenExportDownloader, ResourceExplorerModule, RMModuleDoxigen, ResourceExplorerDownloader
@variables GITHUB_API_TIMEOUT_S, ASSET_ATTRS, HEADING_TAG_RE, ALLOWED_EXTERNAL_LINK_SCHEMES
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urldefrag, unquote

import requests
from bs4 import BeautifulSoup  # pyright: ignore[reportMissingImports]
from tqdm import tqdm  # pyright: ignore[reportMissingModuleSource]
import uuid

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError  # pyright: ignore[reportMissingImports]

from .version import __version__


#: @var GITHUB_API_TIMEOUT_S @brief Module-level variable `GITHUB_API_TIMEOUT_S`.
GITHUB_API_TIMEOUT_S = 1


def _parse_version_tuple(v: str) -> Optional[Tuple[int, ...]]:
    """
    @brief Execute `_parse_version_tuple`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param v Input argument for `_parse_version_tuple`.
    @return Optional[Tuple[int, ...]] Return value of `_parse_version_tuple`.
    """
    v = (v or "").strip()
    if not v:
        return None
    if v.startswith(("v", "V")):
        v = v[1:]
    if not re.fullmatch(r"\d+(?:\.\d+)*", v):
        return None
    try:
        return tuple(int(p) for p in v.split("."))
    except Exception:
        return None


def _is_version_newer(latest: str, current: str) -> bool:
    """
    @brief Execute `_is_version_newer`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param latest Input argument for `_is_version_newer`.
    @param current Input argument for `_is_version_newer`.
    @return bool Return value of `_is_version_newer`.
    """
    latest_t = _parse_version_tuple(latest)
    current_t = _parse_version_tuple(current)
    if not latest_t or not current_t:
        return False
    width = max(len(latest_t), len(current_t))
    latest_t = latest_t + (0,) * (width - len(latest_t))
    current_t = current_t + (0,) * (width - len(current_t))
    return latest_t > current_t


def _get_latest_version_from_github(owner: str, repo: str) -> Optional[str]:
    """
    @brief Execute `_get_latest_version_from_github`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param owner Input argument for `_get_latest_version_from_github`.
    @param repo Input argument for `_get_latest_version_from_github`.
    @return Optional[str] Return value of `_get_latest_version_from_github`.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        r = requests.get(
            url,
            timeout=GITHUB_API_TIMEOUT_S,
            headers={"Accept": "application/vnd.github+json"},
        )
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict):
            return None
        tag = data.get("tag_name") or data.get("name")
        if not isinstance(tag, str):
            return None
        tag = tag.strip()
        if tag.startswith(("v", "V")):
            tag = tag[1:]
        return tag if _parse_version_tuple(tag) else None
    except Exception:
        return None


def check_for_new_version(program: str, current_version: str) -> None:
    """
    @brief Execute `check_for_new_version`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param program Input argument for `check_for_new_version`.
    @param current_version Input argument for `check_for_new_version`.
    @return None Return value of `check_for_new_version`.
    """

    latest = _get_latest_version_from_github("Ogekuri", "HtmlDownloader")
    if not latest:
        return
    if _is_version_newer(latest, current_version):
        print(
            f"A new version of {program} is available: current {current_version}, latest {latest}. "
            f"To upgrade, run: {program} --upgrade"
        )


# ----------------------------
# Shared helpers
# ----------------------------


def safe_filename(path: str) -> str:
    """
    @brief Execute `safe_filename`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param path Input argument for `safe_filename`.
    @return str Return value of `safe_filename`.
    """
    path = (path or "").strip()
    path = re.sub(r"[<>:\"|?*\x00-\x1F]", "_", path)
    path = path.replace("\\", "_")
    return path


def positive_int(value: str) -> int:
    """
    @brief Execute `positive_int`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param value Input argument for `positive_int`.
    @return int Return value of `positive_int`.
    """
    try:
        parsed = int(value)
    except Exception as exc:
        raise argparse.ArgumentTypeError("deve essere un intero") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("deve essere un intero positivo")
    return parsed


def is_http_url(s: str) -> bool:
    """
    @brief Execute `is_http_url`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param s Input argument for `is_http_url`.
    @return bool Return value of `is_http_url`.
    """
    try:
        u = urlparse(s)
        return u.scheme in ("http", "https")
    except Exception:
        return False


def normalize_url(u: str, base: str) -> str:
    """
    @brief Execute `normalize_url`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param u Input argument for `normalize_url`.
    @param base Input argument for `normalize_url`.
    @return str Return value of `normalize_url`.
    """
    u = (u or "").strip()
    if not u:
        return u
    if u.startswith(("data:", "mailto:", "javascript:", "blob:")):
        return u
    return urljoin(base, u)


def ensure_parent(p: Path) -> None:
    """
    @brief Execute `ensure_parent`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param p Input argument for `ensure_parent`.
    @return None Return value of `ensure_parent`.
    """
    p.parent.mkdir(parents=True, exist_ok=True)


def local_path_for_url(asset_url: str, out_dir: Path) -> Path:
    """
    @brief Execute `local_path_for_url`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param asset_url Input argument for `local_path_for_url`.
    @param out_dir Input argument for `local_path_for_url`.
    @return Path Return value of `local_path_for_url`.
    """
    u = urlparse(asset_url)
    host = safe_filename(u.netloc or "nohost")
    p = u.path if u.path else "/index"
    if p.endswith("/"):
        p += "index"
    p = safe_filename(p.lstrip("/"))

    if u.query:
        q = safe_filename(re.sub(r"[^a-zA-Z0-9]+", "_", u.query))[:80]
        root, ext = os.path.splitext(p)
        p = f"{root}__q_{q}{ext or ''}"

    return out_dir / "assets" / host / p


def download_one(
    session: requests.Session, url: str, dest: Path, timeout: int = 60
) -> bool:
    """
    @brief Execute `download_one`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param session Input argument for `download_one`.
    @param url Input argument for `download_one`.
    @param dest Input argument for `download_one`.
    @param timeout Input argument for `download_one`.
    @return bool Return value of `download_one`.
    """
    ensure_parent(dest)
    try:
        with session.get(url, stream=True, timeout=timeout, allow_redirects=True) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 128):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception:
        return False


def escape_html(s: str) -> str:
    """
    @brief Execute `escape_html`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param s Input argument for `escape_html`.
    @return str Return value of `escape_html`.
    """
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


@dataclass
class TocNode:
    """
    @brief Define class `TocNode`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    title: str
    href: str
    children: List["TocNode"] = field(default_factory=list)


def limit_toc_nodes(nodes: List[TocNode], max_entries: Optional[int]) -> List[TocNode]:
    """
    @brief Execute `limit_toc_nodes`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param nodes Input argument for `limit_toc_nodes`.
    @param max_entries Input argument for `limit_toc_nodes`.
    @return List[TocNode] Return value of `limit_toc_nodes`.
    """
    if not max_entries or max_entries <= 0:
        return nodes

    count = 0

    def trim_list(items: List[TocNode]) -> List[TocNode]:
        """
        @brief Execute `trim_list`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param items Input argument for `trim_list`.
        @return List[TocNode] Return value of `trim_list`.
        """
        nonlocal count
        out: List[TocNode] = []
        for n in items:
            if count >= max_entries:
                break
            count += 1
            n.children = trim_list(n.children)
            out.append(n)
        return out

    return trim_list(nodes)


def ensure_heading_ids(soup: BeautifulSoup) -> None:
    """
    @brief Execute `ensure_heading_ids`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param soup Input argument for `ensure_heading_ids`.
    @return None Return value of `ensure_heading_ids`.
    """
    used: Set[str] = set()
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        hid = h.get("id")
        text = " ".join(h.get_text(" ", strip=True).split())
        if not hid and text:
            base = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
            if base:
                cand = base
                i = 2
                while cand in used:
                    cand = f"{base}-{i}"
                    i += 1
                h["id"] = cand
                hid = cand
        if hid:
            used.add(hid)


def strip_styles(soup: BeautifulSoup) -> None:
    """
    @brief Execute `strip_styles`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param soup Input argument for `strip_styles`.
    @return None Return value of `strip_styles`.
    """
    for link in list(soup.find_all("link", rel=lambda v: v and "stylesheet" in v)):
        link.decompose()
    for style in list(soup.find_all("style")):
        style.decompose()
    for tag in soup.find_all(True):
        if tag.has_attr("style"):
            del tag["style"]
        if tag.has_attr("class"):
            del tag["class"]


def toc_from_headings(soup: BeautifulSoup) -> List[TocNode]:
    """
    @brief Execute `toc_from_headings`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param soup Input argument for `toc_from_headings`.
    @return List[TocNode] Return value of `toc_from_headings`.
    """
    nodes: List[TocNode] = []
    stack: List[Tuple[int, TocNode]] = []
    for h in soup.find_all(re.compile(r"^h[1-6]$")):
        hid = h.get("id")
        if not hid:
            continue
        title = " ".join(h.get_text(" ", strip=True).split())
        if not title:
            continue
        level = int(h.name[1])
        node = TocNode(title=title, href=f"#{hid}")
        while stack and stack[-1][0] >= level:
            stack.pop()
        if stack:
            stack[-1][1].children.append(node)
        else:
            nodes.append(node)
        stack.append((level, node))
    return nodes


def toc_from_nav_html(toc_html: str, base_url: str) -> List[TocNode]:
    """
    @brief Execute `toc_from_nav_html`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param toc_html Input argument for `toc_from_nav_html`.
    @param base_url Input argument for `toc_from_nav_html`.
    @return List[TocNode] Return value of `toc_from_nav_html`.
    """
    soup = BeautifulSoup(toc_html, "lxml")

    def parse_list(list_el) -> List[TocNode]:
        """
        @brief Execute `parse_list`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param list_el Input argument for `parse_list`.
        @return List[TocNode] Return value of `parse_list`.
        """
        items: List[TocNode] = []
        for li in list_el.find_all("li", recursive=False):
            link = li.find("a")
            if not link:
                # Check for title-only elements (e.g., <li class="toc-title">)
                if "toc-title" in li.get("class", []) or li.get("id") == "doc-lister":
                    title = " ".join(li.get_text(" ", strip=True).split())
                    if title:
                        # Create a node without href (will be rendered as plain text)
                        node = TocNode(title=title, href="#")
                        items.append(node)
                continue
            title = " ".join(link.get_text(" ", strip=True).split())
            href = normalize_url(link.get("href") or "", base_url)
            if not title or not href:
                continue
            node = TocNode(title=title, href=href)
            child_lists = li.find_all(["ul", "ol"], recursive=False)
            for cl in child_lists:
                node.children.extend(parse_list(cl))
            items.append(node)
        return items

    top_lists = soup.find_all(["ul", "ol"], recursive=False)
    if not top_lists:
        # fallback: attempt with any list if no top-level found
        top_lists = soup.find_all(["ul", "ol"])
    out: List[TocNode] = []
    if top_lists:
        # Process only the first list to avoid duplicates from multiple nav structures
        out.extend(parse_list(top_lists[0]))
    return out


def nav_outline_from_html(nav_html: str) -> str:
    """
    @brief Execute `nav_outline_from_html`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param nav_html Input argument for `nav_outline_from_html`.
    @return str Return value of `nav_outline_from_html`.
    """
    soup = BeautifulSoup(nav_html or "", "lxml")
    root_ul = soup.find("ul")
    lines: List[str] = []

    def norm_text(t: str) -> str:
        """
        @brief Execute `norm_text`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param t Input argument for `norm_text`.
        @return str Return value of `norm_text`.
        """
        clean = " ".join((t or "").replace("\xa0", " ").split())
        return clean.replace(" ", "_")

    def bullet(depth: int) -> str:
        """
        @brief Execute `bullet`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param depth Input argument for `bullet`.
        @return str Return value of `bullet`.
        """
        if depth == 0:
            return "*"
        if depth == 1:
            return "o"
        return "#"

    def walk_ul(ul, depth: int) -> None:
        """
        @brief Execute `walk_ul`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param ul Input argument for `walk_ul`.
        @param depth Input argument for `walk_ul`.
        @return None Return value of `walk_ul`.
        """
        for li in ul.find_all("li", recursive=False):
            label_el = None
            if hasattr(li, "select_one"):
                label_el = li.select_one(":scope > div .label a") or li.select_one(
                    ":scope > span.label a"
                )
            title = ""
            if label_el:
                title = norm_text(label_el.get_text(" ", strip=True))
            if title:
                indent = " " * (4 + depth * 6)
                lines.append(f"{indent}{bullet(depth)} {title}")
            child_ul = li.find("ul", recursive=False)
            if child_ul:
                walk_ul(child_ul, depth + 1)

    if root_ul:
        walk_ul(root_ul, 0)

    return "\n".join(lines)


#: @var ASSET_ATTRS @brief Module-level variable `ASSET_ATTRS`.
ASSET_ATTRS = [
    ("img", "src"),
    ("img", "data-src"),
    ("source", "srcset"),
    ("link", "href"),
]

#: @var HEADING_TAG_RE @brief Module-level variable `HEADING_TAG_RE`.
HEADING_TAG_RE = re.compile(r"^h[1-6]$")


class Logger:
    """
    @brief Define class `Logger`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """

    def __init__(self, verbose: bool = False, debug: bool = False):
        """
        @brief Execute `__init__`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `__init__`.
        @param verbose Input argument for `__init__`.
        @param debug Input argument for `__init__`.
        @return Any Return value of `__init__`.
        """
        self.verbose_enabled = bool(verbose or debug)
        self.debug_enabled = bool(debug)

    def info(self, msg: str) -> None:
        """
        @brief Execute `info`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `info`.
        @param msg Input argument for `info`.
        @return None Return value of `info`.
        """
        print(msg)

    def verbose(self, msg: str) -> None:
        """
        @brief Execute `verbose`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `verbose`.
        @param msg Input argument for `verbose`.
        @return None Return value of `verbose`.
        """
        if self.verbose_enabled:
            print(msg)

    def debug(self, msg: str) -> None:
        """
        @brief Execute `debug`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `debug`.
        @param msg Input argument for `debug`.
        @return None Return value of `debug`.
        """
        if self.debug_enabled:
            print(msg)

    def check(self, msg: str) -> None:
        """
        @brief Execute `check`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `check`.
        @param msg Input argument for `check`.
        @return None Return value of `check`.
        """
        if self.verbose_enabled or self.debug_enabled:
            print(msg)


class UpgradeAction(argparse.Action):
    """
    @brief Define class `UpgradeAction`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values,
        option_string: Optional[str] = None,
    ) -> None:
        """
        @brief Execute `__call__`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `__call__`.
        @param parser Input argument for `__call__`.
        @param namespace Input argument for `__call__`.
        @param values Input argument for `__call__`.
        @param option_string Input argument for `__call__`.
        @return None Return value of `__call__`.
        """
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    "htmldownloader",
                ]
            )
            parser.exit(proc.returncode)
        except Exception as exc:
            parser.exit(1, f"Upgrade failed: {exc}\n")


class VersionedArgumentParser(argparse.ArgumentParser):
    """
    @brief Define class `VersionedArgumentParser`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """

    def __init__(self, *args, version: str = "", **kwargs):
        """
        @brief Execute `__init__`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `__init__`.
        @param version Input argument for `__init__`.
        @param *args Input argument for `__init__`.
        @param **kwargs Input argument for `__init__`.
        @return Any Return value of `__init__`.
        """
        super().__init__(*args, **kwargs)
        self._usage_version = (version or "").strip()

    def format_usage(self) -> str:
        """
        @brief Execute `format_usage`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `format_usage`.
        @return str Return value of `format_usage`.
        """
        s = super().format_usage()
        if not s or not self._usage_version:
            return s
        # Append version to the first line of the usage (preserve trailing parts)
        parts = s.splitlines(True)
        if not parts:
            return s
        first = parts[0].rstrip("\r\n")
        rest = "".join(parts[1:])
        first = f"{first} ({self._usage_version})\n"
        return first + rest


def iter_asset_urls(soup: BeautifulSoup, page_url: str) -> Set[str]:
    """
    @brief Execute `iter_asset_urls`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param soup Input argument for `iter_asset_urls`.
    @param page_url Input argument for `iter_asset_urls`.
    @return Set[str] Return value of `iter_asset_urls`.
    """
    urls: Set[str] = set()

    for tag_name, attr in ASSET_ATTRS:
        for t in soup.find_all(tag_name):
            v = t.get(attr)
            if not v:
                continue
            if attr == "srcset":
                parts = [p.strip().split(" ")[0] for p in v.split(",") if p.strip()]
                for p in parts:
                    u = normalize_url(p, page_url)
                    if is_http_url(u):
                        urls.add(u)
            else:
                u = normalize_url(v, page_url)
                if is_http_url(u):
                    urls.add(u)

    # inline background-image url(...)
    bg_re = re.compile(r"url\(([^)]+)\)")
    for t in soup.find_all(style=True):
        style = t.get("style") or ""
        for m in bg_re.finditer(style):
            raw = m.group(1).strip().strip("'\"")
            u = normalize_url(raw, page_url)
            if is_http_url(u):
                urls.add(u)

    return urls


def rewrite_asset_links_inplace(
    soup: BeautifulSoup, base_url: str, out_dir: Path
) -> None:
    """
    @brief Execute `rewrite_asset_links_inplace`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param soup Input argument for `rewrite_asset_links_inplace`.
    @param base_url Input argument for `rewrite_asset_links_inplace`.
    @param out_dir Input argument for `rewrite_asset_links_inplace`.
    @return None Return value of `rewrite_asset_links_inplace`.
    """
    def to_rel(u: str) -> str:
        """
        @brief Execute `to_rel`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param u Input argument for `to_rel`.
        @return str Return value of `to_rel`.
        """
        u2 = normalize_url(u, base_url)
        if not is_http_url(u2):
            return u
        lp = local_path_for_url(u2, out_dir)
        return lp.relative_to(out_dir).as_posix()

    for tag_name, attr in ASSET_ATTRS:
        for t in soup.find_all(tag_name):
            v = t.get(attr)
            if not v:
                continue
            if attr == "srcset":
                parts = []
                for seg in (v or "").split(","):
                    seg = seg.strip()
                    if not seg:
                        continue
                    bits = seg.split()
                    url_part = bits[0]
                    rest = " ".join(bits[1:])
                    parts.append(f"{to_rel(url_part)}{(' ' + rest) if rest else ''}")
                t[attr] = ", ".join(parts)
            else:
                t[attr] = to_rel(v)

    bg_re = re.compile(r"url\(([^)]+)\)")
    for t in soup.find_all(style=True):
        style = t.get("style") or ""

        def repl(m):
            """
            @brief Execute `repl`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param m Input argument for `repl`.
            @return Any Return value of `repl`.
            """
            raw = m.group(1).strip().strip("'\"")
            return f"url('{to_rel(raw)}')"

        t["style"] = bg_re.sub(repl, style)


#: @var ALLOWED_EXTERNAL_LINK_SCHEMES @brief Module-level variable `ALLOWED_EXTERNAL_LINK_SCHEMES`.
ALLOWED_EXTERNAL_LINK_SCHEMES = {
    "http",
    "https",
    "ftp",
    "ftps",
}


def normalize_document_links_inplace(soup: BeautifulSoup, logger: Optional[Logger]) -> None:
    """
    @brief Execute `normalize_document_links_inplace`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param soup Input argument for `normalize_document_links_inplace`.
    @param logger Input argument for `normalize_document_links_inplace`.
    @return None Return value of `normalize_document_links_inplace`.
    """

    if not soup:
        return

    # Index document ids case-insensitively
    id_map: Dict[str, str] = {}
    for el in soup.find_all(True):
        el_id = (el.get("id") or "").strip()
        if el_id:
            id_map.setdefault(el_id.lower(), el_id)

    total = 0
    kept_external = 0
    kept_anchor = 0
    rewritten = 0
    removed = 0

    debug_samples: List[str] = []

    for a in soup.find_all("a"):
        if not a.has_attr("href"):
            continue
        href_raw = (a.get("href") or "").strip()
        if href_raw == "":
            total += 1
            try:
                del a["href"]
            except Exception:
                a["href"] = None
            removed += 1
            if logger and logger.debug_enabled and len(debug_samples) < 10:
                debug_samples.append("drop empty href")
            continue

        total += 1

        # Direct in-document anchor
        if href_raw.startswith("#"):
            frag = href_raw[1:].strip()
            if not frag:
                try:
                    del a["href"]
                except Exception:
                    a["href"] = None
                removed += 1
                if logger and logger.debug_enabled and len(debug_samples) < 10:
                    debug_samples.append("drop anchor '#' (empty fragment)")
                continue
            actual = id_map.get(frag.lower())
            if actual:
                # Normalize casing
                if actual != frag:
                    a["href"] = f"#{actual}"
                    rewritten += 1
                    if logger and logger.debug_enabled and len(debug_samples) < 10:
                        debug_samples.append(f"rewrite '#{frag}' -> '#{actual}'")
                else:
                    kept_anchor += 1
                continue

            # Unknown fragment → drop href
            try:
                del a["href"]
            except Exception:
                a["href"] = None
            removed += 1
            if logger and logger.debug_enabled and len(debug_samples) < 10:
                debug_samples.append(f"drop unknown in-doc anchor '#{frag}'")
            continue

        parsed = urlparse(href_raw)
        scheme = (parsed.scheme or "").lower()

        # External link with explicit scheme
        if scheme in ALLOWED_EXTERNAL_LINK_SCHEMES:
            kept_external += 1
            continue

        # Attempt to rewrite any URL-with-fragment to a local in-doc anchor
        _, frag = urldefrag(href_raw)
        frag = (frag or "").strip()
        if frag:
            actual = id_map.get(frag.lower())
            if actual:
                a["href"] = f"#{actual}"
                rewritten += 1
                if logger and logger.debug_enabled and len(debug_samples) < 10:
                    debug_samples.append(f"rewrite '{href_raw}' -> '#{actual}'")
                continue
            try:
                del a["href"]
            except Exception:
                a["href"] = None
            removed += 1
            if logger and logger.debug_enabled and len(debug_samples) < 10:
                debug_samples.append(f"drop unresolved fragment '{href_raw}'")
            continue

        # No fragment and not an allowed external scheme → drop href
        try:
            del a["href"]
        except Exception:
            a["href"] = None
        removed += 1
        if logger and logger.debug_enabled and len(debug_samples) < 10:
            debug_samples.append(f"drop disallowed href '{href_raw}'")

    if logger:
        logger.verbose(
            f"[verbose] normalize_document_links: links={total}, kept_external={kept_external}, kept_anchor={kept_anchor}, rewritten={rewritten}, removed={removed}"
        )
        if logger.debug_enabled and debug_samples:
            logger.debug(
                "[debug] normalize_document_links samples: "
                + "; ".join(debug_samples[:10])
            )


def build_toc_html(
    toc_items: List[TocNode],
    document_filename: str = "document.html",
    target_frame: str = "doc",
) -> str:
    """
    @brief Execute `build_toc_html`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param toc_items Input argument for `build_toc_html`.
    @param document_filename Input argument for `build_toc_html`.
    @param target_frame Input argument for `build_toc_html`.
    @return str Return value of `build_toc_html`.
    """
    def resolved_href(href: str) -> str:
        """
        @brief Execute `resolved_href`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param href Input argument for `resolved_href`.
        @return str Return value of `resolved_href`.
        """
        href = (href or "").strip()
        _, frag = urldefrag(href)
        if frag:
            return f"{document_filename}#{frag}"
        if href.startswith("#"):
            return f"{document_filename}{href}"
        return document_filename

    def render_nodes(nodes: List[TocNode]) -> str:
        """
        @brief Execute `render_nodes`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `render_nodes`.
        @return str Return value of `render_nodes`.
        """
        if not nodes:
            return ""
        items = []
        for n in nodes:
            href = resolved_href(n.href)
            children_html = render_nodes(n.children)
            items.append(
                f'<li><a target="{escape_html(target_frame)}" href="{href}">{escape_html(n.title)}</a>{children_html}</li>'
            )
        return f"<ul>{''.join(items)}</ul>"

    toc_html = render_nodes(toc_items)

    return f"""<!doctype html>
<html lang="it">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <title>TOC</title>
    <style>
        body {{ font-family: sans-serif; margin: 1rem; }}
        h1 {{ margin-top: 0; font-size: 1.4rem; }}
    </style>
</head>
<body>
    <h1>TOC</h1>
    {toc_html}
</body>
</html>
"""


def build_frameset_index(
    toc_filename: str = "toc.html", document_filename: str = "document.html"
) -> str:
    """
    @brief Execute `build_frameset_index`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param toc_filename Input argument for `build_frameset_index`.
    @param document_filename Input argument for `build_frameset_index`.
    @return str Return value of `build_frameset_index`.
    """
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Indice e documento</title>
</head>
<frameset cols="28%,*">
  <frame src="{toc_filename}" name="toc" />
  <frame src="{document_filename}" name="doc" />
  <noframes>
    <body>
      <p>Il browser non supporta i frame. Apri <a href="{toc_filename}">toc</a> e <a href="{document_filename}">documento</a>.</p>
    </body>
  </noframes>
</frameset>
</html>
"""


def minimal_readable_wrapper(
    inner_html: str, title: str = "Documento (offline)"
) -> str:
    """
    @brief Execute `minimal_readable_wrapper`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param inner_html Input argument for `minimal_readable_wrapper`.
    @param title Input argument for `minimal_readable_wrapper`.
    @return str Return value of `minimal_readable_wrapper`.
    """
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{escape_html(title)}</title>
</head>
<body>
{inner_html}
</body>
</html>
"""


# ----------------------------
# Downloader framework
# ----------------------------


class BaseDownloader:
    """
    @brief Define class `BaseDownloader`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    name: str = "base"

    def __init__(
        self,
        from_url: str,
        out_dir: Path,
        session: requests.Session,
        logger: Optional[Logger] = None,
        limit: Optional[int] = None,
        toc_only: bool = False,
        disable_numbering: bool = False,
    ):
        """
        @brief Execute `__init__`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `__init__`.
        @param from_url Input argument for `__init__`.
        @param out_dir Input argument for `__init__`.
        @param session Input argument for `__init__`.
        @param logger Input argument for `__init__`.
        @param limit Input argument for `__init__`.
        @param toc_only Input argument for `__init__`.
        @param disable_numbering Input argument for `__init__`.
        @return Any Return value of `__init__`.
        """
        self.from_url = from_url
        self.out_dir = out_dir
        self.session = session
        self.log = logger or Logger()
        self.limit = limit
        self.toc_only = toc_only
        self.disable_numbering = disable_numbering
        self.post_process_pipeline = [
            self._clean_document_style,
            self._add_document_style,
            self._normalize_document_links,
            self._remove_unused_images,
            self._remove_unused_assets,
            self._normalize_image_position,
            self._clean_assets_tree,
            self._remove_empty_assets_root,
            self._verify_toc_consistency,
            self._verify_toc_depth,
            self._prune_toc_and_clean_headings,
            self._enforce_toc_headings,
            self._test_toc_headings,
            self.fix_heading_ref_position,
            self._enforce_toc_headings,
            self._deduplicate_toc_entries,
            self._enforce_toc_headings,
            self.fix_heading_numbering,
            self._test_toc_headings,
        ]

    @classmethod
    def matches_url(cls, url: str) -> bool:
        """
        @brief Execute `matches_url`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param cls Input argument for `matches_url`.
        @param url Input argument for `matches_url`.
        @return bool Return value of `matches_url`.
        """
        return False

    @classmethod
    def probe_html(cls, url: str, html: str) -> bool:
        """
        @brief Execute `probe_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param cls Input argument for `probe_html`.
        @param url Input argument for `probe_html`.
        @param html Input argument for `probe_html`.
        @return bool Return value of `probe_html`.
        """
        return False

    def run(self) -> None:
        """
        @brief Execute `run`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `run`.
        @return None Return value of `run`.
        """
        raise NotImplementedError

    def _toc_tree_from_html(self, toc_html: str) -> List[TocNode]:
        """
        @brief Execute `_toc_tree_from_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_toc_tree_from_html`.
        @param toc_html Input argument for `_toc_tree_from_html`.
        @return List[TocNode] Return value of `_toc_tree_from_html`.
        """
        return toc_from_nav_html(toc_html, self.from_url)

    def post_process(self) -> None:
        """
        @brief Execute `post_process`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `post_process`.
        @return None Return value of `post_process`.
        """
        for func in self.post_process_pipeline:
            try:
                func()
            except Exception as e:
                self.log.debug(f"[debug] Post-process {func.__name__} failed: {e}")
                if func.__name__ == "_test_toc_headings":
                    raise

    def _verify_toc_consistency(self) -> None:
        """
        @brief Execute `_verify_toc_consistency`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_verify_toc_consistency`.
        @return None Return value of `_verify_toc_consistency`.
        """
        toc_path = self.out_dir / "toc.html"
        doc_path = self.out_dir / "document.html"
        if not toc_path.exists() or not doc_path.exists():
            return

        toc_soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")
        doc_soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")

        # Find all links in TOC
        toc_links = toc_soup.find_all("a", href=True)
        issues = []

        for link in toc_links:
            href = link.get("href", "").strip()
            if not href:
                continue
            _, frag = urldefrag(href)
            anchor_id = (frag or "").strip()
            if not anchor_id:
                continue
            link_text = " ".join(link.get_text(" ", strip=True).split())

            # Find corresponding element in document.html
            target = doc_soup.find(id=anchor_id)
            if not target:
                issues.append(
                    f"Missing anchor '{anchor_id}' for TOC link '{link_text}'"
                )
                continue

            # Check if it's a heading and text matches
            if target.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                heading_text = " ".join(target.get_text(" ", strip=True).split())
                if link_text.lower() != heading_text.lower():
                    issues.append(
                        f"TOC text '{link_text}' does not match heading '{heading_text}' for anchor '{anchor_id}'"
                    )

        if issues:
            self.log.verbose("[verbose] TOC consistency issues found:")
            for issue in issues:
                self.log.verbose(f"  - {issue}")
        else:
            self.log.check("[check] TOC consistency verified")

    def _verify_toc_depth(self) -> None:
        """
        @brief Execute `_verify_toc_depth`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_verify_toc_depth`.
        @return None Return value of `_verify_toc_depth`.
        """
        toc_path = self.out_dir / "toc.html"
        if not toc_path.exists():
            return

        toc_soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")

        def get_max_depth(ul, current_depth=0):
            """
            @brief Execute `get_max_depth`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param ul Input argument for `get_max_depth`.
            @param current_depth Input argument for `get_max_depth`.
            @return Any Return value of `get_max_depth`.
            """
            if not ul:
                return current_depth
            max_d = current_depth
            for li in ul.find_all("li", recursive=False):
                child_ul = li.find("ul", recursive=False)
                if child_ul:
                    max_d = max(max_d, get_max_depth(child_ul, current_depth + 1))
            return max_d

        root_ul = toc_soup.find("ul")
        max_depth = get_max_depth(root_ul, 1) if root_ul else 0

        if max_depth > 6:
            self.log.info(
                f"[warning] TOC depth is {max_depth} levels, which exceeds the recommended maximum of 6"
            )
        else:
            self.log.check(f"[check] TOC depth is {max_depth} levels (within limit)")

    def _prune_toc_and_clean_headings(self) -> None:
        """
        @brief Execute `_prune_toc_and_clean_headings`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_prune_toc_and_clean_headings`.
        @return None Return value of `_prune_toc_and_clean_headings`.
        """
        import re

        heading_prefix_re = re.compile(r"^\d+(\.\d+)*\s+")

        def href_fragment_id(href: str) -> str:
            """
            @brief Execute `href_fragment_id`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param href Input argument for `href_fragment_id`.
            @return str Return value of `href_fragment_id`.
            """
            href = (href or "").strip()
            if not href:
                return ""
            _, frag = urldefrag(href)
            return (frag or "").strip()

        pruned_ids: Set[str] = set()
        # Process toc.html
        toc_path = self.out_dir / "toc.html"
        if toc_path.exists():
            toc_soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")

            # Prune TOC at depth >=7
            root_ul = toc_soup.find("ul")
            if root_ul:

                def prune_ul(ul, depth):
                    """
                    @brief Execute `prune_ul`.
                    @details Implements deterministic control flow as defined by module runtime semantics.
                    @param ul Input argument for `prune_ul`.
                    @param depth Input argument for `prune_ul`.
                    @return Any Return value of `prune_ul`.
                    """
                    for li in list(ul.find_all("li", recursive=False)):
                        if depth >= 7:
                            a = li.find("a", href=True)
                            if a:
                                frag = href_fragment_id(a.get("href") or "")
                                if frag:
                                    pruned_ids.add(frag.lower())
                            li.decompose()
                            continue
                        child_ul = li.find("ul", recursive=False)
                        if child_ul:
                            prune_ul(child_ul, depth + 1)

                prune_ul(root_ul, 1)  # root ul depth 1, li depth 2

            # Clean heading prefixes from TOC links
            for a in toc_soup.find_all("a"):
                if a.string:
                    a.string = heading_prefix_re.sub("", a.string)

            toc_path.write_text(str(toc_soup), encoding="utf-8")

        # Process document.html
        doc_path = self.out_dir / "document.html"
        if doc_path.exists():
            doc_soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")

            # Clean heading prefixes from headings
            for h in doc_soup.find_all(re.compile(r"^h[1-7]$")):
                if h.string:
                    h.string = heading_prefix_re.sub("", h.string)

            # If we pruned deep TOC entries, demote their corresponding headings in document.html.
            # A heading is associated to a pruned TOC entry if:
            # - the heading id is referenced by a pruned TOC href, OR
            # - the heading is contained in a div/section whose id is referenced by a pruned TOC href.
            if pruned_ids:
                for h in list(doc_soup.find_all(re.compile(r"^h[1-6]$"))):
                    hid = (h.get("id") or "").strip()
                    hid_l = hid.lower() if hid else ""
                    container_id_l = ""
                    for parent in h.parents:
                        if getattr(parent, "name", None) in ("section", "div"):
                            pid = (parent.get("id") or "").strip()
                            if pid:
                                pid_l = pid.lower()
                                if pid_l in pruned_ids:
                                    container_id_l = pid_l
                                    break

                    if (hid_l and hid_l in pruned_ids) or container_id_l:
                        text = h.get_text(" ", strip=True).upper()
                        new_tag = doc_soup.new_tag("strong")
                        new_tag.string = text
                        if hid:
                            new_tag["id"] = hid
                        h.replace_with(new_tag)

            doc_path.write_text(str(doc_soup), encoding="utf-8")

    def _deduplicate_toc_entries(self) -> None:
        """
        @brief Execute `_deduplicate_toc_entries`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_deduplicate_toc_entries`.
        @return None Return value of `_deduplicate_toc_entries`.
        """
        toc_path = self.out_dir / "toc.html"
        if not toc_path.exists():
            return

        toc_soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")

        def href_fragment_id(href: str) -> str:
            """
            @brief Execute `href_fragment_id`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param href Input argument for `href_fragment_id`.
            @return str Return value of `href_fragment_id`.
            """
            href = (href or "").strip()
            if not href:
                return ""
            _, frag = urldefrag(href)
            return (frag or "").strip().lower()

        root_ul = toc_soup.find("ul")
        if not root_ul:
            return

        # Use TocNode representation for safer manipulation: parse TOC to TocNode
        # objects, process them in reading order and rebuild HTML from nodes.
        def process_nodes(nodes: List[TocNode], seen: Set[str]) -> List[TocNode]:
            """
            @brief Execute `process_nodes`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param nodes Input argument for `process_nodes`.
            @param seen Input argument for `process_nodes`.
            @return List[TocNode] Return value of `process_nodes`.
            """
            out: List[TocNode] = []
            for n in nodes:
                href = (n.href or "").strip()
                _, frag = urldefrag(href)
                frag_norm = (frag or "").strip().lower()

                if frag_norm and frag_norm in seen:
                    # promote children: process children and extend at this level
                    promoted = process_nodes(n.children, seen)
                    out.extend(promoted)
                    continue

                if frag_norm:
                    seen.add(frag_norm)

                # process children recursively
                n.children = process_nodes(n.children, seen)
                out.append(n)

            return out

        # Build TocNode list from the captured TOC HTML and process with the
        # TocNode-based algorithm, then rebuild the TOC HTML deterministically.
        toc_html_orig = str(toc_soup)
        toc_nodes = self._toc_tree_from_html(toc_html_orig)
        processed_nodes = process_nodes(toc_nodes, set())
        new_toc_html = build_toc_html(processed_nodes)
        toc_path.write_text(new_toc_html, encoding="utf-8")

    def _enforce_toc_headings(self) -> None:
        """
        @brief Execute `_enforce_toc_headings`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_enforce_toc_headings`.
        @return None Return value of `_enforce_toc_headings`.
        """
        toc_path = self.out_dir / "toc.html"
        doc_path = self.out_dir / "document.html"
        if not toc_path.exists() or not doc_path.exists():
            return

        toc_soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")
        doc_soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")

        def href_fragment_id(href: str) -> str:
            """
            @brief Execute `href_fragment_id`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param href Input argument for `href_fragment_id`.
            @return str Return value of `href_fragment_id`.
            """
            href = (href or "").strip()
            if not href:
                return ""
            _, frag = urldefrag(href)
            return (frag or "").strip()

        # Map fragment id -> toc depth (depth = number of UL ancestors)
        referenced_depth: Dict[str, int] = {}
        for a in toc_soup.select("ul a[href]"):
            frag = href_fragment_id(a.get("href") or "")
            if not frag:
                continue
            depth = len(a.find_parents("ul"))
            frag_l = frag.lower()
            if frag_l not in referenced_depth:
                referenced_depth[frag_l] = depth

        def clamp_heading_level(depth: int) -> int:
            """
            @brief Execute `clamp_heading_level`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param depth Input argument for `clamp_heading_level`.
            @return int Return value of `clamp_heading_level`.
            """
            try:
                depth_i = int(depth)
            except Exception:
                depth_i = 1
            if depth_i < 1:
                return 1
            if depth_i > 6:
                return 6
            return depth_i

        def find_referenced_container_id(h) -> str:
            """
            @brief Execute `find_referenced_container_id`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param h Input argument for `find_referenced_container_id`.
            @return str Return value of `find_referenced_container_id`.
            """
            for parent in h.parents:
                if getattr(parent, "name", None) not in ("section", "div"):
                    continue
                pid = (parent.get("id") or "").strip()
                if not pid:
                    continue
                pid_l = pid.lower()
                if pid_l in referenced_depth:
                    return pid_l
            return ""

        # Process headings in document.html
        for h in list(doc_soup.find_all(re.compile(r"^h[1-6]$"))):
            hid = (h.get("id") or "").strip()
            hid_l = hid.lower() if hid else ""

            expected_depth = None
            referenced_by = ""

            if hid_l and hid_l in referenced_depth:
                expected_depth = referenced_depth[hid_l]
                referenced_by = "id"
            else:
                container_id_l = find_referenced_container_id(h)
                if container_id_l:
                    expected_depth = referenced_depth[container_id_l]
                    referenced_by = "container"

            if expected_depth is None:
                # Not referenced: convert to bold uppercase non-heading
                text = h.get_text(" ", strip=True).upper()
                new_tag = doc_soup.new_tag("strong")
                new_tag.string = text
                if hid:
                    new_tag["id"] = hid
                h.replace_with(new_tag)
                continue

            # Referenced: correct heading level based on TOC depth.
            # For container-based references, correct only the first heading inside that container
            # to avoid flattening internal structure.
            if referenced_by == "container":
                container = h.find_parent(["section", "div"], id=True)
                if container:
                    first_h = container.find(re.compile(r"^h[1-6]$"))
                    if first_h is not h:
                        continue

            expected_level = clamp_heading_level(expected_depth)
            expected_name = f"h{expected_level}"
            if h.name != expected_name:
                h.name = expected_name

        # Write back document.html
        doc_path.write_text(str(doc_soup), encoding="utf-8")

    def _test_toc_headings(self) -> None:
        """
        @brief Execute `_test_toc_headings`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_test_toc_headings`.
        @return None Return value of `_test_toc_headings`.
        """
        toc_path = self.out_dir / "toc.html"
        doc_path = self.out_dir / "document.html"
        if not toc_path.exists() or not doc_path.exists():
            return

        self.log.verbose("[verbose] test_toc_headings: avvio controlli TOC↔heading")
        toc_soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")
        doc_soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")

        def href_fragment_id(href: str) -> str:
            """
            @brief Execute `href_fragment_id`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param href Input argument for `href_fragment_id`.
            @return str Return value of `href_fragment_id`.
            """
            href = (href or "").strip()
            if not href:
                return ""
            _, frag = urldefrag(href)
            return (frag or "").strip()

        def clamp_heading_level(depth: int) -> int:
            """
            @brief Execute `clamp_heading_level`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param depth Input argument for `clamp_heading_level`.
            @return int Return value of `clamp_heading_level`.
            """
            try:
                value = int(depth)
            except Exception:
                value = 1
            return max(1, min(6, value))

        referenced_depth: Dict[str, int] = {}
        for a in toc_soup.select("ul a[href]"):
            frag = href_fragment_id(a.get("href") or "")
            if not frag:
                continue
            depth = len(a.find_parents("ul"))
            frag_l = frag.lower()
            if frag_l not in referenced_depth:
                referenced_depth[frag_l] = depth

        if not referenced_depth:
            self.log.verbose(
                "[verbose] test_toc_headings: nessun href con frammento trovato, controllo saltato"
            )
            return

        doc_by_id: Dict[str, Any] = {}
        for el in doc_soup.find_all(True):
            el_id = (el.get("id") or "").strip()
            if el_id:
                doc_by_id.setdefault(el_id.lower(), el)

        self.log.verbose(
            f"[verbose] test_toc_headings: verifico {len(referenced_depth)} href presenti nella TOC"
        )

        missing_targets: List[str] = []
        invalid_targets: List[str] = []
        depth_mismatch: List[str] = []

        for frag, depth in referenced_depth.items():
            target = doc_by_id.get(frag)
            if not target:
                missing_targets.append(frag)
                continue

            expected_level = clamp_heading_level(depth)
            tag_name = (getattr(target, "name", "") or "").lower()

            if HEADING_TAG_RE.match(tag_name):
                level = int(tag_name[1])
                if level != expected_level:
                    depth_mismatch.append(
                        f"{frag} atteso h{expected_level} trovato {tag_name}"
                    )
                else:
                    self.log.debug(
                        f"[debug] test_toc_headings: '{frag}' referenziato tramite heading id (h{level})"
                    )
                continue

            if tag_name in ("div", "section"):
                heading = target.find(HEADING_TAG_RE)
                if not heading:
                    invalid_targets.append(f"{frag} (contenitore senza heading)")
                    continue
                level = int(heading.name[1])
                if level != expected_level:
                    depth_mismatch.append(
                        f"{frag} atteso h{expected_level} trovato {heading.name}"
                    )
                else:
                    self.log.debug(
                        f"[debug] test_toc_headings: '{frag}' referenziato tramite contenitore → {heading.name}"
                    )
                continue

            invalid_targets.append(f"{frag} (tag={tag_name or 'unknown'})")

        referenced_fragments = set(referenced_depth.keys())
        total_headings = 0
        referenced_headings = 0
        unreferenced_headings: List[str] = []

        self.log.verbose(
            "[verbose] test_toc_headings: controllo copertura heading in document.html"
        )

        for heading in doc_soup.find_all(HEADING_TAG_RE):
            total_headings += 1
            hid = (heading.get("id") or "").strip()
            hid_l = hid.lower() if hid else ""
            referenced = False

            if hid_l and hid_l in referenced_fragments:
                referenced = True
                referenced_headings += 1
                self.log.debug(
                    f"[debug] test_toc_headings: heading {heading.name}#{hid or '<no-id>'} referenziato tramite id"
                )
            else:
                for parent in heading.parents:
                    pname = (getattr(parent, "name", "") or "").lower()
                    if pname not in ("div", "section"):
                        continue
                    pid = (parent.get("id") or "").strip()
                    if not pid:
                        continue
                    pid_l = pid.lower()
                    if pid_l in referenced_fragments:
                        referenced = True
                        referenced_headings += 1
                        self.log.debug(
                            f"[debug] test_toc_headings: heading {heading.name}#{hid or '<no-id>'} referenziato tramite contenitore {pid}"
                        )
                        break

            if not referenced:
                title = " ".join(heading.get_text(" ", strip=True).split())
                unreferenced_headings.append(
                    f"{heading.name}#{hid or '<no-id>'} {title or '<senza testo>'}"
                )

        self.log.verbose(
            f"[verbose] test_toc_headings: heading referenziati {referenced_headings}/{total_headings}"
        )

        def summarize(items: List[str]) -> str:
            """
            @brief Execute `summarize`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param items Input argument for `summarize`.
            @return str Return value of `summarize`.
            """
            if not items:
                return ""
            preview = ", ".join(items[:5])
            if len(items) > 5:
                preview += ", ..."
            return preview

        issues: List[str] = []
        if missing_targets:
            issues.append(
                f"missing anchors ({len(missing_targets)}): {summarize(missing_targets)}"
            )
        if invalid_targets:
            issues.append(
                f"invalid targets ({len(invalid_targets)}): {summarize(invalid_targets)}"
            )
        if depth_mismatch:
            issues.append(
                f"depth mismatch ({len(depth_mismatch)}): {summarize(depth_mismatch)}"
            )
        if unreferenced_headings:
            issues.append(
                f"unreferenced headings ({len(unreferenced_headings)}): {summarize(unreferenced_headings)}"
            )

        if issues:
            raise ValueError("test_toc_headings: " + "; ".join(issues))

        self.log.check("[check] test_toc_headings completato")

    def fix_heading_ref_position(self) -> None:
        """
        @brief Execute `fix_heading_ref_position`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `fix_heading_ref_position`.
        @return None Return value of `fix_heading_ref_position`.
        """

        toc_path = self.out_dir / "toc.html"
        doc_path = self.out_dir / "document.html"
        if not toc_path.exists() or not doc_path.exists():
            return

        toc_soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")
        doc_soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")

        toc_fragments: List[str] = []
        toc_fragments_l: Set[str] = set()
        for a in toc_soup.find_all("a", href=True):
            href = (a.get("href") or "").strip()
            _, frag = urldefrag(href)
            frag = (frag or "").strip()
            if not frag:
                continue
            frag_l = frag.lower()
            if frag_l in toc_fragments_l:
                continue
            toc_fragments_l.add(frag_l)
            toc_fragments.append(frag)

        if not toc_fragments:
            self.log.verbose(
                "[verbose] fix_heading_ref_position: nessun href con frammento trovato, controllo saltato"
            )
            return

        # Build an index of ids in the document (case-insensitive).
        doc_by_id: Dict[str, List[Any]] = {}
        for el in doc_soup.find_all(True):
            el_id = (el.get("id") or "").strip()
            if not el_id:
                continue
            doc_by_id.setdefault(el_id.lower(), []).append(el)

        self.log.verbose(
            f"[verbose] fix_heading_ref_position: verifico {len(toc_fragments)} frammenti della TOC"
        )

        moved: List[str] = []
        missing: List[str] = []
        invalid: List[str] = []
        conflicts: List[str] = []

        for frag in toc_fragments:
            frag_l = frag.lower()
            targets = doc_by_id.get(frag_l) or []
            if not targets:
                missing.append(frag)
                continue

            target = targets[0]
            tag_name = (getattr(target, "name", "") or "").lower()

            if HEADING_TAG_RE.match(tag_name):
                continue

            heading = None
            if hasattr(target, "find"):
                heading = target.find(HEADING_TAG_RE)
            if not heading:
                invalid.append(f"{frag} (tag={tag_name or 'unknown'} senza heading)")
                continue

            old_heading_id = (heading.get("id") or "").strip()
            if old_heading_id and old_heading_id.lower() in toc_fragments_l and old_heading_id.lower() != frag_l:
                conflicts.append(
                    f"{frag} (heading interno ha gia' id referenziato dalla TOC: {old_heading_id})"
                )
                continue

            # Remove id from the container and assign the TOC fragment id to the heading.
            if hasattr(target, "attrs") and target.get("id") is not None:
                try:
                    del target["id"]
                except Exception:
                    target["id"] = None

            if old_heading_id and old_heading_id != frag:
                # Try to preserve the old heading id by moving it to the container,
                # but only if it does not collide with another element.
                other_els = [e for e in doc_soup.find_all(id=old_heading_id) if e is not heading]
                if not other_els:
                    try:
                        target["id"] = old_heading_id
                    except Exception:
                        pass

            heading["id"] = frag
            moved.append(frag)

        # Re-index after modifications and ensure all TOC href fragments point to headings.
        if moved:
            doc_by_id2: Dict[str, Any] = {}
            for el in doc_soup.find_all(True):
                el_id = (el.get("id") or "").strip()
                if el_id:
                    doc_by_id2.setdefault(el_id.lower(), el)

            not_headings: List[str] = []
            for frag in toc_fragments:
                t = doc_by_id2.get(frag.lower())
                name = (getattr(t, "name", "") or "").lower() if t else ""
                if not t or not HEADING_TAG_RE.match(name):
                    not_headings.append(frag)

            if not_headings:
                invalid.extend([f"{f} (non punta a heading dopo fix)" for f in not_headings])

            doc_path.write_text(str(doc_soup), encoding="utf-8")

        if moved:
            self.log.verbose(
                f"[verbose] fix_heading_ref_position: spostati {len(moved)} id dalla sezione al heading"
            )
            self.log.debug(
                f"[debug] fix_heading_ref_position: spostati: {', '.join(moved[:8])}{', ...' if len(moved) > 8 else ''}"
            )

        issues: List[str] = []
        if missing:
            issues.append(f"missing anchors ({len(missing)}): {', '.join(missing[:5])}{', ...' if len(missing) > 5 else ''}")
        if conflicts:
            issues.append(f"conflicts ({len(conflicts)}): {conflicts[0]}{', ...' if len(conflicts) > 1 else ''}")
        if invalid:
            issues.append(f"invalid targets ({len(invalid)}): {invalid[0]}{', ...' if len(invalid) > 1 else ''}")

        if issues:
            raise ValueError("fix_heading_ref_position: " + "; ".join(issues))

        self.log.check("[check] fix_heading_ref_position completato")

    def fix_heading_numbering(self) -> None:
        """
        @brief Execute `fix_heading_numbering`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `fix_heading_numbering`.
        @return None Return value of `fix_heading_numbering`.
        """

        import re
        from bs4 import NavigableString  # pyright: ignore[reportMissingImports]

        toc_path = self.out_dir / "toc.html"
        doc_path = self.out_dir / "document.html"
        if not toc_path.exists() or not doc_path.exists():
            return

        # Matches: "1 ", "1.", "1.2 ", "1.2.", "1.2.3 ", "1.2.3.", ...
        numbering_prefix_re = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+")

        def normalize_ws(text: str) -> str:
            """
            @brief Execute `normalize_ws`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param text Input argument for `normalize_ws`.
            @return str Return value of `normalize_ws`.
            """
            return " ".join((text or "").split())

        def strip_numbering_prefix(text: str) -> str:
            """
            @brief Execute `strip_numbering_prefix`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param text Input argument for `strip_numbering_prefix`.
            @return str Return value of `strip_numbering_prefix`.
            """
            return normalize_ws(numbering_prefix_re.sub("", normalize_ws(text)))

        def set_flat_text(tag, text: str) -> None:
            """
            @brief Execute `set_flat_text`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param tag Input argument for `set_flat_text`.
            @param text Input argument for `set_flat_text`.
            @return None Return value of `set_flat_text`.
            """
            tag.clear()
            tag.append(NavigableString(text))

        toc_soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")
        doc_soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")

        # Phase 1: remove existing numbering from all TOC link texts
        toc_links = list(toc_soup.select("ul a[href]"))
        for a in toc_links:
            cleaned = strip_numbering_prefix(a.get_text(" ", strip=True))
            set_flat_text(a, cleaned)

        # Phase 1: remove existing numbering from all headings in the document
        for h in doc_soup.find_all(re.compile(r"^h[1-6]$")):
            cleaned = strip_numbering_prefix(h.get_text(" ", strip=True))
            set_flat_text(h, cleaned)

        if self.disable_numbering:
            toc_path.write_text(str(toc_soup), encoding="utf-8")
            doc_path.write_text(str(doc_soup), encoding="utf-8")
            self.log.check("[check] fix_heading_numbering completato (aggiunta numbering disabilitata)")
            return

        # Build numbering from TOC structure (depth inferred from UL nesting)
        def href_fragment_id(href: str) -> str:
            """
            @brief Execute `href_fragment_id`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param href Input argument for `href_fragment_id`.
            @return str Return value of `href_fragment_id`.
            """
            href = (href or "").strip()
            if not href:
                return ""
            _, frag = urldefrag(href)
            return (frag or "").strip()

        counters: List[int] = []
        numbering_by_frag: Dict[str, str] = {}
        title_by_frag: Dict[str, str] = {}

        for a in toc_links:
            frag = href_fragment_id(a.get("href") or "")
            if not frag:
                continue
            depth = len(a.find_parents("ul"))
            if depth < 1:
                depth = 1

            # Maintain counters per depth
            if len(counters) < depth:
                counters.extend([0] * (depth - len(counters)))
            elif len(counters) > depth:
                counters = counters[:depth]

            counters[depth - 1] += 1
            for i in range(depth, len(counters)):
                counters[i] = 0

            number = ".".join(str(c) for c in counters[:depth] if c)
            title_clean = strip_numbering_prefix(a.get_text(" ", strip=True))
            numbered_title = f"{number} {title_clean}" if title_clean else number

            frag_l = frag.lower()
            numbering_by_frag[frag_l] = number
            title_by_frag[frag_l] = title_clean
            set_flat_text(a, numbered_title)

        # Apply numbering to corresponding headings (by fragment id)
        doc_by_id: Dict[str, Any] = {}
        for el in doc_soup.find_all(True):
            el_id = (el.get("id") or "").strip()
            if el_id:
                doc_by_id.setdefault(el_id.lower(), el)

        for frag_l, number in numbering_by_frag.items():
            target = doc_by_id.get(frag_l)
            if not target:
                continue
            tag_name = (getattr(target, "name", "") or "").lower()
            heading = target if HEADING_TAG_RE.match(tag_name) else None
            if heading is None and hasattr(target, "find"):
                heading = target.find(HEADING_TAG_RE)
            if not heading:
                continue

            title_clean = title_by_frag.get(frag_l, strip_numbering_prefix(heading.get_text(" ", strip=True)))
            numbered_title = f"{number} {title_clean}" if title_clean else number
            set_flat_text(heading, numbered_title)

        toc_path.write_text(str(toc_soup), encoding="utf-8")
        doc_path.write_text(str(doc_soup), encoding="utf-8")
        self.log.check("[check] fix_heading_numbering completato")

    def _clean_document_style(self) -> None:
        """
        @brief Execute `_clean_document_style`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_clean_document_style`.
        @return None Return value of `_clean_document_style`.
        """
        # Process document.html
        doc_path = self.out_dir / "document.html"
        if doc_path.exists():
            soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")
            strip_styles(soup)
            doc_path.write_text(str(soup), encoding="utf-8")

        # Process toc.html
        toc_path = self.out_dir / "toc.html"
        if toc_path.exists():
            soup = BeautifulSoup(toc_path.read_text(encoding="utf-8"), "lxml")
            strip_styles(soup)
            toc_path.write_text(str(soup), encoding="utf-8")

    def _add_document_style(self) -> None:
        """
        @brief Execute `_add_document_style`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_add_document_style`.
        @return None Return value of `_add_document_style`.
        """
        doc_path = self.out_dir / "document.html"
        if not doc_path.exists():
            return

        soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")

        # Check if there are any tables or images in the document
        tables = soup.find_all("table")
        images = soup.find_all("img")
        if not tables and not images:
            return

        # Create or find the head element
        head = soup.find("head")
        if not head:
            html_tag = soup.find("html")
            if html_tag:
                head = soup.new_tag("head")
                html_tag.insert(0, head)
            else:
                return

        # Create style tag with table border CSS and image border CSS
        style_tag = soup.new_tag("style")
        style_tag.string = """
table {
    border-collapse: collapse;
}
table, th, td {
    border: 1px solid black;
}
img:not(table img) {
    border: 1px solid black;
}
"""
        head.append(style_tag)

        doc_path.write_text(str(soup), encoding="utf-8")

    def _normalize_document_links(self) -> None:
        """
        @brief Execute `_normalize_document_links`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_normalize_document_links`.
        @return None Return value of `_normalize_document_links`.
        """
        doc_path = self.out_dir / "document.html"
        if not doc_path.exists():
            return

        soup = BeautifulSoup(doc_path.read_text(encoding="utf-8"), "lxml")
        normalize_document_links_inplace(soup, self.log)
        doc_path.write_text(str(soup), encoding="utf-8")

    def _remove_unused_images(self) -> None:
        """
        @brief Execute `_remove_unused_images`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_remove_unused_images`.
        @return None Return value of `_remove_unused_images`.
        """
        assets_dir = self.out_dir / "assets"
        if not assets_dir.exists() or not assets_dir.is_dir():
            return

        # Read HTML contents to search references
        contents = ""
        for fn in ("document.html", "toc.html", "index.html"):
            p = self.out_dir / fn
            if p.exists():
                try:
                    contents += p.read_text(encoding="utf-8")
                except Exception:
                    continue

        image_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}

        for f in sorted(assets_dir.rglob("*")):
            if not f.is_file():
                continue
            if f.suffix.lower() not in image_suffixes:
                continue

            try:
                rel = f.relative_to(self.out_dir).as_posix()
            except Exception:
                rel = f.name

            # If neither the relative path nor the basename appear in the HTML, delete
            if (rel not in contents) and (f.name not in contents):
                try:
                    f.unlink()
                    self.log.verbose(f"[verbose] Removed unused image: {rel}")
                except Exception as e:
                    self.log.debug(f"[debug] Failed to remove {rel}: {e}")

    def _remove_unused_assets(self) -> None:
        """
        @brief Execute `_remove_unused_assets`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_remove_unused_assets`.
        @return None Return value of `_remove_unused_assets`.
        """
        assets_dir = self.out_dir / "assets"
        if not assets_dir.exists() or not assets_dir.is_dir():
            return

        doc_path = self.out_dir / "document.html"
        contents = ""
        if doc_path.exists():
            try:
                contents = doc_path.read_text(encoding="utf-8")
            except Exception:
                contents = ""

        for f in sorted(assets_dir.rglob("*")):
            if not f.is_file():
                continue
            try:
                rel = f.relative_to(self.out_dir).as_posix()
            except Exception:
                rel = f.name

            # If neither the relative path nor the basename appear in document.html, delete
            if (rel not in contents) and (f.name not in contents):
                try:
                    f.unlink()
                    self.log.verbose(f"[verbose] Removed unused asset: {rel}")
                except Exception as e:
                    self.log.debug(f"[debug] Failed to remove {rel}: {e}")

    def _normalize_image_position(self) -> None:
        """
        @brief Execute `_normalize_image_position`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_normalize_image_position`.
        @return None Return value of `_normalize_image_position`.
        """
        assets_dir = self.out_dir / "assets"
        if not assets_dir.exists() or not assets_dir.is_dir():
            return

        doc_files = []
        for fn in ("document.html", "toc.html", "index.html"):
            p = self.out_dir / fn
            if p.exists():
                doc_files.append(p)

        # Collect image files under assets recursively
        for f in sorted(assets_dir.rglob("*")):
            if not f.is_file():
                continue
            # skip files already in the root of assets
            try:
                if f.parent.resolve() == assets_dir.resolve():
                    continue
            except Exception:
                pass

            stem = f.stem
            suf = f.suffix
            new_name = f"{stem}_{uuid.uuid4().hex}{suf}"
            target = assets_dir / new_name
            # ensure unique
            while target.exists():
                new_name = f"{stem}_{uuid.uuid4().hex}{suf}"
                target = assets_dir / new_name

            old_rel = f.relative_to(self.out_dir).as_posix()
            new_rel = target.relative_to(self.out_dir).as_posix()

            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                f.replace(target)
                self.log.verbose(f"[verbose] Moved image {old_rel} -> {new_rel}")
            except Exception as e:
                self.log.debug(f"[debug] Failed to move image {old_rel}: {e}")
                continue

            # Update references in HTML files
            for p in doc_files:
                try:
                    txt = p.read_text(encoding="utf-8")
                    if old_rel in txt or f.name in txt:
                        txt = txt.replace(old_rel, new_rel)
                        txt = txt.replace(f.name, new_name)
                        p.write_text(txt, encoding="utf-8")
                        self.log.debug(f"[debug] Updated refs in {p.name}: {old_rel} -> {new_rel}")
                except Exception:
                    continue

    def _clean_assets_tree(self) -> None:
        """
        @brief Execute `_clean_assets_tree`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_clean_assets_tree`.
        @return None Return value of `_clean_assets_tree`.
        """
        assets_dir = self.out_dir / "assets"
        if not assets_dir.exists() or not assets_dir.is_dir():
            return

        # Walk directories bottom-up and try to remove empty ones
        # Use sorted(reverse=True) to attempt children before parents
        dirs = [d for d in assets_dir.rglob("*") if d.is_dir()]
        for d in sorted(dirs, key=lambda p: len(str(p)), reverse=True):
            try:
                # rmdir only if empty
                d.rmdir()
                self.log.verbose(f"[verbose] Removed empty dir: {d.relative_to(self.out_dir).as_posix()}")
            except Exception:
                # not empty or cannot remove, ignore
                continue

    def _remove_empty_assets_root(self) -> None:
        """
        @brief Execute `_remove_empty_assets_root`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_remove_empty_assets_root`.
        @return None Return value of `_remove_empty_assets_root`.
        """
        assets_dir = self.out_dir / "assets"
        if not assets_dir.exists() or not assets_dir.is_dir():
            return

        # Check for any files or non-empty directories under assets/
        has_any = False
        for p in assets_dir.rglob("*"):
            # if any file exists, or any directory that contains something, mark
            # as non-empty
            if p.is_file():
                has_any = True
                break
            if p.is_dir():
                try:
                    # if dir contains any children, it's non-empty
                    if any(p.iterdir()):
                        has_any = True
                        break
                except Exception:
                    has_any = True
                    break

        if has_any:
            return

        try:
            assets_dir.rmdir()
            self.log.verbose(f"[verbose] Removed empty assets dir: {assets_dir.relative_to(self.out_dir).as_posix()}")
        except Exception as e:
            self.log.debug(f"[debug] Failed to remove assets dir {assets_dir}: {e}")


class DownloaderRegistry:
    """
    @brief Define class `DownloaderRegistry`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    def __init__(self):
        """
        @brief Execute `__init__`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `__init__`.
        @return Any Return value of `__init__`.
        """
        self._classes: List[type[BaseDownloader]] = []

    def register(self, downloader_cls: type[BaseDownloader]) -> None:
        """
        @brief Execute `register`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `register`.
        @param downloader_cls Input argument for `register`.
        @return None Return value of `register`.
        """
        self._classes.append(downloader_cls)

    def detect(self, url: str, session: requests.Session) -> type[BaseDownloader]:
        """
        @brief Execute `detect`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `detect`.
        @param url Input argument for `detect`.
        @param session Input argument for `detect`.
        @return type[BaseDownloader] Return value of `detect`.
        """
        url_matches = [c for c in self._classes if c.matches_url(url)]
        if len(url_matches) == 1:
            return url_matches[0]

        html = ""
        try:
            r = session.get(url, timeout=30, allow_redirects=True)
            r.raise_for_status()
            html = r.text[:2_000_000]
        except Exception:
            pass

        html_matches = [c for c in self._classes if html and c.probe_html(url, html)]
        if len(html_matches) == 1:
            return html_matches[0]

        if html_matches:
            return html_matches[0]
        if url_matches:
            return url_matches[0]
        raise RuntimeError(
            "Impossibile determinare il tipo di downloader per questa URL."
        )


# ----------------------------
# Document-viewer (TI) downloader
# ----------------------------


def guess_ext_from_content_type(ct: str) -> str:
    """
    @brief Execute `guess_ext_from_content_type`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param ct Input argument for `guess_ext_from_content_type`.
    @return str Return value of `guess_ext_from_content_type`.
    """
    ct = (ct or "").split(";")[0].strip().lower()
    if not ct:
        return ""
    ext = mimetypes.guess_extension(ct) or ""
    if ct in ("text/javascript", "application/javascript"):
        return ".js"
    if ct == "text/css":
        return ".css"
    if ct.startswith("image/") and not ext:
        return "." + ct.split("/", 1)[1]
    return ext


class NetworkImageRecorder:
    """
    @brief Define class `NetworkImageRecorder`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """

    def __init__(self, out_dir: Path):
        """
        @brief Execute `__init__`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `__init__`.
        @param out_dir Input argument for `__init__`.
        @return Any Return value of `__init__`.
        """
        self.out_dir = out_dir
        self.saved: Dict[str, Path] = {}
        self.failed: Set[str] = set()

    def attach(self, page):
        """
        @brief Execute `attach`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `attach`.
        @param page Input argument for `attach`.
        @return Any Return value of `attach`.
        """
        def on_response(resp):
            """
            @brief Execute `on_response`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param resp Input argument for `on_response`.
            @return Any Return value of `on_response`.
            """
            try:
                url = resp.url
                if not is_http_url(url):
                    return
                ct = (resp.headers.get("content-type") or "").lower()
                if not ct.startswith("image/"):
                    return
                if url in self.saved or url in self.failed:
                    return

                lp = local_path_for_url(url, self.out_dir)
                if not lp.suffix:
                    ext = guess_ext_from_content_type(ct)
                    if ext:
                        lp = lp.with_suffix(ext)

                ensure_parent(lp)
                body = resp.body()
                with open(lp, "wb") as f:
                    f.write(body)
                self.saved[url] = lp
            except Exception:
                try:
                    self.failed.add(resp.url)
                except Exception:
                    pass

        page.on("response", on_response)


class DocumentViewerDownloader(BaseDownloader):
    """
    @brief Define class `DocumentViewerDownloader`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    name = "document-viewer"

    TOC_SELECTORS = [
        "#viewer_navTree",
        "nav",
        "[role='navigation']",
        "aside",
        "#contents",
        ".contents",
        ".toc",
    ]
    CONTENT_SELECTORS = [
        "ti-library-viewer-content-area",  # TI's actual content area component
        ".viewer-content",  # Content area class
        ".content-area",  # Alternative content class
        "#loadContentArea",  # TI's content loading area
        ".cardWrapper",  # Card wrapper containing document sections
        "main:not(.viewer-sidebar)",
        "[role='main']:not(.viewer-sidebar)",
        "article",
        ".document",
        ".content:not(.tab-slider-content)",
        "#content",
    ]
    TOC_SCROLL_SELECTORS = [
        "nav",
        "[role='navigation']",
        "#contents",
        ".contents",
        ".toc",
    ]

    @classmethod
    def matches_url(cls, url: str) -> bool:
        """
        @brief Execute `matches_url`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param cls Input argument for `matches_url`.
        @param url Input argument for `matches_url`.
        @return bool Return value of `matches_url`.
        """
        u = urlparse(url)
        return ("ti.com" in u.netloc) and ("/document-viewer/" in u.path)

    @classmethod
    def probe_html(cls, url: str, html: str) -> bool:
        """
        @brief Execute `probe_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param cls Input argument for `probe_html`.
        @param url Input argument for `probe_html`.
        @param html Input argument for `probe_html`.
        @return bool Return value of `probe_html`.
        """
        h = html.lower()
        return "document-viewer" in h

    def _pick_best_outerhtml(self, page, selectors: List[str]) -> Optional[str]:
        """
        @brief Execute `_pick_best_outerhtml`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_pick_best_outerhtml`.
        @param page Input argument for `_pick_best_outerhtml`.
        @param selectors Input argument for `_pick_best_outerhtml`.
        @return Optional[str] Return value of `_pick_best_outerhtml`.
        """
        best = None
        best_score = -1
        for sel in selectors:
            try:
                handles = page.query_selector_all(sel)
            except Exception:
                continue
            for h in handles:
                try:
                    txt = (h.inner_text() or "").strip()
                    score = len(txt)
                    if score > best_score:
                        best_score = score
                        best = h
                except Exception:
                    continue
        if not best:
            return None
        try:
            return best.evaluate("el => el.outerHTML")
        except Exception:
            return None

    def _expand_full_toc(
        self, page, max_rounds: int = 10, settle_ms: int = 400
    ) -> None:
        """
        @brief Execute `_expand_full_toc`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_expand_full_toc`.
        @param page Input argument for `_expand_full_toc`.
        @param max_rounds Input argument for `_expand_full_toc`.
        @param settle_ms Input argument for `_expand_full_toc`.
        @return None Return value of `_expand_full_toc`.
        """
        selectors = [
            "button[aria-expanded='false']",
            "[role='treeitem'] > button[aria-expanded='false']",
            "button:has-text('Expand all')",
            "button:has-text('Expand')",
            ".expand",
            ".chevron",
        ]

        for i in range(max_rounds):
            try:
                clicked = page.evaluate(
                    "(selectors) => {\n"
                    "  let c = 0;\n"
                    "  selectors.forEach(sel => {\n"
                    "    document.querySelectorAll(sel).forEach(btn => {\n"
                    "      const aria = btn.getAttribute('aria-expanded');\n"
                    "      if (aria === 'true') return;\n"
                    "      btn.click();\n"
                    "      c += 1;\n"
                    "    });\n"
                    "  });\n"
                    "  return c;\n"
                    "}",
                    selectors,
                )
            except Exception:
                clicked = 0

            try:
                remaining = page.evaluate(
                    "(selectors) => {\n"
                    "  let r = 0;\n"
                    "  selectors.forEach(sel => { r += document.querySelectorAll(sel).length; });\n"
                    "  return r;\n"
                    "}",
                    [selectors[0], selectors[1]],
                )
            except Exception:
                remaining = 0

            self.log.verbose(
                f"[verbose] toc-expand round={i + 1} clicked={clicked} remaining={remaining}"
            )
            page.wait_for_timeout(settle_ms)

            if clicked == 0 and remaining == 0:
                break

    def _scroll_toc_container(
        self, page, step_px: int = 900, max_rounds: int = 40, settle_ms: int = 200
    ) -> None:
        """
        @brief Execute `_scroll_toc_container`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_scroll_toc_container`.
        @param page Input argument for `_scroll_toc_container`.
        @param step_px Input argument for `_scroll_toc_container`.
        @param max_rounds Input argument for `_scroll_toc_container`.
        @param settle_ms Input argument for `_scroll_toc_container`.
        @return None Return value of `_scroll_toc_container`.
        """
        for sel in self.TOC_SCROLL_SELECTORS:
            try:
                info = page.evaluate(
                    "(sel) => { const el = document.querySelector(sel); if (!el) return null; return {h: el.scrollHeight, c: el.clientHeight}; }",
                    sel,
                )
            except Exception:
                info = None
            if not info or not info.get("c"):
                continue

            last_pos = -1
            stable = 0
            for i in range(max_rounds):
                try:
                    pos = page.evaluate(
                        "(sel) => { const el = document.querySelector(sel); if (!el) return -1; return el.scrollTop; }",
                        sel,
                    )
                except Exception:
                    break
                try:
                    page.evaluate(
                        "(sel, step) => { const el = document.querySelector(sel); if (!el) return; el.scrollBy(0, step); }",
                        sel,
                        step_px,
                    )
                except Exception:
                    break
                page.wait_for_timeout(settle_ms)
                if pos == last_pos:
                    stable += 1
                else:
                    stable = 0
                last_pos = pos
                if stable >= 3:
                    break
            try:
                page.evaluate(
                    "(sel) => { const el = document.querySelector(sel); if (el) el.scrollTo(0, 0); }",
                    sel,
                )
            except Exception:
                pass

    def _find_scroll_container(self, page):
        """
        @brief Execute `_find_scroll_container`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_find_scroll_container`.
        @param page Input argument for `_find_scroll_container`.
        @return Any Return value of `_find_scroll_container`.
        """
        best = None
        best_area = -1
        for sel in self.CONTENT_SELECTORS:
            try:
                handles = page.query_selector_all(sel)
            except Exception:
                continue
            for h in handles:
                try:
                    info = h.evaluate(
                        "el => {\n"
                        "  const cs = getComputedStyle(el);\n"
                        "  return {\n"
                        "    scrollHeight: el.scrollHeight,\n"
                        "    clientHeight: el.clientHeight,\n"
                        "    clientWidth: el.clientWidth,\n"
                        "    overflowY: cs.overflowY,\n"
                        "  };\n"
                        "}"
                    )
                except Exception:
                    continue
                if not info or not info.get("clientHeight"):
                    continue
                scroll_h = info.get("scrollHeight", 0)
                client_h = info.get("clientHeight", 0)
                if scroll_h <= client_h + 10:
                    continue
                area = info.get("clientWidth", 0) * client_h
                if area > best_area:
                    best_area = area
                    best = h
        if best:
            return best

        try:
            handle = page.evaluate_handle(
                "() => {\n"
                "  const els = Array.from(document.querySelectorAll('*'));\n"
                "  let best = null;\n"
                "  let bestArea = 0;\n"
                "  for (const el of els) {\n"
                "    const cs = getComputedStyle(el);\n"
                "    const oy = cs.overflowY;\n"
                "    const scrollable = (oy === 'auto' || oy === 'scroll' || oy === 'overlay') && el.scrollHeight > el.clientHeight + 10;\n"
                "    if (!scrollable) continue;\n"
                "    const r = el.getBoundingClientRect();\n"
                "    const area = Math.max(0, r.width) * Math.max(0, r.height);\n"
                "    if (area > bestArea) { bestArea = area; best = el; }\n"
                "  }\n"
                "  return best;\n"
                "}"
            )
            element = handle.as_element() if handle else None
            return element
        except Exception:
            return None

    def _auto_scroll_element(
        self,
        page,
        element,
        settle_ms: int,
        step_px: int,
        max_rounds: int,
        stable_rounds: int,
        label: str,
    ) -> bool:
        """
        @brief Execute `_auto_scroll_element`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_auto_scroll_element`.
        @param page Input argument for `_auto_scroll_element`.
        @param element Input argument for `_auto_scroll_element`.
        @param settle_ms Input argument for `_auto_scroll_element`.
        @param step_px Input argument for `_auto_scroll_element`.
        @param max_rounds Input argument for `_auto_scroll_element`.
        @param stable_rounds Input argument for `_auto_scroll_element`.
        @param label Input argument for `_auto_scroll_element`.
        @return bool Return value of `_auto_scroll_element`.
        """
        try:
            info = element.evaluate(
                "el => ({ scrollHeight: el.scrollHeight, clientHeight: el.clientHeight })"
            )
        except Exception:
            return False
        if not info or info.get("scrollHeight", 0) <= info.get("clientHeight", 0) + 10:
            return True

        last_height = -1
        last_scroll_top = -1
        stable = 0
        for i in range(max_rounds):
            try:
                metrics = element.evaluate(
                    "el => ({ scrollHeight: el.scrollHeight, scrollTop: el.scrollTop, clientHeight: el.clientHeight })"
                )
            except Exception:
                return False
            height = metrics.get("scrollHeight", 0)
            scroll_top = metrics.get("scrollTop", 0)
            client_h = metrics.get("clientHeight", 0)
            if i == 0:
                self.log.verbose(f"[verbose] auto-scroll start ({label})")
            if height == last_height:
                stable += 1
            else:
                stable = 0
            if i % 8 == 0:
                self.log.verbose(
                    f"[verbose] auto-scroll round={i + 1} height={height} stable={stable} ({label})"
                )
            if stable >= stable_rounds:
                self.log.verbose(
                    f"[verbose] auto-scroll stop round={i + 1} stable={stable} height={height} ({label})"
                )
                break
            if scroll_top == last_scroll_top and (scroll_top + client_h >= height - 2):
                self.log.verbose(
                    f"[verbose] auto-scroll stop round={i + 1} bottom reached ({label})"
                )
                break
            last_height = height
            last_scroll_top = scroll_top
            try:
                element.evaluate("(el, step) => { el.scrollBy(0, step); }", step_px)
            except Exception:
                return False
            page.wait_for_timeout(settle_ms)

        try:
            element.evaluate("el => { el.scrollTop = el.scrollHeight; }")
            page.wait_for_timeout(settle_ms * 2)
            element.evaluate("el => { el.scrollTop = 0; }")
        except Exception:
            pass
        return True

    def _auto_scroll(
        self,
        page,
        settle_ms: int = 300,
        step_px: int = 1400,
        max_rounds: int = 320,
        stable_rounds: int = 6,
    ) -> None:
        """
        @brief Execute `_auto_scroll`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_auto_scroll`.
        @param page Input argument for `_auto_scroll`.
        @param settle_ms Input argument for `_auto_scroll`.
        @param step_px Input argument for `_auto_scroll`.
        @param max_rounds Input argument for `_auto_scroll`.
        @param stable_rounds Input argument for `_auto_scroll`.
        @return None Return value of `_auto_scroll`.
        """
        scroll_el = self._find_scroll_container(page)
        if scroll_el and self._auto_scroll_element(
            page,
            scroll_el,
            settle_ms=settle_ms,
            step_px=step_px,
            max_rounds=max_rounds,
            stable_rounds=stable_rounds,
            label="container",
        ):
            return

        try:
            page.evaluate("() => window.scrollTo(0, 0)")
        except Exception:
            pass

        last_height = -1
        stable = 0
        for i in range(max_rounds):
            try:
                height = page.evaluate(
                    "() => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
                )
                client_h = page.evaluate(
                    "() => Math.max(document.body.clientHeight, document.documentElement.clientHeight, window.innerHeight)"
                )
            except Exception:
                break
            if height <= client_h + 10:
                return
            if i == 0:
                self.log.verbose("[verbose] auto-scroll start")
            if height == last_height:
                stable += 1
            else:
                stable = 0
            if i % 8 == 0:
                self.log.verbose(
                    f"[verbose] auto-scroll round={i + 1} height={height} stable={stable}"
                )
            if stable >= stable_rounds:
                self.log.verbose(
                    f"[verbose] auto-scroll stop round={i + 1} stable={stable} height={height}"
                )
                break
            last_height = height
            page.evaluate(f"() => window.scrollBy(0, {step_px})")
            page.wait_for_timeout(settle_ms)

        try:
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(settle_ms * 2)
            page.evaluate("() => window.scrollTo(0, 0)")
        except Exception:
            pass

    def _collect_cards_from_container(
        self,
        page,
        container,
        settle_ms: int = 200,
        step_ratio: float = 0.9,
        stable_rounds: int = 6,
        max_rounds: int = 400,
    ) -> Dict[str, str]:
        """
        @brief Execute `_collect_cards_from_container`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_collect_cards_from_container`.
        @param page Input argument for `_collect_cards_from_container`.
        @param container Input argument for `_collect_cards_from_container`.
        @param settle_ms Input argument for `_collect_cards_from_container`.
        @param step_ratio Input argument for `_collect_cards_from_container`.
        @param stable_rounds Input argument for `_collect_cards_from_container`.
        @param max_rounds Input argument for `_collect_cards_from_container`.
        @return Dict[str, str] Return value of `_collect_cards_from_container`.
        """
        cards: Dict[str, str] = {}
        last_height = -1
        last_scroll_top = -1
        stable = 0

        for _ in range(max_rounds):
            try:
                batch = container.evaluate(
                    "el => {\n"
                    "  const primary = el.querySelectorAll('.documentSection[data-url]');\n"
                    "  const nodes = primary.length ? Array.from(primary) : Array.from(el.querySelectorAll('[data-url]'));\n"
                    "  return nodes.map(node => ({\n"
                    "    url: node.getAttribute('data-url') || '',\n"
                    "    html: node.outerHTML || ''\n"
                    "  }));\n"
                    "}"
                )
            except Exception:
                break

            for item in batch or []:
                url = (item.get("url") or "").strip()
                html = item.get("html") or ""
                if url and html and url not in cards:
                    cards[url] = html

            try:
                metrics = container.evaluate(
                    "el => ({ scrollTop: el.scrollTop, clientHeight: el.clientHeight, scrollHeight: el.scrollHeight })"
                )
            except Exception:
                break

            scroll_top = metrics.get("scrollTop", 0)
            client_h = metrics.get("clientHeight", 0)
            height = metrics.get("scrollHeight", 0)

            if height == last_height:
                stable += 1
            else:
                stable = 0

            if stable >= stable_rounds:
                break
            if scroll_top == last_scroll_top and (scroll_top + client_h >= height - 2):
                break

            last_height = height
            last_scroll_top = scroll_top

            step = int(client_h * step_ratio) if client_h else 0
            if step <= 0:
                break
            try:
                container.evaluate(
                    "(el, step) => { el.scrollTop = Math.min(el.scrollTop + step, el.scrollHeight); }",
                    step,
                )
            except Exception:
                break
            page.wait_for_timeout(settle_ms)

        return cards

    def _best_card_for_fragment(
        self, cards: Dict[str, str], fragment: str
    ) -> Optional[Tuple[str, str]]:
        """
        @brief Execute `_best_card_for_fragment`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_best_card_for_fragment`.
        @param cards Input argument for `_best_card_for_fragment`.
        @param fragment Input argument for `_best_card_for_fragment`.
        @return Optional[Tuple[str, str]] Return value of `_best_card_for_fragment`.
        """
        frag = unquote((fragment or "").lstrip("#").strip())
        if not frag:
            return None
        frag_l = frag.lower()
        frag_parts = [p for p in frag_l.split("/") if p]
        if frag_l not in frag_parts:
            frag_parts.insert(0, frag_l)
        match_parts = [p for p in frag_parts if len(p) >= 8] or frag_parts

        def score_value(val: str) -> int:
            """
            @brief Execute `score_value`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param val Input argument for `score_value`.
            @return int Return value of `score_value`.
            """
            if not val:
                return 0
            v = unquote(val).lower()
            if v == frag_l:
                return 100
            if frag_l and frag_l in v:
                return 80
            matched = [part for part in match_parts if part and part in v]
            if matched and len(matched) == len(match_parts):
                return 70
            if matched:
                return 40
            return 0

        best_url = None
        best_score = 0
        for url in cards:
            if not self._fragment_matches_url(fragment, url):
                continue
            _, frag_val = urldefrag(url)
            target = frag_val or url
            score = score_value(target)
            if score > best_score:
                best_score = score
                best_url = url

        if best_url and best_score > 0:
            return best_url, cards[best_url]
        return None

    def _fragment_matches_url(self, fragment: str, data_url: str) -> bool:
        """
        @brief Execute `_fragment_matches_url`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_fragment_matches_url`.
        @param fragment Input argument for `_fragment_matches_url`.
        @param data_url Input argument for `_fragment_matches_url`.
        @return bool Return value of `_fragment_matches_url`.
        """
        frag = unquote((fragment or "").lstrip("#").strip()).lower()
        if not frag or not data_url:
            return False
        parts = [p for p in frag.split("/") if p]
        if frag not in parts:
            parts.insert(0, frag)
        parts = [p for p in parts if len(p) >= 8] or parts
        _, frag_val = urldefrag(data_url)
        target = unquote(frag_val or data_url).lower()
        return all(part in target for part in parts)

    def _toc_tree_from_html(self, toc_html: str) -> List[TocNode]:
        """
        @brief Execute `_toc_tree_from_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_toc_tree_from_html`.
        @param toc_html Input argument for `_toc_tree_from_html`.
        @return List[TocNode] Return value of `_toc_tree_from_html`.
        """
        return toc_from_nav_html(toc_html, self.from_url)

    @staticmethod
    def _iter_nodes(nodes: List[TocNode]) -> Iterable[TocNode]:
        """
        @brief Execute `_iter_nodes`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_iter_nodes`.
        @return Iterable[TocNode] Return value of `_iter_nodes`.
        """
        for n in nodes:
            yield n
            yield from DocumentViewerDownloader._iter_nodes(n.children)

    @staticmethod
    def _first_numeric_index(nodes: List[TocNode]) -> Optional[int]:
        """
        @brief Execute `_first_numeric_index`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_first_numeric_index`.
        @return Optional[int] Return value of `_first_numeric_index`.
        """
        for i, n in enumerate(nodes):
            title = (n.title or "").strip().lower()
            if title.startswith("1 "):
                return i
        return None

    @staticmethod
    def _trim_toc_nodes(nodes: List[TocNode]) -> List[TocNode]:
        """
        @brief Execute `_trim_toc_nodes`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_trim_toc_nodes`.
        @return List[TocNode] Return value of `_trim_toc_nodes`.
        """
        if not nodes:
            return []

        trimmed = list(nodes)
        start_idx = DocumentViewerDownloader._first_numeric_index(trimmed)
        if start_idx is not None:
            trimmed = trimmed[start_idx:]

        if trimmed and DocumentViewerDownloader._is_important_notice_label(
            trimmed[-1].title
        ):
            trimmed = trimmed[:-1]

        return trimmed if trimmed else list(nodes)

    @staticmethod
    def _limit_toc_nodes(
        nodes: List[TocNode], max_entries: Optional[int]
    ) -> List[TocNode]:
        """
        @brief Execute `_limit_toc_nodes`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_limit_toc_nodes`.
        @param max_entries Input argument for `_limit_toc_nodes`.
        @return List[TocNode] Return value of `_limit_toc_nodes`.
        """
        return limit_toc_nodes(nodes, max_entries)

    @staticmethod
    def _limit_by_reading_order(
        nodes: List[TocNode], max_entries: Optional[int]
    ) -> List[TocNode]:
        """
        @brief Execute `_limit_by_reading_order`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_limit_by_reading_order`.
        @param max_entries Input argument for `_limit_by_reading_order`.
        @return List[TocNode] Return value of `_limit_by_reading_order`.
        """
        if not max_entries or max_entries <= 0:
            return nodes
        node_ids = {id(n) for n in nodes}
        has_descendants_in_list = False
        for n in nodes:
            for child in DocumentViewerDownloader._iter_nodes(n.children):
                if id(child) in node_ids:
                    has_descendants_in_list = True
                    break
            if has_descendants_in_list:
                break

        if has_descendants_in_list:
            limited: List[TocNode] = []
            seen: Set[int] = set()
            for n in nodes:
                nid = id(n)
                if nid in seen:
                    continue
                seen.add(nid)
                limited.append(n)
                if len(limited) >= max_entries:
                    break
            return limited

        flat = list(DocumentViewerDownloader._iter_nodes(nodes))
        return flat[:max_entries]

    @staticmethod
    def _prune_toc_to_allowed(
        nodes: List[TocNode], allowed_ids: Set[int]
    ) -> List[TocNode]:
        """
        @brief Execute `_prune_toc_to_allowed`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_prune_toc_to_allowed`.
        @param allowed_ids Input argument for `_prune_toc_to_allowed`.
        @return List[TocNode] Return value of `_prune_toc_to_allowed`.
        """
        pruned: List[TocNode] = []
        for n in nodes:
            kept_children = DocumentViewerDownloader._prune_toc_to_allowed(
                n.children, allowed_ids
            )
            is_allowed = id(n) in allowed_ids
            if is_allowed:
                n.children = kept_children
                pruned.append(n)
            elif kept_children:
                pruned.extend(kept_children)
        return pruned

    @staticmethod
    def _first_toc_entry_title(nodes: List[TocNode]) -> Optional[str]:
        """
        @brief Execute `_first_toc_entry_title`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_first_toc_entry_title`.
        @return Optional[str] Return value of `_first_toc_entry_title`.
        """
        for node in nodes:
            title = (node.title or "").strip()
            if title:
                return title
        return None

    @staticmethod
    def _is_important_notice_label(title: Optional[str]) -> bool:
        """
        @brief Execute `_is_important_notice_label`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param title Input argument for `_is_important_notice_label`.
        @return bool Return value of `_is_important_notice_label`.
        """
        text = (title or "").strip().lower()
        return text.startswith("important notice")

    @staticmethod
    def _is_important_notice_section(section_html: str) -> bool:
        """
        @brief Execute `_is_important_notice_section`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param section_html Input argument for `_is_important_notice_section`.
        @return bool Return value of `_is_important_notice_section`.
        """
        soup = BeautifulSoup(section_html, "lxml")
        heading = soup.find(re.compile(r"^h[1-6]$"))
        if heading and DocumentViewerDownloader._is_important_notice_label(
            heading.get_text(" ", strip=True)
        ):
            return True
        flat_text = " ".join(soup.get_text(" ", strip=True).split()).lower()
        return "important notice and disclaimer" in flat_text

    @staticmethod
    def _select_section_nodes(nodes: List[TocNode]) -> List[TocNode]:
        """
        @brief Execute `_select_section_nodes`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_select_section_nodes`.
        @return List[TocNode] Return value of `_select_section_nodes`.
        """
        flat = list(DocumentViewerDownloader._iter_nodes(nodes))
        if not flat:
            return []

        start_idx = DocumentViewerDownloader._first_numeric_index(flat)
        if start_idx is None:
            start_idx = 0

        end_idx = None
        for i in range(len(flat) - 1, -1, -1):
            if DocumentViewerDownloader._is_important_notice_label(flat[i].title):
                end_idx = i
                break

        if end_idx is None or end_idx < start_idx:
            end_idx = len(flat) - 1

        return flat[start_idx : end_idx + 1]

    def _dedup_toc_nodes_by_href(self, nodes: List[TocNode]) -> List[TocNode]:
        """
        @brief Execute `_dedup_toc_nodes_by_href`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_dedup_toc_nodes_by_href`.
        @param nodes Input argument for `_dedup_toc_nodes_by_href`.
        @return List[TocNode] Return value of `_dedup_toc_nodes_by_href`.
        """

        def dedup_list(items: List[TocNode]) -> List[TocNode]:
            """
            @brief Execute `dedup_list`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param items Input argument for `dedup_list`.
            @return List[TocNode] Return value of `dedup_list`.
            """
            seen: Dict[str, TocNode] = {}  # Scope seen to this level only
            out: List[TocNode] = []
            for n in items:
                key = (n.href or "").strip().lower()
                # Recursively deduplicate children first
                n.children = dedup_list(n.children)
                if key:
                    existing = seen.get(key)
                    if existing:
                        # Merge children and prefer the more descriptive/structured title
                        existing_children_before = len(existing.children)
                        existing.children.extend(n.children)
                        if len(n.children) > existing_children_before:
                            existing.title = n.title
                        elif len(n.title or "") > len(existing.title or ""):
                            existing.title = n.title
                        continue
                    seen[key] = n
                out.append(n)
            return out

        return dedup_list(nodes)

    def _is_section_scrollable(self, page, viewport_multiplier: float = 2.0) -> bool:
        """
        @brief Execute `_is_section_scrollable`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_is_section_scrollable`.
        @param page Input argument for `_is_section_scrollable`.
        @param viewport_multiplier Input argument for `_is_section_scrollable`.
        @return bool Return value of `_is_section_scrollable`.
        """
        try:
            result = page.evaluate(
                f"() => {{\n"
                f"  const body = document.body;\n"
                f"  const html = document.documentElement;\n"
                f"  const scrollH = Math.max(body.scrollHeight, html.scrollHeight);\n"
                f"  const clientH = Math.max(body.clientHeight, html.clientHeight, window.innerHeight);\n"
                f"  return scrollH > (clientH * {viewport_multiplier});\n"
                f"}}"
            )
            return bool(result)
        except Exception:
            return False

    def _remove_toc_elements(self, soup: BeautifulSoup) -> None:
        """
        @brief Execute `_remove_toc_elements`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_remove_toc_elements`.
        @param soup Input argument for `_remove_toc_elements`.
        @return None Return value of `_remove_toc_elements`.
        """
        # Remove by tag name (TI custom components)
        toc_tag_names = [
            "ti-library-viewer-side-bar",
            "ti-library-viewer-tab-bar",
            "ti-library-viewer-command-bar",
        ]
        for tag_name in toc_tag_names:
            for elem in list(soup.find_all(tag_name)):
                elem.decompose()

        # Remove by selector
        toc_selectors = [
            "#viewer_navTree",  # Main navigation tree
            ".viewer-sidebar",  # Sidebar container
            "#ti_library_viewer_contents",  # TOC contents section
            ".tiLibrary-tabs",  # Tab bar
            ".tab-slider",  # Tab slider navigation
            "#doc-lister",  # Document lister title (captured separately)
            ".toc_hierarchy",  # TOC hierarchy container
            ".mininav",  # Mini navigation controls
            "[data-lid='ti-library-viewer-side-bar']",  # TOC by data attribute
            "[data-lid='ti-library-viewer-tab-bar']",  # Tab bar by data attribute
            "[data-lid='ti-library-viewer-toc']",  # TOC by data attribute
            "[data-lid='ti-library-viewer-command-bar']",  # Command bar
        ]
        for sel in toc_selectors:
            for elem in list(soup.select(sel)):
                elem.decompose()

    def _convert_doxygen_definition_lists(self, soup: BeautifulSoup) -> None:
        """
        @brief Execute `_convert_doxygen_definition_lists`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_convert_doxygen_definition_lists`.
        @param soup Input argument for `_convert_doxygen_definition_lists`.
        @return None Return value of `_convert_doxygen_definition_lists`.
        """
        try:
            # Handle <dl><dt>/<dd> pairs first
            for dl in list(soup.find_all("dl")):
                parts: List[str] = []
                for dt in dl.find_all("dt"):
                    dd = dt.find_next_sibling("dd")
                    if not dd:
                        continue
                    label = (dt.get_text(" ", strip=True) or "").upper()
                    desc_html = dd.decode_contents() or ""
                    parts.append(f"<p><strong>{escape_html(label)}:</strong> {desc_html}</p>")
                if parts:
                    frag = BeautifulSoup("\n".join(parts), "lxml")
                    dl.replace_with(frag)

            # Handle adjacent paragraph style variations:
            # 1) <p>Label</p> + <p>: description</p>
            # 2) <p>Label</p> + <p>:</p> + <p>description</p>
            for p in list(soup.find_all("p")):
                nxt = p.find_next_sibling()
                if not nxt or nxt.name != "p":
                    continue
                left_text = (p.get_text(" ", strip=True) or "").strip()
                right_text = (nxt.get_text("\n", strip=True) or "")
                if not left_text or right_text is None:
                    continue

                # Case A: right paragraph starts with a colon followed by text
                if re.match(r"^\s*:\s*\S+", right_text):
                    desc_html = re.sub(r"^\s*:\s*", "", nxt.decode_contents(), count=1)
                    label = left_text.upper()
                    new_frag = BeautifulSoup(
                        f"<p><strong>{escape_html(label)}:</strong> {desc_html}</p>",
                        "lxml",
                    )
                    p.replace_with(new_frag)
                    nxt.decompose()
                    continue

                # Case B: right paragraph is just a colon (possibly with spaces)
                if re.match(r"^\s*:\s*$", right_text):
                    desc_node = nxt.find_next_sibling()
                    if desc_node and desc_node.name == "p":
                        desc_html = desc_node.decode_contents() or ""
                        label = left_text.upper()
                        new_frag = BeautifulSoup(
                            f"<p><strong>{escape_html(label)}:</strong> {desc_html}</p>",
                            "lxml",
                        )
                        p.replace_with(new_frag)
                        # remove the marker and the description nodes
                        nxt.decompose()
                        desc_node.decompose()
                        continue
                # Otherwise, not a definition-style pair
        except Exception:
            # Non-fatal: if conversion fails, leave document unchanged
            return

    def _extract_fragment_only(
        self, soup: BeautifulSoup, fragment: str
    ) -> BeautifulSoup:
        """
        @brief Execute `_extract_fragment_only`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_extract_fragment_only`.
        @param soup Input argument for `_extract_fragment_only`.
        @param fragment Input argument for `_extract_fragment_only`.
        @return BeautifulSoup Return value of `_extract_fragment_only`.
        """
        frag = unquote((fragment or "").lstrip("#").strip())
        if not frag:
            return soup

        frag_l = frag.lower()
        frag_parts = [p for p in frag_l.split("/") if p]
        if frag_l not in frag_parts:
            frag_parts.insert(0, frag_l)

        def score_value(val: str) -> int:
            """
            @brief Execute `score_value`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param val Input argument for `score_value`.
            @return int Return value of `score_value`.
            """
            if not val:
                return 0
            v = unquote(val).lower()
            if v == frag_l:
                return 100
            if frag_l and frag_l in v:
                return 80
            score = 0
            for part in frag_parts:
                if part == frag_l:
                    continue
                if v == part:
                    score = max(score, 60)
                elif part and part in v:
                    score = max(score, 40)
            return score

        def pick_best_section(elements):
            """
            @brief Execute `pick_best_section`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param elements Input argument for `pick_best_section`.
            @return Any Return value of `pick_best_section`.
            """
            best = None
            best_score = 0
            best_len = None
            for el in elements:
                data_url = el.get("data-url") or ""
                score = score_value(data_url)
                if score <= 0:
                    continue
                text_len = len(el.get_text(" ", strip=True))
                if score > best_score or (
                    score == best_score and (best_len is None or text_len < best_len)
                ):
                    best = el
                    best_score = score
                    best_len = text_len
            return best

        # Prefer a single documentSection card that matches the fragment to avoid duplicated parent cards.
        candidates = soup.select(".documentSection[data-url]") or soup.find_all(
            attrs={"data-url": True}
        )
        best_section = pick_best_section(candidates)
        if best_section:
            narrowed = BeautifulSoup("", "lxml")
            narrowed.append(BeautifulSoup(str(best_section), "lxml"))
            return narrowed

        def matches_fragment(el) -> bool:
            """
            @brief Execute `matches_fragment`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param el Input argument for `matches_fragment`.
            @return bool Return value of `matches_fragment`.
            """
            if not el:
                return False
            el_id = el.get("id")
            if el_id and (el_id.lower() == frag_l or el_id.lower() in frag_parts):
                return True
            el_name = el.get("name")
            if el_name and (el_name.lower() == frag_l or el_name.lower() in frag_parts):
                return True
            data_url = el.get("data-url") or ""
            if data_url and score_value(data_url) > 0:
                return True
            return False

        target = None
        for el in soup.find_all(True):
            if matches_fragment(el):
                target = el
                break

        if not target:
            return soup

        chosen = target
        parent_section = target.find_parent(attrs={"data-url": True})
        if parent_section:
            chosen = parent_section
        else:
            for ancestor in target.parents:
                if ancestor is soup:
                    break
                if ancestor.name in ("section", "div", "article"):
                    data_url = ancestor.get("data-url") or ""
                    if ancestor.get("id") or score_value(data_url) > 0:
                        chosen = ancestor
                        break

        narrowed = BeautifulSoup("", "lxml")
        narrowed.append(BeautifulSoup(str(chosen), "lxml"))
        return narrowed

    def _wait_for_fragment(self, page, fragment: str, timeout_ms: int = 8000) -> bool:
        """
        @brief Execute `_wait_for_fragment`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_wait_for_fragment`.
        @param page Input argument for `_wait_for_fragment`.
        @param fragment Input argument for `_wait_for_fragment`.
        @param timeout_ms Input argument for `_wait_for_fragment`.
        @return bool Return value of `_wait_for_fragment`.
        """
        frag = unquote((fragment or "").lstrip("#").strip())
        if not frag:
            return True
        frag_l = frag.lower()
        frag_parts = [p for p in frag_l.split("/") if p]
        if frag_l not in frag_parts:
            frag_parts.insert(0, frag_l)

        js = (
            "(frag, fragLower, parts) => {\n"
            "  const norm = (s) => (s || '').toLowerCase();\n"
            "  const matches = (val) => {\n"
            "    const v = norm(val);\n"
            "    if (!v) return false;\n"
            "    if (v === fragLower || v.includes(fragLower)) return true;\n"
            "    for (const p of parts) {\n"
            "      if (p && (v === p || v.includes(p))) return true;\n"
            "    }\n"
            "    return false;\n"
            "  };\n"
            "  if (document.getElementById(frag) || document.getElementById(fragLower)) return true;\n"
            "  const named = document.getElementsByName(frag);\n"
            "  if (named && named.length) return true;\n"
            "  const els = document.querySelectorAll('[data-url], [id], [name]');\n"
            "  for (const el of els) {\n"
            "    const elId = el.getAttribute('id');\n"
            "    if (elId && (norm(elId) === fragLower || parts.includes(norm(elId)))) return true;\n"
            "    const elName = el.getAttribute('name');\n"
            "    if (elName && (norm(elName) === fragLower || parts.includes(norm(elName)))) return true;\n"
            "    if (matches(el.getAttribute('data-url'))) return true;\n"
            "  }\n"
            "  return false;\n"
            "}\n"
        )

        try:
            page.wait_for_function(js, frag, frag_l, frag_parts, timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False
        except Exception:
            return False

    def _click_toc_link(self, page, fragment: str) -> bool:
        """
        @brief Execute `_click_toc_link`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_click_toc_link`.
        @param page Input argument for `_click_toc_link`.
        @param fragment Input argument for `_click_toc_link`.
        @return bool Return value of `_click_toc_link`.
        """
        frag = unquote((fragment or "").lstrip("#").strip())
        if not frag:
            return False
        try:
            return bool(
                page.evaluate(
                    "(frag) => {\n"
                    "  const links = Array.from(document.querySelectorAll('a'));\n"
                    "  const target = links.find(a => (a.getAttribute('href') || '').includes(frag));\n"
                    "  if (!target) return false;\n"
                    "  target.scrollIntoView({ block: 'center' });\n"
                    "  target.click();\n"
                    "  return true;\n"
                    "}\n",
                    frag,
                )
            )
        except Exception:
            return False

    def run(self) -> None:
        """
        @brief Execute `run`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `run`.
        @return None Return value of `run`.
        """
        recorder = NetworkImageRecorder(self.out_dir)
        self.log.debug("[debug] document-viewer: recorder attached")

        def make_anchor(raw_fragment: str, title: str, used: Set[str]) -> str:
            """
            @brief Execute `make_anchor`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param raw_fragment Input argument for `make_anchor`.
            @param title Input argument for `make_anchor`.
            @param used Input argument for `make_anchor`.
            @return str Return value of `make_anchor`.
            """
            base = (raw_fragment or title or "sezione").strip()
            base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower() or "sezione"
            cand = base
            i = 2
            while cand in used:
                cand = f"{base}-{i}"
                i += 1
            used.add(cand)
            return cand

        def normalize_text(value: str) -> str:
            """
            @brief Execute `normalize_text`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param value Input argument for `normalize_text`.
            @return str Return value of `normalize_text`.
            """
            value = (value or "").strip()
            value = re.sub(r"\s+", " ", value)
            return value.lower()

        def strip_ti_disclaimer(section_html: str) -> str:
            """
            @brief Execute `strip_ti_disclaimer`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param section_html Input argument for `strip_ti_disclaimer`.
            @return str Return value of `strip_ti_disclaimer`.
            """
            soup = BeautifulSoup(section_html, "lxml")
            section = soup.find("section")
            if not section:
                return section_html

            disclaimer_tag = None
            for candidate in section.find_all(["p", "div"]):
                text = (
                    " ".join(candidate.get_text(" ", strip=True).split())
                    .strip()
                    .lower()
                )
                if text.startswith("ti provides technical and reliability data"):
                    disclaimer_tag = candidate
                    break

            if not disclaimer_tag:
                return section_html

            for sibling in list(disclaimer_tag.find_next_siblings()):
                sibling.decompose()
            disclaimer_tag.decompose()
            return str(section)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(90_000)

            recorder.attach(page)

            try:
                page.goto(self.from_url, wait_until="networkidle")
            except PlaywrightTimeoutError:
                page.goto(self.from_url, wait_until="domcontentloaded")

            page.wait_for_timeout(2000)

            # Expand navigation tree (with repeated passes and scroll in TOC) to capture full TOC
            for _ in range(3):
                self._expand_full_toc(page)
                self._scroll_toc_container(page)
            self._expand_full_toc(page)

            toc_html = self._pick_best_outerhtml(page, self.TOC_SELECTORS)
            if not toc_html:
                try:
                    toc_html = page.evaluate(
                        "() => { const nav = document.querySelector('nav'); return nav ? nav.outerHTML : null; }"
                    )
                except Exception:
                    toc_html = None

            if toc_html:
                self.log.check("[check] TOC HTML catturata dalla pagina")
            else:
                self.log.debug(
                    "[debug] Nessuna TOC HTML catturata, si useranno le intestazioni"
                )

            # Also capture doc-lister title if present (TI pages have this as a separate element)
            doc_title_html = None
            try:
                doc_title_html = page.evaluate(
                    "() => { const el = document.querySelector('#doc-lister'); return el ? el.outerHTML : null; }"
                )
            except Exception:
                pass

            content_html = self._pick_best_outerhtml(page, self.CONTENT_SELECTORS)
            if not content_html:
                content_html = page.evaluate("() => document.body.outerHTML")

            initial_content_html = content_html or ""
            content_soup = BeautifulSoup(initial_content_html, "lxml")
            ensure_heading_ids(content_soup)

            toc_nodes: List[TocNode] = []
            if toc_html:
                toc_nodes = self._toc_tree_from_html(toc_html)

            # Prepend doc title if captured separately
            if doc_title_html:
                title_soup = BeautifulSoup(doc_title_html, "lxml")
                title_text = " ".join(title_soup.get_text(" ", strip=True).split())
                if title_text and title_text not in str(toc_nodes):
                    title_node = TocNode(title=title_text, href=self.from_url)
                    toc_nodes.insert(0, title_node)

            if not toc_nodes:
                self.log.verbose("[verbose] TOC fallback: building from headings")
                toc_nodes = toc_from_headings(content_soup)

            pre_trim_title_text = self._first_toc_entry_title(toc_nodes)

            section_nodes = self._select_section_nodes(toc_nodes)
            display_toc_nodes = self._trim_toc_nodes(toc_nodes)

            # Apply reading-order limit: take the first <limit> entries across all levels
            if self.limit:
                section_nodes = self._limit_by_reading_order(section_nodes, self.limit)
                allowed_ids = {id(n) for n in section_nodes}
                display_toc_nodes = self._prune_toc_to_allowed(
                    display_toc_nodes, allowed_ids
                )
            else:
                allowed_ids = {id(n) for n in section_nodes}

            if not section_nodes:
                section_nodes = list(self._iter_nodes(toc_nodes))
                allowed_ids = {id(n) for n in section_nodes}

            if not display_toc_nodes:
                display_toc_nodes = self._prune_toc_to_allowed(toc_nodes, allowed_ids)

            clean_display_toc_nodes: List[TocNode] = []
            cleaned_title: Optional[str] = None
            if display_toc_nodes:
                clean_display_toc_nodes = self._dedup_toc_nodes_by_href(
                    display_toc_nodes
                )
                cleaned_title = self._first_toc_entry_title(clean_display_toc_nodes)

            title_text: Optional[str] = pre_trim_title_text or cleaned_title
            used_ids: Set[str] = set()
            section_plan: List[
                Tuple[str, str, str, str]
            ] = []  # (full_url_with_fragment, anchor, title, fragment)
            section_to_toc_node: Dict[
                int, TocNode
            ] = {}  # Map section index to TOC node
            url_to_anchor: Dict[
                str, str
            ] = {}  # Map section URL -> anchor kept in document
            frag_to_anchor: Dict[
                str, str
            ] = {}  # Map normalized fragment -> chosen anchor

            for node in section_nodes:
                raw_href = node.href or ""
                full_href = (
                    normalize_url(raw_href, self.from_url)
                    if raw_href
                    else self.from_url
                )
                base_url, frag = urldefrag(full_href)
                if not base_url:
                    base_url = self.from_url

                frag_norm = (frag or "").lstrip("#").strip().lower()

                # Choose/reuse anchor for this fragment (regardless of whether it will be downloaded)
                anchor = None
                if frag_norm and frag_norm in frag_to_anchor:
                    anchor = frag_to_anchor[frag_norm]

                section_url = full_href if frag else base_url

                # Reuse anchor for repeated section URLs so TOC always points to a kept section
                if section_url in url_to_anchor:
                    anchor = anchor or url_to_anchor[section_url]
                    node.href = f"#{anchor}"
                    continue

                if not anchor:
                    anchor = make_anchor(frag, node.title, used_ids)
                    if frag_norm:
                        frag_to_anchor[frag_norm] = anchor

                node.href = f"#{anchor}"
                url_to_anchor[section_url] = anchor

                # For TI document-viewer, the fragment determines which content is loaded
                # Use the full URL with fragment to ensure unique content per section
                section_idx = len(section_plan)
                section_plan.append((section_url, anchor, node.title, frag))
                section_to_toc_node[section_idx] = node

            if not section_plan:
                self.log.verbose(
                    "[verbose] No TOC sections detected; using full document"
                )
                section_plan.append(
                    (
                        self.from_url,
                        make_anchor("", "documento", used_ids),
                        "Documento",
                        "",
                    )
                )

            if not title_text and section_plan:
                title_text = (section_plan[0][2] or "").strip()
            title_text = title_text or "Documento"

            self.log.debug(f"[debug] Planned {len(section_plan)} sections from TOC")

            scroll_container = self._find_scroll_container(page)
            cards_by_url: Dict[str, str] = {}
            if scroll_container:
                try:
                    scroll_container.evaluate("el => { el.scrollTop = 0; }")
                except Exception:
                    pass
                cards_by_url = self._collect_cards_from_container(
                    page, scroll_container
                )
                self.log.debug(
                    f"[debug] Collected {len(cards_by_url)} cards from scroll container"
                )
                if cards_by_url and len(cards_by_url) < max(3, len(section_plan) // 2):
                    self.log.debug(
                        "[debug] Card cache incomplete; falling back to per-section load"
                    )
                    cards_by_url = {}
            else:
                self._auto_scroll(page)

            sections_html: List[str] = []
            seen_card_urls: Dict[str, str] = {}
            # Download all deduplicated sections (skip scrollability filtering)
            first_scrollable_idx = 0

            # Download sections starting from the first scrollable one
            for section_idx, (section_url, anchor, title, raw_fragment) in enumerate(
                section_plan[first_scrollable_idx:], start=first_scrollable_idx
            ):
                self.log.verbose(
                    f"[verbose] Fetching section {section_idx + 1}/{len(section_plan)} -> {section_url}"
                )
                section_html = None
                card_url = None
                from_cache = False

                if cards_by_url:
                    card_match = self._best_card_for_fragment(
                        cards_by_url, raw_fragment
                    )
                    if card_match:
                        card_url, section_html = card_match
                        if card_url in seen_card_urls:
                            existing_anchor = seen_card_urls[card_url]
                            node = section_to_toc_node.get(section_idx)
                            if node:
                                node.href = f"#{existing_anchor}"
                            continue
                        seen_card_urls[card_url] = anchor
                        from_cache = True

                if not section_html:
                    fragment_ready = False
                    if self._click_toc_link(page, raw_fragment):
                        page.wait_for_timeout(500)
                        fragment_ready = self._wait_for_fragment(
                            page, raw_fragment, timeout_ms=12000
                        )

                    if not fragment_ready:
                        try:
                            page.goto(section_url, wait_until="domcontentloaded")
                        except PlaywrightTimeoutError:
                            try:
                                page.goto(section_url, wait_until="networkidle")
                            except Exception:
                                pass
                        page.wait_for_timeout(500)
                        fragment_ready = self._wait_for_fragment(
                            page, raw_fragment, timeout_ms=12000
                        )

                    if fragment_ready:
                        self._auto_scroll(
                            page,
                            settle_ms=150,
                            step_px=1200,
                            max_rounds=60,
                            stable_rounds=3,
                        )

                    section_html = self._pick_best_outerhtml(
                        page, self.CONTENT_SELECTORS
                    )
                    if not section_html:
                        try:
                            section_html = page.evaluate(
                                "() => document.body.outerHTML"
                            )
                        except Exception:
                            section_html = ""

                section_soup = BeautifulSoup(section_html or "", "lxml")
                self._remove_toc_elements(
                    section_soup
                )  # Remove TOC/navigation before processing
                section_soup = self._extract_fragment_only(section_soup, raw_fragment)
                if section_idx == 0 and title:
                    expected = normalize_text(title)
                    section_text = normalize_text(
                        section_soup.get_text(" ", strip=True)
                    )
                    if expected and expected not in section_text:
                        fallback_soup = BeautifulSoup(initial_content_html, "lxml")
                        self._remove_toc_elements(fallback_soup)
                        fallback_section = self._extract_fragment_only(
                            fallback_soup, raw_fragment
                        )
                        fallback_text = normalize_text(
                            fallback_section.get_text(" ", strip=True)
                        )
                        if expected and expected not in fallback_text:
                            first_card = fallback_soup.select_one(
                                ".documentSection[data-url]"
                            )
                            if first_card:
                                alt = BeautifulSoup("", "lxml")
                                alt.append(BeautifulSoup(str(first_card), "lxml"))
                                fallback_section = alt
                                fallback_text = normalize_text(
                                    fallback_section.get_text(" ", strip=True)
                                )
                        if expected and expected in fallback_text:
                            self.log.debug(
                                "[debug] Fallback to initial content for first section"
                            )
                            section_soup = fallback_section
                ensure_heading_ids(section_soup)

                if not from_cache:
                    if not card_url:
                        first_card = section_soup.find(attrs={"data-url": True})
                        if first_card:
                            card_url = (first_card.get("data-url") or "").strip()
                    if card_url and not self._fragment_matches_url(
                        raw_fragment, card_url
                    ):
                        card_url = None
                    if card_url:
                        if card_url in seen_card_urls:
                            existing_anchor = seen_card_urls[card_url]
                            node = section_to_toc_node.get(section_idx)
                            if node:
                                node.href = f"#{existing_anchor}"
                            continue
                        seen_card_urls[card_url] = anchor

                asset_urls = iter_asset_urls(section_soup, section_url)
                for u in sorted(asset_urls):
                    lp = local_path_for_url(u, self.out_dir)
                    if not lp.exists():
                        download_one(self.session, u, lp)

                self.log.debug(
                    f"[debug] Section assets: {len(asset_urls)} from {section_url}"
                )

                rewrite_asset_links_inplace(section_soup, section_url, self.out_dir)
                strip_styles(section_soup)

                wrapper = BeautifulSoup("", "lxml")
                section_tag = wrapper.new_tag("section")
                section_tag["id"] = anchor
                if title and not section_soup.find(["h1", "h2", "h3"]):
                    heading = wrapper.new_tag("h2")
                    heading.string = title
                    section_tag.append(heading)
                inner_html = (
                    section_soup.body.decode_contents()
                    if section_soup.body
                    else str(section_soup)
                )
                inner_soup = BeautifulSoup(inner_html, "lxml")
                container = inner_soup.body or inner_soup
                for child in list(container.children):
                    section_tag.append(child)

                sections_html.append(str(section_tag))

            browser.close()
            if sections_html:
                if self._is_important_notice_section(sections_html[-1]):
                    sections_html.pop()
                else:
                    sections_html[-1] = strip_ti_disclaimer(sections_html[-1])

        self.log.check("[check] Generating document.html")
        body_parts = []
        if title_text:
            body_parts.append(
                f'<p class="document-title">{escape_html(title_text)}</p>'
            )
        body_parts.extend(sections_html)
        doc_html = minimal_readable_wrapper(
            "\n".join(body_parts), title="Documento (offline)"
        )
        doc_soup = BeautifulSoup(doc_html, "lxml")
        ensure_heading_ids(doc_soup)
        # Convert Doxygen-style definition lists and textual definition
        # pairs into inline bold uppercase labels to improve text retrieval
        self._convert_doxygen_definition_lists(doc_soup)
        toc_from_doc = toc_from_headings(doc_soup)
        toc_for_output = (
            clean_display_toc_nodes if clean_display_toc_nodes else toc_from_doc
        )
        (self.out_dir / "document.html").write_text(str(doc_soup), encoding="utf-8")
        self.log.check("[check] Generating toc.html")
        (self.out_dir / "toc.html").write_text(
            build_toc_html(
                toc_for_output, document_filename="document.html", target_frame="doc"
            ),
            encoding="utf-8",
        )
        self.log.check("[check] Generating index.html")
        (self.out_dir / "index.html").write_text(
            build_frameset_index(
                toc_filename="toc.html", document_filename="document.html"
            ),
            encoding="utf-8",
        )

        self.log.check(
            f"[check] Captured images via network: {len(recorder.saved)} (failed: {len(recorder.failed)})"
        )

        self.post_process()


# ----------------------------
# Doxygen-export downloader
# ----------------------------


class DoxygenExportDownloader(BaseDownloader):
    """
    @brief Define class `DoxygenExportDownloader`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    name = "doxygen-export"

    @classmethod
    def matches_url(cls, url: str) -> bool:
        """
        @brief Execute `matches_url`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param cls Input argument for `matches_url`.
        @param url Input argument for `matches_url`.
        @return bool Return value of `matches_url`.
        """
        u = urlparse(url)
        # TI export path typically contains /exports/ and ends with index.html
        return ("/exports/" in u.path and url.lower().endswith(".html")) or (
            "doxygen" in u.path.lower()
        )

    @classmethod
    def probe_html(cls, url: str, html: str) -> bool:
        """
        @brief Execute `probe_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param cls Input argument for `probe_html`.
        @param url Input argument for `probe_html`.
        @param html Input argument for `probe_html`.
        @return bool Return value of `probe_html`.
        """
        h = html.lower()
        return ('name="generator"' in h and "doxygen" in h) or ("dynsections.js" in h)

    def _scope(self) -> Tuple[str, str]:
        """
        @brief Execute `_scope`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_scope`.
        @return Tuple[str, str] Return value of `_scope`.
        """
        u = urlparse(self.from_url)
        host = u.netloc
        path = u.path
        dir_path = path.rsplit("/", 1)[0] + "/" if "/" in path else "/"
        scope_dir_url = f"{u.scheme}://{u.netloc}{dir_path}"
        return host, scope_dir_url

    def _fetch_soup(self, url: str) -> BeautifulSoup:
        """
        @brief Execute `_fetch_soup`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_fetch_soup`.
        @param url Input argument for `_fetch_soup`.
        @return BeautifulSoup Return value of `_fetch_soup`.
        """
        r = self.session.get(url, timeout=60, allow_redirects=True)
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")

    def _is_in_scope(self, url: str, host: str, scope_dir_url: str) -> bool:
        """
        @brief Execute `_is_in_scope`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_is_in_scope`.
        @param url Input argument for `_is_in_scope`.
        @param host Input argument for `_is_in_scope`.
        @param scope_dir_url Input argument for `_is_in_scope`.
        @return bool Return value of `_is_in_scope`.
        """
        if not is_http_url(url):
            return False
        u = urlparse(url)
        if u.netloc != host:
            return False
        return url.startswith(scope_dir_url)

    def _page_title(self, soup: BeautifulSoup) -> str:
        """
        @brief Execute `_page_title`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_page_title`.
        @param soup Input argument for `_page_title`.
        @return str Return value of `_page_title`.
        """
        t = soup.find("title")
        if t and t.get_text(strip=True):
            return t.get_text(strip=True)
        h1 = soup.find("h1")
        if h1:
            return " ".join(h1.get_text(" ", strip=True).split())
        return "Page"

    def _document_title(self, soup: BeautifulSoup) -> str:
        """
        @brief Execute `_document_title`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_document_title`.
        @param soup Input argument for `_document_title`.
        @return str Return value of `_document_title`.
        """
        title_area = soup.select_one("#titlearea")
        if title_area:
            text = " ".join(title_area.get_text(" ", strip=True).split())
            if text:
                return text

        project_name = soup.select_one("#projectname")
        project_number = soup.select_one("#projectnumber")
        name_text = (
            " ".join(project_name.get_text(" ", strip=True).split())
            if project_name
            else ""
        )
        number_text = (
            " ".join(project_number.get_text(" ", strip=True).split())
            if project_number
            else ""
        )
        combined = " ".join([p for p in (name_text, number_text) if p])
        if combined:
            return combined

        return self._page_title(soup)

    def _extract_main(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        @brief Execute `_extract_main`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_extract_main`.
        @param soup Input argument for `_extract_main`.
        @return BeautifulSoup Return value of `_extract_main`.
        """
        main = soup.select_one("#doc-content")
        if not main:
            main = (
                soup.select_one("div.contents") or soup.select_one("main") or soup.body
            )

        # Remove TOC elements from page content
        self._remove_toc_elements(main)

        frag = BeautifulSoup("", "lxml")
        wrapper = frag.new_tag("div")
        wrapper["class"] = "page-content"
        wrapper.append(BeautifulSoup(str(main), "lxml"))
        frag.append(wrapper)
        return frag

    def _remove_toc_elements(self, soup: BeautifulSoup) -> None:
        """
        @brief Execute `_remove_toc_elements`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_remove_toc_elements`.
        @param soup Input argument for `_remove_toc_elements`.
        @return None Return value of `_remove_toc_elements`.
        """
        if not soup:
            return

        # Remove TOC containers and navigation elements
        toc_selectors = [
            "#nav-tree",
            "#nav-tree-contents",
            ".contents .toc",
            ".PageDoc .toc",
            "#doc-content .toc",
            ".navpath",
            ".directory",
            ".memberdecls .toc",
        ]

        for sel in toc_selectors:
            for elem in list(soup.select(sel)):
                elem.decompose()

    def _links_to_html_pages(
        self, soup: BeautifulSoup, page_url: str, host: str, scope_dir_url: str
    ) -> Set[str]:
        """
        @brief Execute `_links_to_html_pages`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_links_to_html_pages`.
        @param soup Input argument for `_links_to_html_pages`.
        @param page_url Input argument for `_links_to_html_pages`.
        @param host Input argument for `_links_to_html_pages`.
        @param scope_dir_url Input argument for `_links_to_html_pages`.
        @return Set[str] Return value of `_links_to_html_pages`.
        """
        out: Set[str] = set()
        for a in soup.find_all("a"):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            full = normalize_url(href, page_url)
            full, _ = urldefrag(full)
            if full.lower().endswith(".html") and self._is_in_scope(
                full, host, scope_dir_url
            ):
                out.add(full)
        return out

    def _expand_nav_tree(self, page) -> None:
        # Wait for the nav tree to load completely
        """
        @brief Execute `_expand_nav_tree`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_expand_nav_tree`.
        @param page Input argument for `_expand_nav_tree`.
        @return None Return value of `_expand_nav_tree`.
        """
        page.wait_for_selector("#nav-tree-contents ul", timeout=20000)
        page.wait_for_timeout(2000)

        self.log.verbose("[verbose] Iniziando espansione TOC...")

        # Scroll to make sure all content is loaded
        page.evaluate(
            """
            (() => {
                const navTree = document.querySelector('#nav-tree-contents');
                if (navTree) {
                    navTree.scrollTop = 0;
                    navTree.scrollIntoView();
                }
            })();
            """
        )
        page.wait_for_timeout(1000)

        if self.limit:
            self._expand_nav_tree_limited(page, self.limit)
        else:
            self._expand_nav_tree_full(page)

        # Wait for final DOM stabilization
        page.wait_for_timeout(2000)
        self._cleanup_nav_tree_styles(page)

    def _expand_nav_tree_full(self, page) -> None:
        # Track expanded items for limit enforcement
        """
        @brief Execute `_expand_nav_tree_full`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_expand_nav_tree_full`.
        @param page Input argument for `_expand_nav_tree_full`.
        @return None Return value of `_expand_nav_tree_full`.
        """
        expanded_count = 0

        # Expand systematically by clicking on arrows multiple times
        total_clicks = 0
        round_num = -1
        for round_num in range(50):  # Increased rounds for deep nesting
            clicked = page.evaluate(
                f"""
                ((limit, expandedCount) => {{
                    const root = document.querySelector('#nav-tree-contents');
                    if (!root) return {{clicks: 0, expanded: expandedCount}};
                    let clicks = 0;
                    let currentExpanded = expandedCount;

                    // Function to check if an item is an API Reference section or inside one
                    function isApiReferenceRelated(item) {{
                        // Check if this item itself is API Reference
                        const label = item.querySelector('.label');
                        if (label) {{
                            const labelText = label.textContent.trim();
                            if (labelText === 'API Reference') {{
                                console.log('Found API Reference section, skipping expansion');
                                return true;
                            }}
                        }}

                        // Check if we're inside an API Reference section
                        let parent = item.parentElement;
                        while (parent && parent !== root) {{
                            if (parent.classList && parent.classList.contains('children_ul')) {{
                                const parentItem = parent.previousElementSibling;
                                if (parentItem && parentItem.classList && parentItem.classList.contains('item')) {{
                                    const parentLabel = parentItem.querySelector('.label');
                                    if (parentLabel && parentLabel.textContent.trim() === 'API Reference') {{
                                        console.log('Found item inside API Reference section, skipping expansion');
                                        return true;
                                    }}
                                }}
                            }}
                            parent = parent.parentElement;
                        }}
                        return false;
                    }}

                    // Get all items with arrows that might be expandable
                    const items = Array.from(root.querySelectorAll('div.item'));
                    for (const item of items) {{
                        // Check limit before expanding
                        if (limit && currentExpanded >= limit) {{
                            console.log('Reached expansion limit:', limit);
                            break;
                        }}

                        const arrow = item.querySelector('.arrow');
                        if (arrow) {{
                            const text = arrow.textContent.trim();
                            if (text === '►' || text === '▶' || text === '+') {{
                                const label = item.querySelector('.label');
                                const labelText = label ? label.textContent.trim() : 'no-label';
                                console.log('Found expandable item:', labelText);

                                // Skip API Reference sections and their children
                                if (isApiReferenceRelated(item)) {{
                                    console.log('Skipping API Reference related item:', labelText);
                                    continue;
                                }}

                                console.log('Expanding item:', labelText);
                                try {{
                                    arrow.click();
                                    clicks++;
                                    currentExpanded++;
                                }} catch (e) {{
                                    try {{
                                        item.click();
                                        clicks++;
                                        currentExpanded++;
                                    }} catch (e2) {{
                                        // Continue to next item
                                    }}
                                }}
                            }}
                        }}
                    }}

                    return {{clicks: clicks, expanded: currentExpanded}};
                }})({self.limit or "null"}, {expanded_count})
                """
            )

            total_clicks += clicked.get("clicks", 0)
            expanded_count = clicked.get("expanded", expanded_count)

            if round_num % 10 == 0 or clicked.get("clicks", 0) > 0:
                self.log.verbose(
                    f"[verbose] Espansione TOC round {round_num + 1}: {clicked.get('clicks', 0)} click, totale {total_clicks}, espanse {expanded_count}"
                )

            # Stop if limit reached or no more clicks
            if (self.limit and expanded_count >= self.limit) or clicked.get(
                "clicks", 0
            ) == 0:
                if self.limit and expanded_count >= self.limit:
                    self.log.verbose(
                        f"[verbose] Limite espansione raggiunto: {expanded_count}/{self.limit}"
                    )
                break

            # Wait for content to load after clicks
            page.wait_for_timeout(800)

        self.log.verbose(
            f"[verbose] Espansione TOC completata: {total_clicks} click totali in {round_num + 1} round, {expanded_count} voci espanse"
        )
        self.log.debug(
            f"[debug] TOC expansion: completed after {round_num + 1} rounds with {total_clicks} total clicks, {expanded_count} items expanded"
        )

        # Final pass: force expand any remaining collapsed elements, except API Reference
        # Only if we haven't reached the limit
        if not self.limit or expanded_count < self.limit:
            page.evaluate(
                """
                (() => {
                    const root = document.querySelector('#nav-tree-contents');
                    if (!root) return;

                    // Function to check if an item is API Reference related
                    function isApiReferenceRelated(element) {
                        const item = element.closest('div.item');
                        if (!item) return false;

                        // Check if this item itself is API Reference
                        const label = item.querySelector('.label');
                        if (label && label.textContent.trim() === 'API Reference') {
                            return true;
                        }

                        // Check if we're inside an API Reference section
                        let parent = item.parentElement;
                        while (parent && parent !== root) {
                            if (parent.classList && parent.classList.contains('children_ul')) {
                                const parentItem = parent.previousElementSibling;
                                if (parentItem && parentItem.classList && parentItem.classList.contains('item')) {
                                    const parentLabel = parentItem.querySelector('.label');
                                    if (parentLabel && parentLabel.textContent.trim() === 'API Reference') {
                                        return true;
                                    }
                                }
                            }
                            parent = parent.parentElement;
                        }
                        return false;
                    }

                    // Force all arrows to expanded state, except API Reference related
                    const arrows = root.querySelectorAll('.arrow');
                    arrows.forEach(arrow => {
                        if (!isApiReferenceRelated(arrow)) {
                            const text = arrow.textContent.trim();
                            if (text === '►' || text === '▶' || text === '+') {
                                arrow.textContent = '▼';
                            }
                        }
                    });

                    // Force all ul elements to be visible, except those under API Reference
                    // But don't set display: block, leave styles empty to match fixture
                    const uls = root.querySelectorAll('ul');
                    uls.forEach(ul => {
                        if (!isApiReferenceRelated(ul)) {
                            ul.style.visibility = 'visible';
                            ul.style.height = 'auto';
                            ul.style.overflow = 'visible';
                            // Don't set display: block to match fixture expectations
                        }
                    });

                    // Ensure API Reference section is collapsed
                    const items = Array.from(root.querySelectorAll('div.item'));
                    for (const item of items) {
                        const label = item.querySelector('.label');
                        if (label && label.textContent.trim() === 'API Reference') {
                            const arrow = item.querySelector('.arrow');
                            if (arrow) {
                                arrow.textContent = '►'; // Force collapsed state
                            }
                            // Hide children of API Reference
                            const childrenUl = item.parentElement.querySelector('ul.children_ul');
                            if (childrenUl) {
                                childrenUl.style.display = 'none';
                            }
                            break;
                        }
                    }
                })();
                """
            )

    def _expand_nav_tree_limited(self, page, limit: int) -> None:
        """
        @brief Execute `_expand_nav_tree_limited`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_expand_nav_tree_limited`.
        @param page Input argument for `_expand_nav_tree_limited`.
        @param limit Input argument for `_expand_nav_tree_limited`.
        @return None Return value of `_expand_nav_tree_limited`.
        """
        total_clicks = 0

        for round_num in range(120):
            result = page.evaluate(
                """
                (limit) => {
                    const root = document.querySelector('#nav-tree-contents > ul');
                    if (!root) return {expanded: 0, count: 0, reached: false};
                    let expanded = 0;
                    let count = 0;

                    function isApiReferenceRelated(item) {
                        const label = item.querySelector('.label');
                        if (label && label.textContent.trim() === 'API Reference') {
                            return true;
                        }
                        let parent = item.parentElement;
                        while (parent) {
                            if (parent.classList && parent.classList.contains('children_ul')) {
                                const parentItem = parent.previousElementSibling;
                                if (parentItem && parentItem.classList && parentItem.classList.contains('item')) {
                                    const parentLabel = parentItem.querySelector('.label');
                                    if (parentLabel && parentLabel.textContent.trim() === 'API Reference') {
                                        return true;
                                    }
                                }
                            }
                            parent = parent.parentElement;
                        }
                        return false;
                    }

                    function arrowState(arrow) {
                        if (!arrow) return 'leaf';
                        const text = arrow.textContent.trim();
                        if (text === '▼') return 'expanded';
                        if (text === '►' || text === '▶' || text === '+') return 'collapsed';
                        return 'leaf';
                    }

                    function walk(ul) {
                        const items = Array.from(ul.children).filter(el => el.tagName.toLowerCase() === 'li');
                        for (const li of items) {
                            if (count >= limit) return true;
                            const item = li.querySelector(':scope > div.item');
                            if (!item) continue;
                            count += 1;
                            if (count >= limit) return true;

                            const arrow = item.querySelector('.arrow');
                            const state = arrowState(arrow);
                            let didExpand = false;
                            if (state === 'collapsed' && !isApiReferenceRelated(item)) {
                                try {
                                    arrow.click();
                                    expanded += 1;
                                    didExpand = true;
                                } catch (e) {
                                    try {
                                        item.click();
                                        expanded += 1;
                                        didExpand = true;
                                    } catch (e2) {
                                        // ignore
                                    }
                                }
                            }

                            const childUl = li.querySelector(':scope > ul');
                            if (childUl && (state === 'expanded' || didExpand)) {
                                if (walk(childUl)) return true;
                            }
                        }
                        return false;
                    }

                    walk(root);
                    return {expanded: expanded, count: count, reached: count >= limit};
                }
                """,
                limit,
            )

            count = result.get("count", 0) if isinstance(result, dict) else 0
            expanded = result.get("expanded", 0) if isinstance(result, dict) else 0
            total_clicks += expanded

            if round_num % 8 == 0 or expanded > 0:
                self.log.verbose(
                    f"[verbose] Espansione TOC limitata round {round_num + 1}: espanse {expanded}, conteggio {count}/{limit}"
                )

            if expanded == 0:
                break

            page.wait_for_timeout(600)

        self.log.verbose(
            f"[verbose] Espansione TOC limitata completata: {total_clicks} espansioni totali"
        )

    def _cleanup_nav_tree_styles(self, page) -> None:
        """
        @brief Execute `_cleanup_nav_tree_styles`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_cleanup_nav_tree_styles`.
        @param page Input argument for `_cleanup_nav_tree_styles`.
        @return None Return value of `_cleanup_nav_tree_styles`.
        """
        page.evaluate(
            """
            (() => {
                const root = document.querySelector('#nav-tree-contents');
                if (!root) return;

                // Remove display styles from all elements
                const allElements = root.querySelectorAll('*');
                allElements.forEach(el => {
                    if (el.style.display) {
                        el.style.display = '';
                    }
                });

                // Special handling for ul elements - ensure they have empty style
                const uls = root.querySelectorAll('ul');
                uls.forEach(ul => {
                    ul.removeAttribute('style');
                    ul.setAttribute('style', '');
                });
            })();
            """
        )

    def _fetch_nav_tree_with_playwright(self) -> Tuple[str, str]:
        """
        @brief Execute `_fetch_nav_tree_with_playwright`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_fetch_nav_tree_with_playwright`.
        @return Tuple[str, str] Return value of `_fetch_nav_tree_with_playwright`.
        """
        nav_html = ""
        nav_outline = ""
        self.log.verbose("[verbose] Avvio estrazione TOC con Playwright...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context_args = {}
                ua = (
                    self.session.headers.get("User-Agent")
                    if hasattr(self, "session")
                    else None
                )
                if ua:
                    context_args["user_agent"] = ua
                context = browser.new_context(**context_args)
                page = context.new_page()

                self.log.verbose("[verbose] Caricamento pagina per estrazione TOC...")
                page.goto(self.from_url, wait_until="networkidle")
                page.wait_for_selector("#nav-tree-contents ul", timeout=20000)

                self._expand_nav_tree(page)

                self.log.verbose("[verbose] Estrazione HTML della TOC espansa...")
                nav_html = (
                    page.evaluate(
                        """
                    (() => { 
                        const el = document.querySelector('#nav-tree-contents ul'); 
                        if (!el) return '';
                        
                        // Clone the element to avoid modifying the original
                        const clone = el.cloneNode(true);
                        
                        // Clean up extra styles added during expansion
                        const uls = clone.querySelectorAll('ul');
                        uls.forEach(ul => {
                            ul.style.visibility = '';
                            ul.style.height = '';
                            ul.style.overflow = '';
                        });
                        
                        // Also clean up the root element itself
                        if (clone.style) {
                            clone.style.visibility = '';
                            clone.style.height = '';
                            clone.style.overflow = '';
                        }
                        
                        // Remove only the expansion arrow links (those with arrow spans as siblings)
                        // Actually, let's not remove any javascript:void(0) links for now
                        // The fixture expects them to be preserved
                        
                        
                        return clone.outerHTML;
                    })()
                    """
                    )
                    or ""
                )

                self.log.debug(
                    f"[debug] TOC HTML extracted: {len(nav_html)} characters"
                )
                browser.close()

        except Exception as e:
            self.log.debug(f"[debug] TOC extraction failed: {str(e)}")
            nav_html = ""

        if nav_html:
            nav_outline = nav_outline_from_html(nav_html)
            self.log.verbose(
                f"[verbose] TOC outline generato: {len(nav_outline.splitlines())} righe"
            )
            self.log.debug(
                f"[debug] TOC extraction successful: HTML={len(nav_html)} chars, outline={len(nav_outline.splitlines())} lines"
            )
        else:
            self.log.debug("[debug] TOC extraction failed: no HTML captured")

        return nav_html, nav_outline

    def _nav_link_href(self, link, base_url: str) -> str:
        """
        @brief Execute `_nav_link_href`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_nav_link_href`.
        @param link Input argument for `_nav_link_href`.
        @param base_url Input argument for `_nav_link_href`.
        @return str Return value of `_nav_link_href`.
        """
        if not link:
            return ""
        href = (link.get("href") or "").strip()
        if href and href.lower() != "javascript:void(0)":
            return normalize_url(href, base_url)

        for cls in link.get("class") or []:
            if ".html" not in cls:
                continue
            if ":" in cls:
                page, frag = cls.split(":", 1)
                if page:
                    return normalize_url(f"{page}#{frag}" if frag else page, base_url)
            else:
                return normalize_url(cls, base_url)
        return ""

    def _toc_tree_from_html(self, toc_html: str) -> List[TocNode]:
        """
        @brief Execute `_toc_tree_from_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_toc_tree_from_html`.
        @param toc_html Input argument for `_toc_tree_from_html`.
        @return List[TocNode] Return value of `_toc_tree_from_html`.
        """
        return toc_from_nav_html(toc_html, "document.html")

    def _toc_nodes_from_nav_html(self, nav_html: str) -> List[TocNode]:
        """
        @brief Execute `_toc_nodes_from_nav_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_toc_nodes_from_nav_html`.
        @param nav_html Input argument for `_toc_nodes_from_nav_html`.
        @return List[TocNode] Return value of `_toc_nodes_from_nav_html`.
        """
        soup = BeautifulSoup(nav_html or "", "lxml")
        root_ul = soup.find("ul")
        if not root_ul:
            return []

        def parse_ul(ul) -> List[TocNode]:
            """
            @brief Execute `parse_ul`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param ul Input argument for `parse_ul`.
            @return List[TocNode] Return value of `parse_ul`.
            """
            items: List[TocNode] = []
            for li in ul.find_all("li", recursive=False):
                label = li.select_one(":scope > div .label a") or li.select_one(
                    ":scope > span.label a"
                )
                if not label:
                    continue
                title = " ".join(label.get_text(" ", strip=True).split())
                if not title:
                    continue
                href = self._nav_link_href(label, self.from_url)
                node = TocNode(title=title, href=href)
                child_ul = li.find("ul", recursive=False)
                if child_ul:
                    node.children = parse_ul(child_ul)
                items.append(node)
            return items

        nodes = parse_ul(root_ul)
        if len(nodes) == 1 and nodes[0].children:
            return nodes[0].children
        return nodes

    @staticmethod
    def _iter_toc_nodes(nodes: List[TocNode]) -> Iterable[TocNode]:
        """
        @brief Execute `_iter_toc_nodes`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param nodes Input argument for `_iter_toc_nodes`.
        @return Iterable[TocNode] Return value of `_iter_toc_nodes`.
        """
        for n in nodes:
            yield n
            yield from DoxygenExportDownloader._iter_toc_nodes(n.children)

    def _select_main_container(self, soup: BeautifulSoup):
        """
        @brief Execute `_select_main_container`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_select_main_container`.
        @param soup Input argument for `_select_main_container`.
        @return Any Return value of `_select_main_container`.
        """
        if not soup:
            return None
        main = (
            soup.select_one("div.contents div.textblock")
            or soup.select_one("div.contents")
            or soup.select_one("#doc-content")
        )
        if not main:
            main = soup.select_one("main") or soup.body
        if not main:
            return None
        self._remove_toc_elements(main)
        return main

    def _find_fragment_anchor(self, main, fragment: str):
        """
        @brief Execute `_find_fragment_anchor`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_find_fragment_anchor`.
        @param main Input argument for `_find_fragment_anchor`.
        @param fragment Input argument for `_find_fragment_anchor`.
        @return Any Return value of `_find_fragment_anchor`.
        """
        frag = (fragment or "").strip()
        if not frag or not main:
            return None
        target = main.find(id=frag) or main.find(attrs={"name": frag})
        if not target:
            return None
        if target.name and re.match(r"^h[1-6]$", target.name):
            return target
        if target.name == "a":
            parent = target.parent
            if parent and parent.name and re.match(r"^h[1-6]$", parent.name):
                return parent
            next_heading = target.find_next(re.compile(r"^h[1-6]$"))
            if next_heading and (
                next_heading.get("id") == frag or next_heading.find(id=frag)
            ):
                return next_heading
        return target

    @staticmethod
    def _normalize_heading_text(value: str) -> str:
        """
        @brief Execute `_normalize_heading_text`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param value Input argument for `_normalize_heading_text`.
        @return str Return value of `_normalize_heading_text`.
        """
        return " ".join((value or "").split()).strip().lower()

    def _strip_duplicate_section_title(
        self, container, title: str, section_anchor: str
    ) -> Optional[str]:
        """
        @brief Execute `_strip_duplicate_section_title`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_strip_duplicate_section_title`.
        @param container Input argument for `_strip_duplicate_section_title`.
        @param title Input argument for `_strip_duplicate_section_title`.
        @param section_anchor Input argument for `_strip_duplicate_section_title`.
        @return Optional[str] Return value of `_strip_duplicate_section_title`.
        """
        target = self._normalize_heading_text(title)
        if not target or not container:
            return None

        heading_re = re.compile(r"^h[1-6]$")
        preserved_id = None

        matching_heading = None
        for heading in container.find_all(heading_re):
            if (
                self._normalize_heading_text(heading.get_text(" ", strip=True))
                == target
            ):
                matching_heading = heading
                break
        if matching_heading:
            hid = (matching_heading.get("id") or "").strip()
            if hid:
                preserved_id = hid
            matching_heading.decompose()

        for title_el in container.select(".headertitle .title, .header .title"):
            if (
                self._normalize_heading_text(title_el.get_text(" ", strip=True))
                == target
            ):
                title_el.decompose()

        if preserved_id and preserved_id != section_anchor:
            return preserved_id
        return None

    def _extract_section_html(
        self, soup: BeautifulSoup, fragment: str, next_fragment: Optional[str]
    ) -> str:
        """
        @brief Execute `_extract_section_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_extract_section_html`.
        @param soup Input argument for `_extract_section_html`.
        @param fragment Input argument for `_extract_section_html`.
        @param next_fragment Input argument for `_extract_section_html`.
        @return str Return value of `_extract_section_html`.
        """
        main = self._select_main_container(soup)
        if not main:
            return ""

        children = [
            child
            for child in main.contents
            if not (isinstance(child, str) and not child.strip())
        ]
        if not children:
            return str(main)

        start_el = self._find_fragment_anchor(main, fragment) if fragment else None
        end_el = (
            self._find_fragment_anchor(main, next_fragment) if next_fragment else None
        )

        def direct_child(el):
            """
            @brief Execute `direct_child`.
            @details Implements deterministic control flow as defined by module runtime semantics.
            @param el Input argument for `direct_child`.
            @return Any Return value of `direct_child`.
            """
            cur = el
            while cur and cur.parent and cur.parent != main:
                cur = cur.parent
            return cur if cur and cur.parent == main else None

        start_block = direct_child(start_el) if start_el else None
        if not start_block:
            start_block = children[0]

        end_block = direct_child(end_el) if end_el else None

        try:
            start_idx = children.index(start_block)
        except ValueError:
            return str(main)

        end_idx = len(children)
        if end_block:
            try:
                candidate = children.index(end_block)
                if candidate > start_idx:
                    end_idx = candidate
            except ValueError:
                pass

        sliced = children[start_idx:end_idx]
        return "".join(str(child) for child in sliced)

    def _build_toc(self, doc: BeautifulSoup) -> List[TocNode]:
        """
        @brief Execute `_build_toc`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_build_toc`.
        @param doc Input argument for `_build_toc`.
        @return List[TocNode] Return value of `_build_toc`.
        """
        nodes: List[TocNode] = []
        container = doc.select_one("#offline-doc")
        if not container:
            return nodes

        # Track content by hash to consolidate duplicates
        content_to_anchor: Dict[str, str] = {}

        for sec in container.find_all("section", recursive=False):
            title_el = sec.find(re.compile(r"^h[1-6]$"))
            title = (
                " ".join(title_el.get_text(" ", strip=True).split())
                if title_el
                else "Pagina"
            )
            section_id = sec.get("id", "")
            href = f"#{section_id}" if section_id else "#"

            # Create content hash for deduplication
            content_text = " ".join(sec.get_text(" ", strip=True).split())
            content_hash = str(hash(content_text))

            if content_hash in content_to_anchor:
                # Duplicate content - point to existing anchor
                existing_anchor = content_to_anchor[content_hash]
                page_node = TocNode(title=title or "Pagina", href=f"#{existing_anchor}")
            else:
                # New content - use this section's anchor
                content_to_anchor[content_hash] = section_id
                page_node = TocNode(title=title or "Pagina", href=href)

            child_nodes: List[TocNode] = []
            stack: List[Tuple[int, TocNode]] = []
            for h in sec.find_all(re.compile(r"^h[2-6]$")):
                if title_el is not None and h is title_el:
                    continue
                hid = h.get("id")
                if not hid:
                    continue
                h_title = " ".join(h.get_text(" ", strip=True).split())
                if not h_title:
                    continue
                level = int(h.name[1])
                node = TocNode(title=h_title, href=f"#{hid}")
                while stack and stack[-1][0] >= level:
                    stack.pop()
                if stack:
                    stack[-1][1].children.append(node)
                else:
                    child_nodes.append(node)
                stack.append((level, node))

            page_node.children = child_nodes
            nodes.append(page_node)

        return nodes

    def run(self) -> None:
        """
        @brief Execute `run`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `run`.
        @return None Return value of `run`.
        """
        host, scope_dir_url = self._scope()

        index_soup = self._fetch_soup(self.from_url)
        document_title = self._document_title(index_soup)

        nav_html, nav_outline = self._fetch_nav_tree_with_playwright()

        if self.toc_only:
            if nav_html:
                (self.out_dir / "toc_raw.html").write_text(nav_html, encoding="utf-8")
            if nav_outline:
                (self.out_dir / "toc_raw.txt").write_text(nav_outline, encoding="utf-8")
            self.log.check("[check] TOC-only mode: skipped document download")
            return

        self.log.debug("[debug] doxygen-export: starting crawl")

        if self.limit and nav_html:
            toc_nodes = self._toc_nodes_from_nav_html(nav_html)
            toc_nodes = limit_toc_nodes(toc_nodes, self.limit)
            flat_nodes = list(self._iter_toc_nodes(toc_nodes))
            if flat_nodes:
                self.log.verbose(
                    f"[verbose] TOC limitata a {len(flat_nodes)} voci in ordine di lettura"
                )

                entries: List[Tuple[TocNode, str, str, str]] = []
                page_fragments: Dict[str, List[str]] = {}
                for node in flat_nodes:
                    raw_href = (node.href or "").strip()
                    full_href = (
                        normalize_url(raw_href, self.from_url)
                        if raw_href
                        else self.from_url
                    )
                    page_url, frag = urldefrag(full_href)
                    page_url = page_url or self.from_url
                    frag = frag or ""
                    entries.append((node, page_url, frag, node.title))
                    page_fragments.setdefault(page_url, []).append(frag)

                pages_by_url: Dict[str, BeautifulSoup] = {}
                for page_url in sorted(page_fragments.keys()):
                    try:
                        pages_by_url[page_url] = self._fetch_soup(page_url)
                        self.log.debug(f"[debug] Fetched TOC page: {page_url}")
                    except Exception as e:
                        self.log.debug(
                            f"[debug] Failed to fetch TOC page {page_url}: {str(e)}"
                        )
                        pages_by_url[page_url] = BeautifulSoup("", "lxml")

                doc = BeautifulSoup("", "lxml")
                container = doc.new_tag("div")
                container["id"] = "offline-doc"
                doc.append(container)

                content_hashes: Dict[str, str] = {}
                duplicates_skipped = 0
                page_positions = {url: 0 for url in page_fragments}

                self.log.verbose(
                    "[verbose] Costruzione documento unificato da TOC limitata..."
                )

                for idx, (node, page_url, frag, title) in enumerate(entries, start=1):
                    pos = page_positions[page_url]
                    frag_list = page_fragments[page_url]
                    next_frag = None
                    if pos + 1 < len(frag_list):
                        next_frag = frag_list[pos + 1] or None
                    page_positions[page_url] = pos + 1

                    psoup = pages_by_url.get(page_url)
                    section_html = self._extract_section_html(psoup, frag, next_frag)
                    section_soup = BeautifulSoup(section_html, "lxml")
                    anchor = f"page-{idx}"
                    section_container = section_soup.body or section_soup
                    preserved_id = self._strip_duplicate_section_title(
                        section_container, title, anchor
                    )
                    section_text = " ".join(
                        section_soup.get_text(" ", strip=True).split()
                    )

                    content_hash = ""
                    if section_text:
                        content_hash = str(hash(section_text))
                        if content_hash in content_hashes:
                            node.href = f"#{content_hashes[content_hash]}"
                            duplicates_skipped += 1
                            self.log.debug(
                                f"[debug] Duplicate TOC entry skipped at {idx}: {title}"
                            )
                            continue

                    if section_text:
                        content_hashes[content_hash] = anchor
                    node.href = f"#{anchor}"

                    sec = doc.new_tag("section")
                    sec["id"] = anchor
                    h1 = doc.new_tag("h1")
                    h1.string = title or "Pagina"
                    if preserved_id:
                        h1["id"] = preserved_id
                    sec.append(h1)

                    for child in list(section_container.children):
                        sec.append(child)
                    container.append(sec)

                self.log.verbose(
                    f"[verbose] Documento da TOC limitata: {len(container.find_all('section'))} sezioni, {duplicates_skipped} duplicati saltati"
                )

                ensure_heading_ids(doc)

                if document_title:
                    title_tag = doc.new_tag("p")
                    title_tag["class"] = "document-title"
                    title_tag.string = document_title
                    container.insert_before(title_tag)

                # Download assets from the touched pages
                asset_urls: Set[str] = set()
                for page_url, psoup in pages_by_url.items():
                    page_assets = iter_asset_urls(psoup, page_url)
                    asset_urls |= page_assets
                    self.log.debug(
                        f"[debug] Found {len(page_assets)} assets in {page_url}"
                    )

                self.log.verbose(f"[verbose] Download di {len(asset_urls)} asset...")
                for u in tqdm(
                    sorted(asset_urls), desc="Downloading assets", unit="file"
                ):
                    lp = local_path_for_url(u, self.out_dir)
                    if not lp.exists():
                        success = download_one(self.session, u, lp)
                        if not success:
                            self.log.debug(f"[debug] Asset download failed: {u}")

                self.log.verbose(
                    f"[verbose] Asset download completato: {len(asset_urls)} file"
                )
                self.log.debug(
                    f"[debug] Assets totali scaricati o riusati: {len(asset_urls)}"
                )

                rewrite_asset_links_inplace(doc, scope_dir_url, self.out_dir)
                strip_styles(doc)

                self.log.check("[check] Generating document.html")
                doc_html = minimal_readable_wrapper(
                    str(doc), title=document_title or "Documento (offline)"
                )
                (self.out_dir / "document.html").write_text(doc_html, encoding="utf-8")
                self.log.check("[check] Generating toc.html")
                (self.out_dir / "toc.html").write_text(
                    build_toc_html(
                        toc_nodes, document_filename="document.html", target_frame="doc"
                    ),
                    encoding="utf-8",
                )
                self.log.check("[check] Generating index.html")
                (self.out_dir / "index.html").write_text(
                    build_frameset_index(
                        toc_filename="toc.html", document_filename="document.html"
                    ),
                    encoding="utf-8",
                )
                self.post_process()
                return
            else:
                self.log.debug(
                    "[debug] TOC limitata vuota, fallback al crawling completo"
                )

        # Crawl pages
        MAX_PAGES = 250
        queue: List[str] = [urldefrag(self.from_url)[0]]
        seen: Set[str] = set()
        pages: List[Tuple[str, BeautifulSoup]] = []

        self.log.verbose("[verbose] Iniziando crawling delle pagine...")

        while queue and len(seen) < MAX_PAGES:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)

            if len(seen) % 10 == 1 or len(seen) <= 5:
                self.log.verbose(
                    f"[verbose] Download pagina {len(seen)}/{MAX_PAGES}: {url}"
                )

            try:
                psoup = self._fetch_soup(url)
                pages.append((url, psoup))
                self.log.debug(
                    f"[debug] Page {len(seen)} downloaded successfully: {len(str(psoup))} chars"
                )
            except Exception as e:
                self.log.debug(f"[debug] Page {len(seen)} download failed: {str(e)}")
                continue

            for nxt in sorted(
                self._links_to_html_pages(psoup, url, host, scope_dir_url)
            ):
                if nxt not in seen and (len(queue) + len(seen) < MAX_PAGES):
                    queue.append(nxt)

        self.log.verbose(
            f"[verbose] Crawling completato: {len(pages)} pagine scaricate"
        )
        self.log.debug(
            f"[debug] doxygen-export: crawled {len(pages)} pages (limit {MAX_PAGES})"
        )

        if self.limit:
            original_count = len(pages)
            pages = pages[: self.limit]
            self.log.verbose(
                f"[verbose] Applicato limite: {len(pages)}/{original_count} pagine"
            )
            self.log.debug(
                f"[debug] Applied limit: kept {len(pages)} of {original_count} pages"
            )

        # Build unified doc with robust anchors and content deduplication
        doc = BeautifulSoup("", "lxml")
        container = doc.new_tag("div")
        container["id"] = "offline-doc"
        doc.append(container)

        content_hashes: Dict[str, str] = {}  # content_hash -> anchor
        duplicates_skipped = 0

        self.log.verbose("[verbose] Costruzione documento unificato...")

        for i, (url, psoup) in enumerate(pages, start=1):
            title = self._page_title(psoup)
            anchor = f"page-{i}"

            main = self._extract_main(psoup)
            preserved_id = self._strip_duplicate_section_title(main, title, anchor)
            content_text = " ".join(main.get_text(" ", strip=True).split())
            content_hash = str(hash(content_text))

            # Skip duplicate content
            if content_hash in content_hashes:
                duplicates_skipped += 1
                self.log.debug(
                    f"[debug] Skipped duplicate content for page {i}: {title} (hash: {content_hash[:8]}...)"
                )
                continue

            content_hashes[content_hash] = anchor

            sec = doc.new_tag("section")
            sec["id"] = anchor
            h1 = doc.new_tag("h1")
            h1.string = title
            if preserved_id:
                h1["id"] = preserved_id
            sec.append(h1)

            sec.append(BeautifulSoup(str(main), "lxml"))
            container.append(sec)

            if i % 20 == 0 or i <= 10:
                self.log.verbose(
                    f"[verbose] Aggiunta sezione {i}/{len(pages)}: {anchor} -> {title}"
                )
            self.log.debug(
                f"[debug] Added section {anchor}: {title} ({len(content_text)} chars, hash: {content_hash[:8]}...)"
            )

        self.log.verbose(
            f"[verbose] Documento costruito: {len(container.find_all('section'))} sezioni, {duplicates_skipped} duplicati saltati"
        )
        self.log.debug(
            f"[debug] Document built: {len(container.find_all('section'))} sections, {duplicates_skipped} duplicates skipped"
        )

        ensure_heading_ids(doc)

        if document_title:
            title_tag = doc.new_tag("p")
            title_tag["class"] = "document-title"
            title_tag.string = document_title
            container.insert_before(title_tag)

        toc_nodes = self._build_toc(doc)
        toc_nodes = limit_toc_nodes(toc_nodes, self.limit)
        self.log.verbose(
            f"[verbose] TOC generata con {len(toc_nodes)} voci di primo livello"
        )
        self.log.debug(
            f"[debug] TOC built: {len(toc_nodes)} top-level entries, limit={self.limit}"
        )

        # Download assets from all pages
        asset_urls: Set[str] = set()
        for url, psoup in pages:
            page_assets = iter_asset_urls(psoup, url)
            asset_urls |= page_assets
            self.log.debug(f"[debug] Found {len(page_assets)} assets in {url}")

        self.log.verbose(f"[verbose] Download di {len(asset_urls)} asset...")

        for u in tqdm(sorted(asset_urls), desc="Downloading assets", unit="file"):
            lp = local_path_for_url(u, self.out_dir)
            if not lp.exists():
                success = download_one(self.session, u, lp)
                if not success:
                    self.log.debug(f"[debug] Asset download failed: {u}")

        self.log.verbose(f"[verbose] Asset download completato: {len(asset_urls)} file")
        self.log.debug(f"[debug] Assets totali scaricati o riusati: {len(asset_urls)}")

        # Rewrite to local
        rewrite_asset_links_inplace(doc, scope_dir_url, self.out_dir)

        # Remove stylesheet references and inline styles
        strip_styles(doc)

        # Output
        self.log.check("[check] Generating document.html")
        doc_html = minimal_readable_wrapper(
            str(doc), title=document_title or "Documento (offline)"
        )
        (self.out_dir / "document.html").write_text(doc_html, encoding="utf-8")
        self.log.check("[check] Generating toc.html")
        (self.out_dir / "toc.html").write_text(
            build_toc_html(
                toc_nodes, document_filename="document.html", target_frame="doc"
            ),
            encoding="utf-8",
        )
        self.log.check("[check] Generating index.html")
        (self.out_dir / "index.html").write_text(
            build_frameset_index(
                toc_filename="toc.html", document_filename="document.html"
            ),
            encoding="utf-8",
        )

        self.post_process()


# ----------------------------
# Resource Explorer downloader
# ----------------------------


class ResourceExplorerModule:
    """
    @brief Define class `ResourceExplorerModule`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    name: str = "base"

    def select(
        self, url: str, html: str, soup: Optional[BeautifulSoup]
    ) -> Optional[Dict[str, str]]:
        """
        @brief Execute `select`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `select`.
        @param url Input argument for `select`.
        @param html Input argument for `select`.
        @param soup Input argument for `select`.
        @return Optional[Dict[str, str]] Return value of `select`.
        """
        return None

    def run(self, downloader: "ResourceExplorerDownloader", selection: Dict[str, str]) -> None:
        """
        @brief Execute `run`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `run`.
        @param downloader Input argument for `run`.
        @param selection Input argument for `run`.
        @return None Return value of `run`.
        """
        raise NotImplementedError


class RMModuleDoxigen(ResourceExplorerModule):
    """
    @brief Define class `RMModuleDoxigen`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    name = "RMModuleDoxigen"
    _CONTAINER_SELECTOR = "div.css-1aefuid-contentContainer"
    _BASE_URL = "https://dev.ti.com/tirex/explore/"

    def select(
        self, url: str, html: str, soup: Optional[BeautifulSoup]
    ) -> Optional[Dict[str, str]]:
        """
        @brief Execute `select`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `select`.
        @param url Input argument for `select`.
        @param html Input argument for `select`.
        @param soup Input argument for `select`.
        @return Optional[Dict[str, str]] Return value of `select`.
        """
        if not soup:
            return None
        iframe = soup.select_one(
            f"{self._CONTAINER_SELECTOR} iframe[src], {self._CONTAINER_SELECTOR} frame[src]"
        )
        if not iframe:
            return None
        src = (iframe.get("src") or "").strip()
        if not src:
            return None
        doxygen_url = urljoin(self._BASE_URL, src)
        return {"doxygen_url": doxygen_url}

    def run(self, downloader: "ResourceExplorerDownloader", selection: Dict[str, str]) -> None:
        """
        @brief Execute `run`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `run`.
        @param downloader Input argument for `run`.
        @param selection Input argument for `run`.
        @return None Return value of `run`.
        """
        doxygen_url = selection.get("doxygen_url") or ""
        if not doxygen_url:
            raise RuntimeError("Modulo RMModuleDoxigen: URL Doxygen non valida.")
        downloader.log.info(f"[i] Resource module: {self.name}")
        inner = DoxygenExportDownloader(
            doxygen_url,
            downloader.out_dir,
            downloader.session,
            logger=downloader.log,
            limit=downloader.limit,
            disable_numbering=downloader.disable_numbering,
        )
        inner.run()


class ResourceExplorerDownloader(BaseDownloader):
    """
    @brief Define class `ResourceExplorerDownloader`.
    @details Encapsulates behavior used by downloader orchestration and processing pipeline.
    """
    name = "resource-explorer"

    def __init__(self, *args, **kwargs):
        """
        @brief Execute `__init__`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `__init__`.
        @param *args Input argument for `__init__`.
        @param **kwargs Input argument for `__init__`.
        @return Any Return value of `__init__`.
        """
        super().__init__(*args, **kwargs)
        self.modules: List[ResourceExplorerModule] = [RMModuleDoxigen()]

    @classmethod
    def matches_url(cls, url: str) -> bool:
        """
        @brief Execute `matches_url`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param cls Input argument for `matches_url`.
        @param url Input argument for `matches_url`.
        @return bool Return value of `matches_url`.
        """
        u = urlparse(url)
        return u.netloc.endswith("dev.ti.com") and "/tirex/explore/node" in u.path.lower()

    @classmethod
    def probe_html(cls, url: str, html: str) -> bool:
        """
        @brief Execute `probe_html`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param cls Input argument for `probe_html`.
        @param url Input argument for `probe_html`.
        @param html Input argument for `probe_html`.
        @return bool Return value of `probe_html`.
        """
        return "css-1aefuid-contentContainer" in (html or "")

    def _select_module(
        self, html: str, soup: Optional[BeautifulSoup]
    ) -> Optional[Tuple[ResourceExplorerModule, Dict[str, str]]]:
        """
        @brief Execute `_select_module`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_select_module`.
        @param html Input argument for `_select_module`.
        @param soup Input argument for `_select_module`.
        @return Optional[Tuple[ResourceExplorerModule, Dict[str, str]]] Return value of `_select_module`.
        """
        for module in self.modules:
            selection = module.select(self.from_url, html, soup)
            if selection:
                return module, selection
        return None

    def _render_with_playwright(self) -> str:
        """
        @brief Execute `_render_with_playwright`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `_render_with_playwright`.
        @return str Return value of `_render_with_playwright`.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context_args = {}
                ua = (
                    self.session.headers.get("User-Agent")
                    if hasattr(self, "session")
                    else None
                )
                if ua:
                    context_args["user_agent"] = ua
                context = browser.new_context(**context_args)
                page = context.new_page()
                page.set_default_timeout(60_000)
                try:
                    page.goto(self.from_url, wait_until="networkidle")
                except PlaywrightTimeoutError:
                    page.goto(self.from_url, wait_until="domcontentloaded")
                try:
                    page.wait_for_selector(
                        "div.css-1aefuid-contentContainer iframe[src], div.css-1aefuid-contentContainer frame[src]",
                        timeout=20_000,
                    )
                except PlaywrightTimeoutError:
                    pass
                html = page.content()
                browser.close()
                return html
        except Exception:
            return ""

    def run(self) -> None:
        """
        @brief Execute `run`.
        @details Implements deterministic control flow as defined by module runtime semantics.
        @param self Input argument for `run`.
        @return None Return value of `run`.
        """
        try:
            r = self.session.get(self.from_url, timeout=30, allow_redirects=True)
            r.raise_for_status()
            html = r.text
        except Exception as exc:
            raise RuntimeError("Impossibile scaricare la pagina Resource Explorer.") from exc

        soup = BeautifulSoup(html, "lxml")
        chosen = self._select_module(html, soup)
        if chosen:
            module, selection = chosen
            module.run(self, selection)
            return

        self.log.verbose(
            "[verbose] Resource Explorer: fallback a Playwright per caricare iframe"
        )
        rendered_html = self._render_with_playwright()
        rendered_soup = BeautifulSoup(rendered_html, "lxml") if rendered_html else None
        chosen = self._select_module(rendered_html, rendered_soup)
        if chosen:
            module, selection = chosen
            module.run(self, selection)
            return

        raise RuntimeError("Nessun modulo Resource Explorer compatibile trovato.")


# ----------------------------
# Main
# ----------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    """
    @brief Execute `build_arg_parser`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @return argparse.ArgumentParser Return value of `build_arg_parser`.
    """
    ap = VersionedArgumentParser(prog="htmldownloader", version=__version__)
    ap.add_argument(
        "--version",
        "--ver",
        action="version",
        version=__version__,
    )
    ap.add_argument(
        "--upgrade",
        action=UpgradeAction,
        nargs=0,
        help="Aggiorna il pacchetto htmldownloader via pip e termina",
    )
    ap.add_argument("--from-url", required=True)
    ap.add_argument("--to-dir", required=True)
    ap.add_argument(
        "--user-agent", default="Mozilla/5.0 (X11; Linux x86_64) htmldownloader/1.0"
    )
    ap.add_argument(
        "--limit",
        type=positive_int,
        default=None,
        help="Limita TOC e sezioni a <max> voci",
    )
    ap.add_argument(
        "--verbose", action="store_true", help="Stampa avanzamento download e check"
    )
    ap.add_argument(
        "--debug",
        action="store_true",
        help="Abilita log dettagliati e include il verbose",
    )
    ap.add_argument(
        "--disable-numbering",
        action="store_true",
        help="Disabilita l'aggiunta del numbering in toc.html/document.html (mantiene la rimozione dei prefissi)",
    )
    return ap


def print_strict_help(program: str, version: str, parser: argparse.ArgumentParser) -> None:
    """
    @brief Execute `print_strict_help`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @param program Input argument for `print_strict_help`.
    @param version Input argument for `print_strict_help`.
    @param parser Input argument for `print_strict_help`.
    @return None Return value of `print_strict_help`.
    """
    # Header
    print(f"{program} ({version})")
    print()

    # Usage
    print("Usage:")
    print(f"  {program} [--help] [--version|--ver] [--verbose] [--debug]")
    print()

    # Example(s)
    print("Example/Examples:")
    print(f"  {program} --from-url http://foo.bar --to-dir foo-bar/ --verbose")
    print()

    # Fixed core options block
    print("Options:")
    print("  -h, --help            Show this help message and exit")
    print("  --version, --ver      Print the program version and exit")
    print("  --verbose             Verbose progress logs")
    print("  --debug               Debug logs + extra artifacts")

    # Generate full list of options from parser._actions (avoid duplicates)
    seen_opts: Set[str] = set(["-h", "--help", "--version", "--ver", "--verbose", "--debug"])
    # Collect actions in insertion order
    actions = [a for a in getattr(parser, "_actions", [])]
    for a in actions:
        # Skip the help/version that we've already printed
        opt_strings = [s for s in a.option_strings if s not in seen_opts]
        if not opt_strings:
            continue
        seen_opts.update(opt_strings)
        opt_display = ", ".join(opt_strings)
        help_text = (a.help or "").strip()
        # Align to match typical formatting
        print(f"  {opt_display.ljust(22)} {help_text}")


def main() -> int:
    """
    @brief Execute `main`.
    @details Implements deterministic control flow as defined by module runtime semantics.
    @return int Return value of `main`.
    """
    ap = build_arg_parser()
    # If executed with no parameters or with -h/--help, print strict help and exit 0
    if len(sys.argv) == 1 or any(s in ("-h", "--help") for s in sys.argv[1:]):
        print_strict_help(ap.prog, __version__, ap)
        return 0

    args = ap.parse_args()

    check_for_new_version(ap.prog, __version__)

    from_url = args.from_url.strip()
    out_dir = Path(args.to_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    limit = args.limit

    logger = Logger(verbose=bool(args.verbose or args.debug), debug=bool(args.debug))

    session = requests.Session()
    session.headers.update({"User-Agent": args.user_agent})

    registry = DownloaderRegistry()
    registry.register(ResourceExplorerDownloader)
    registry.register(DocumentViewerDownloader)
    registry.register(DoxygenExportDownloader)

    dl_cls = registry.detect(from_url, session)
    downloader = dl_cls(
        from_url,
        out_dir,
        session,
        logger=logger,
        limit=limit,
        disable_numbering=bool(args.disable_numbering),
    )

    logger.info(f"[i] Using downloader: {downloader.name}")
    downloader.run()

    logger.info("[ok] Saved:")
    logger.info(f"  - {out_dir / 'toc.html'}")
    logger.info(f"  - {out_dir / 'index.html'}")
    logger.info(f"  - {out_dir / 'document.html'}")
    logger.info(f"  - {out_dir / 'assets'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
