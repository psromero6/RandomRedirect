"""Checks every link in links.csv and comments out the ones that are gone.

A dead link becomes a line like:
    # removed 2026-11-25 (HTTP 404): https://example.com,,1
The site skips lines starting with #, so it's off the list but easy to restore.

Only links that are clearly gone get removed. Timeouts, rate limits and
server errors are treated as "still alive", so a bad day for a site
doesn't wipe it from the list.
"""
import csv
import datetime
import io
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

LINKS_FILE = sys.argv[1] if len(sys.argv) > 1 else "links.csv"
TIMEOUT = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (RandomRedirect link checker)"}

YT_RE = re.compile(r"(?:youtu\.be/|youtube\.com/(?:watch\?(?:.*&)?v=|shorts/|embed/))([\w-]{11})", re.I)


def fetch(url, method="GET"):
    """Returns (status, final_url). Raises on network trouble."""
    req = urllib.request.Request(url, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            return res.status, res.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.geturl() if hasattr(e, "geturl") else url


def dead_reason(url):
    """Returns a short reason if the link is clearly dead, else None."""
    try:
        yt = YT_RE.search(url)
        if yt:
            watch = "https://www.youtube.com/watch?v=" + yt.group(1)
            status, _ = fetch("https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(watch, safe=""))
            # 404/400 = video doesn't exist. 401/403 can just mean "embedding off", so keep those.
            return f"YouTube {status}" if status in (400, 404) else None

        status, final = fetch(url, method="GET")
        if "imgur.com/removed" in final:
            return "removed from Imgur"
        if status in (404, 410):
            return f"HTTP {status}"
        return None
    except Exception as e:  # timeouts, DNS hiccups, etc. -> don't remove
        print(f"  could not check ({e}); keeping it", file=sys.stderr)
        return None


def main():
    with open(LINKS_FILE, encoding="utf-8") as f:
        lines = f.read().splitlines()

    today = datetime.date.today().isoformat()
    out, removed = [], 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        is_data = stripped and not stripped.startswith("#") and not (i == 0 and stripped.lower().startswith("url"))
        if not is_data:
            out.append(line)
            continue
        url = next(csv.reader(io.StringIO(stripped)))[0].strip()
        print("Checking", url)
        reason = dead_reason(url)
        if reason:
            print("  DEAD:", reason)
            out.append(f"# removed {today} ({reason}): {line}")
            removed += 1
        else:
            out.append(line)

    if removed:
        with open(LINKS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
    print(f"Done. {removed} link(s) removed.")


if __name__ == "__main__":
    main()
