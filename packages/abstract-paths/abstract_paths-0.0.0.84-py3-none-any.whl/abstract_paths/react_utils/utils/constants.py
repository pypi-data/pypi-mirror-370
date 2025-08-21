import argparse,json,os,re
from pathlib import Path
from typing import *
from ..imports import * 

EXTS = (".ts", ".tsx", ".js", ".jsx", ".mts", ".cts")

RE_IMPORT = re.compile(
    r'^\s*import\s+(?P<clause>.*?)\s+from\s+[\'"](?P<spec>[^\'"]+)[\'"]\s*;?',
    re.M | re.S,
)
RE_SIDE_EFFECT_IMPORT = re.compile(
    r'^\s*import\s+[\'"](?P<spec>[^\'"]+)[\'"]\s*;?',
    re.M,
)
RE_NAMED_BINDINGS = re.compile(r'{(?P<named>[^}]*)}')
RE_DEFAULT_IMPORT = re.compile(r'^\s*([A-Za-z_\$][\w\$]*)\s*(?:,|$)')

RE_REEXPORT = re.compile(
    r'^\s*export\s*{\s*(?P<names>[^}]*)\s*}\s*from\s*[\'"](?P<spec>[^\'"]+)[\'"]',
    re.M,
)

RE_EXPORT_FN_DECL = re.compile(
    r'^\s*export\s+(?:async\s+)?function\s+([A-Za-z_\$][\w\$]*)\s*\(',
    re.M,
)
RE_EXPORT_CONST_FN = re.compile(
    r'^\s*export\s+(?:const|let|var)\s+([A-Za-z_\$][\w\$]*)\s*=\s*(?:async\s*)?(?:function\s*\(|\()',
    re.M,
)
RE_EXPORT_DEFAULT_NAMED = re.compile(
    r'^\s*export\s+default\s+(?:async\s+)?function\s+([A-Za-z_\$][\w\$]*)\s*\(',
    re.M,
)
RE_EXPORT_DEFAULT_ANON = re.compile(
    r'^\s*export\s+default\s+(?:async\s+)?(?:function\s*\(|\()',
    re.M,
)
RE_EXPORT_NAMED_LOCAL = re.compile(
    r'^\s*export\s*{\s*([^}]*)\s*}\s*;?',
    re.M,
)

RE_BLOCK_COMMENT = re.compile(r'/\*.*?\*/', re.S)
RE_LINE_COMMENT = re.compile(r'//.*?$|^\s*#.*?$', re.M)
# ─── your global defaults ────────────────────────────────────────────────────
REACT_DEFAULT_ALLOWED_EXTS: Set[str] = set(EXTS)

REACT_DEFAULT_EXCLUDE_TYPES: Set[str] = {
    "image", "video", "audio", "presentation",
    "spreadsheet", "archive", "executable"
}

# never want these—even if they sneak into ALLOWED
REACT_unallowed = set(get_media_exts(REACT_DEFAULT_EXCLUDE_TYPES)) | {'.shp', '.cpg', '.dbf', '.shx','.geojson',".pyc",'.shx','.geojson','.prj','.sbn','.sbx'}
REACT_DEFAULT_UNALLOWED_EXTS = {e for e in REACT_unallowed if e not in REACT_DEFAULT_ALLOWED_EXTS}

REACT_DEFAULT_EXCLUDE_DIRS: Set[str] = {
    "node_modules", "__pycache__", "backups", "backup","junk"
}

REACT_DEFAULT_EXCLUDE_PATTERNS: Set[str] = {
    "__init__*", "*.tmp", "*.log", "*.lock", "*.zip","*~"
}


REACT_DEFAULT_CFG = define_defaults(
                        allowed_exts=REACT_DEFAULT_ALLOWED_EXTS,
                        unallowed_exts=REACT_DEFAULT_UNALLOWED_EXTS,
                        exclude_types=REACT_DEFAULT_EXCLUDE_TYPES,
                        exclude_dirs=REACT_DEFAULT_EXCLUDE_DIRS,
                        exclude_patterns=REACT_DEFAULT_EXCLUDE_PATTERNS
                        )


REACT_ALLOWED = make_allowed_predicate(cfg=REACT_DEFAULT_CFG)
