from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import List, Tuple

from ..ir import Document, Edit, Node, MD_DOC, MD_HEADING
from ..ir import assign_ids, flatten
from ..markers import DEFAULT_OPTIONS, make_omission_line
from ..utils import line_starts, slugify


_ATX_RE = re.compile(
    r"^(?P<prefix>[ \t>]*)(?P<Hashes>#{1,6})[ \t]+(?P<title>.+?)[ \t]*#*[ \t]*$"
)


def _scan_headings_excluding_fences_and_blockquotes(
    text: str,
) -> List[Tuple[int, int, str]]:
    """
    Return a list of (level, start_line_index, title) for ATX headings (# .. ######),
    ignoring:
      - fenced code blocks delimited by backticks ``` or tildes ~~~ (3+)
      - headings that are inside blockquotes (> ...)
    start_line_index is 0-based.
    """
    lines = text.splitlines()
    n = len(lines)
    in_fence = False
    fence_char = ""
    fence_len = 0

    def _fence_open_close(s: str) -> int:
        """
        If 's' starts with an opening/closing fence (```... or ~~~... with length>=3),
        return the fence length (>=3); else 0. Leading spaces/tabs allowed.
        """
        m = re.match(r"^[ \t]*(```+|~~~+)", s)
        if not m:
            return 0
        token = m.group(1)
        return len(token)

    out: List[Tuple[int, int, str]] = []
    for i, raw in enumerate(lines):
        # Detect fence boundaries
        flen = _fence_open_close(raw)
        if flen >= 3:
            token = raw.lstrip()[0]
            if not in_fence:
                in_fence = True
                fence_char = token
                fence_len = flen
            else:
                # close only if same fence char and length >= opening
                if token == fence_char and flen >= fence_len:
                    in_fence = False
                    fence_char = ""
                    fence_len = 0
            # The fence line itself cannot be a heading
            continue

        if in_fence:
            continue

        m = _ATX_RE.match(raw)
        if not m:
            continue

        # Ignore headings inside blockquotes (any '>' before the hashes)
        prefix = m.group("prefix") or ""
        if ">" in prefix.replace(" ", "").replace("\t", ""):
            continue

        hashes = m.group("Hashes")
        title = (m.group("title") or "").strip()
        if not title:
            continue
        level = len(hashes)
        out.append((level, i, title))
    return out


class MarkdownFallbackEngine:
    """
    Minimal Markdown engine without markdown-it-py.
    - Detects ATX headings (# ... ######) outside code fences and blockquotes.
    - Builds a flat Document with MD_DOC and MD_HEADING nodes.
    - Supports 'full' and 'hide' actions.
    """

    filetypes = {"md"}

    def configure(self, roots: List[Path]) -> None:  # signature compatibility
        return

    def parse(self, path: Path, text: str) -> Document:
        posix = PurePosixPath(path.as_posix())
        ls = line_starts(text)
        n_lines = len(ls) - 1  # number of lines

        # Document root
        root = Node(
            kind=MD_DOC,
            path=posix,
            span=(0, len(text)),
            name=str(posix),
            qual=str(posix),  # targetable by path
            meta={},
            children=[],
        )

        # 1) Collect headings as (level, line_idx, title)
        heads_list = _scan_headings_excluding_fences_and_blockquotes(text)

        # 2) Compute section ends: up to the next heading with level <=
        enriched: List[Tuple[int, int, int, str]] = []
        for i, (lvl, start_line, title) in enumerate(heads_list):
            end_line = n_lines
            for j in range(i + 1, len(heads_list)):
                nxt_lvl, nxt_start, _ = heads_list[j]
                if nxt_lvl <= lvl:
                    end_line = nxt_start
                    break
            enriched.append((lvl, start_line, end_line, title))

        # 3) Create section nodes
        nodes: List[Node] = []
        for lvl, start_line, end_line, title in enriched:
            start_char = ls[start_line] if 0 <= start_line < len(ls) else 0
            end_char = ls[end_line] if 0 <= end_line < len(ls) else len(text)
            slug = slugify(title)
            qual = f"{posix}:{slug}"
            node = Node(
                kind=MD_HEADING,
                path=posix,
                span=(start_char, end_char),
                name=title,
                qual=qual,
                meta={"level": lvl, "slug": slug},
                children=[],
            )
            nodes.append(node)

        root.children.extend(nodes)
        assign_ids([root])
        flat = flatten([root])

        return Document(path=posix, text=text, roots=[root], nodes=flat)

    def supports(self, action) -> bool:
        return action.kind in {"hide", "full"}

    def render(self, doc: Document, decisions: List[Tuple[Node, object]]) -> List[Edit]:
        candidates: List[Edit] = []

        def _line_range(span: Tuple[int, int]) -> Tuple[int, int]:
            s, t = span
            before = doc.text[:s]
            omitted = doc.text[s:t]
            start_line = before.count("\n") + 1
            end_line = start_line + omitted.count("\n")
