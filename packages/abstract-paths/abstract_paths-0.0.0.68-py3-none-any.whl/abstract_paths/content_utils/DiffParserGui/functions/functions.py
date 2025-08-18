# abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/finder/DiffParserTab/diff_apply.py

from __future__ import annotations
from ..imports import *
import re


# ──────────────────────────────────────────────────────────────────────────────
# Diff parsing (simple unified-ish: leading '-' and '+'; blank/other delimits)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Hunk:
    
    subs: List[str] = field(default_factory=list)   # lines without leading '-'
    adds: List[str] = field(default_factory=list)   # lines without leading '+'

def parse_diff_text(diff_text: str) -> List[Hunk]:
    try:
        hunks: List[Hunk] = []
        cur = None
        open_block = False

        def close():
            nonlocal cur, open_block
            if open_block and cur and (cur.subs or cur.adds):
                hunks.append(cur)
            cur, open_block = None, False

        for raw in diff_text.splitlines():
            if raw.startswith('-'):
                if not open_block:
                    cur = Hunk()
                    open_block = True
                cur.subs.append(raw[1:])
            elif raw.startswith('+'):
                if not open_block:
                    cur = Hunk()
                    open_block = True
                cur.adds.append(raw[1:])
            else:
                if open_block:
                    close()
        if open_block:
            close()
        return hunks
    except Exception as e:
        logger.info(f"parse_diff_text: {e}")
# ──────────────────────────────────────────────────────────────────────────────
# Block replacement with tolerant matching (whitespace/comments optional)
# ──────────────────────────────────────────────────────────────────────────────

def _norm_line(s: str, strip_comments=True, collapse_ws=True, lower=False) -> str:
    try:
        if s is None:
            return ""
        if strip_comments:
            s = s.split('//', 1)[0]
        if collapse_ws:
            s = re.sub(r'\s+', ' ', s)
        if lower:
            s = s.lower()
        return s.strip()
    except Exception as e:
        logger.info(f"_norm_line: {e}")
def _find_block(original: List[str], block: List[str]) -> int:
    """
    Return the starting index where `block` occurs in `original` (exact, no norm).
    -1 if not found.
    """
    try:
        if not block:
            return -1
        n, m = len(original), len(block)
        if m > n:
            return -1
        for i in range(0, n - m + 1):
            if original[i:i+m] == block:
                return i
        return -1
    except Exception as e:
        logger.info(f"_find_block: {e}")
def _find_block_tolerant(original: List[str], block: List[str]) -> int:
    """
    Tolerant locate: ignore runs of whitespace and strip '//' comments.
    """
    try:
        if not block:
            return -1
        n, m = len(original), len(block)
        if m > n:
            return -1
        norm_o = [_norm_line(x) for x in original]
        norm_b = [_norm_line(x) for x in block]
        for i in range(0, n - m + 1):
            if norm_o[i:i+m] == norm_b:
                return i
        return -1
    except Exception as e:
        logger.info(f"_find_block_tolerant: {e}")
def apply_custom_diff(original_lines: List[str], diff_lines: List[str], tolerant: bool = True) -> List[str]:
    """
    Apply a simple '+'/'-' diff to a single file:
      - For each hunk, find the contiguous '-'-block in `original_lines`
        (tolerant match by default) and replace it with the '+' lines.
      - If not found exactly, try exact match fallback when tolerant=True fails.
      - If still not found, raise ValueError with details.
    """
    try:
        diff_text = "\n".join(diff_lines)
        hunks = parse_diff_text(diff_text)
        out = original_lines[:]

        # Apply hunks in sequence, updating the working list as we go
        for idx, hunk in enumerate(hunks, 1):
            subs, adds = hunk.subs, hunk.adds

            if tolerant:
                start = _find_block_tolerant(out, subs)
                if start < 0:
                    # fallback to exact, in case comments/whitespace differ weirdly
                    start = _find_block(out, subs)
            else:
                start = _find_block(out, subs)

            if start < 0:
                raise ValueError(f"Hunk #{idx} could not be located in the file.\n"
                                 f"First '-': {subs[0] if subs else '(empty)'}")

            end = start + len(subs)
            out = out[:start] + adds + out[end:]

        return out
    except Exception as e:
        logger.info(f"_find_block_tolerant: {e}")
