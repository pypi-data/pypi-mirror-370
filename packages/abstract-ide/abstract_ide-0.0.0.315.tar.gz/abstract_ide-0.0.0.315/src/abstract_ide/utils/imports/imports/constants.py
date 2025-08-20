import re
# ─────────────────────────────────────────────────────────────────────────────
# Command with markers (no log files on disk needed)
COMMAND = r"""
set -e
echo "__TSC_BEGIN__"
npx tsc --noEmit || true
echo "__TSC_END__"
echo "__BUILD_BEGIN__"
CI=true yarn build || true
echo "__BUILD_END__"
"""

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
FILE_REGEX = re.compile(r'([^\s:()]+\.(?:ts|tsx|js|jsx))\((\d+),(\d+)\)')
FILE_FILE_REGEX = re.compile(
    r'(?P<file>[^\s:()]+\.(?:ts|tsx|js|jsx))'
    r'(?:\((?P<l1>\d+),(?P<c1>\d+)\)|:(?P<l2>\d+):(?P<c2>\d+))'
)

GREP_REGEX = r"import\s+[^;]*\buse[^;]*from\s+['\"]react['\"]"
SEV_ERR = re.compile(r'(^|\b)(ERROR|error)\b|error TS\d+', re.IGNORECASE)
SEV_WRN = re.compile(r'(^|\b)(WARNING|warning)\b|warning TS\d+', re.IGNORECASE)

# Prefer targets left→right when hunting alternates
EXT_SWAP = {
    ".ts":  [".tsx"],
    ".tsx": [".ts"],
    ".js":  [".jsx"],
    ".jsx": [".js"],
}
