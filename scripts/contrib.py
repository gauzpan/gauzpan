#!/usr/bin/env python3
"""Personal side-project contribution graph for the profile README.

Reads GitHub GraphQL `contributionsCollection` for the last 365 days, counts
only contributions in repositories owned by an ALLOWLISTED login, and renders
two SVGs (dark + light). Python 3.9+, standard library only.

Privacy rules, enforced here and covered by tests:
  * Counts come ONLY from the by-repository breakdowns. The aggregate
    `contributionCalendar` is never requested (it includes work activity).
  * A contribution counts only if its repository OWNER is on the allowlist
    (config/contrib-allowlist.json). The match is per owner, not per repo, so
    every repo you own is counted, including ones created later. Owners
    matching HARD_EXCLUDE are dropped even if added to the allowlist by mistake.
  * Repository names are never requested, logged or written to the SVGs.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphs import GLYPHS  # noqa: E402

API_URL = "https://api.github.com/graphql"
HARD_EXCLUDE = ("nutanix",)  # case-insensitive substring match on the owner login
DAYS = 365
PAGE = 100  # GraphQL max for both repositories and nested contributions

# --- GraphQL ----------------------------------------------------------------


def _block(field, extra=""):
    # Deliberately no `name`/`nameWithOwner`: repo names are never fetched.
    return (
        f"{field}(maxRepositories: {PAGE}) {{\n"
        f"  repository {{ owner {{ login }} }}\n"
        f"  contributions(first: {PAGE}) {{\n"
        f"    pageInfo {{ hasNextPage }}\n"
        f"    nodes {{ occurredAt {extra} }}\n"
        f"  }}\n"
        f"}}\n"
    )


# (response field, node field holding a count, or None for one per node)
BLOCKS = (
    ("commitContributionsByRepository", "commitCount"),
    ("pullRequestContributionsByRepository", None),
    ("issueContributionsByRepository", None),
    ("pullRequestReviewContributionsByRepository", None),
)

QUERY = (
    "query($login: String!, $from: DateTime!, $to: DateTime!) {\n"
    "  user(login: $login) {\n"
    "    contributionsCollection(from: $from, to: $to) {\n"
    + "".join(_block(f, c or "") for f, c in BLOCKS)
    + "    }\n  }\n}\n"
)


def graphql(token, query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-contrib-graph",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.load(resp)
            break
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"GraphQL request failed: HTTP {e.code}")
        except urllib.error.URLError as e:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise SystemExit(f"GraphQL request failed: {e.reason}")
    if payload.get("errors"):
        # Messages can echo query text, not repo names; still print only a count.
        raise SystemExit(f"GraphQL returned {len(payload['errors'])} error(s)")
    return payload["data"]


def _iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_window(run, login, start, end, stats):
    """Fetch [start, end]. If any list may be truncated (a repo has more than
    one page of contributions, or 100 repos came back), split the window and
    recurse, so paging is exhaustive down to a single day."""
    data = run(QUERY, {"login": login, "from": _iso(start), "to": _iso(end)})
    cc = data["user"]["contributionsCollection"]
    truncated = False
    for field, _ in BLOCKS:
        repos = cc[field]
        if len(repos) >= PAGE:
            truncated = True
        if any(r["contributions"]["pageInfo"]["hasNextPage"] for r in repos):
            truncated = True
    if truncated:
        if end - start > dt.timedelta(days=1):
            mid = start + (end - start) / 2
            mid = mid.replace(microsecond=0)
            return fetch_window(run, login, start, mid - dt.timedelta(seconds=1), stats) + \
                fetch_window(run, login, mid, end, stats)
        stats["truncated_windows"] += 1  # a single day with 100+ items in one repo
    items = []
    for field, count_field in BLOCKS:
        for repo in cc[field]:
            owner = (repo["repository"]["owner"] or {}).get("login", "")
            for node in repo["contributions"]["nodes"]:
                n = node[count_field] if count_field else 1
                items.append({"owner": owner, "at": node["occurredAt"], "count": int(n)})
    return items


def to_dated(items, utc_offset_minutes=0):
    out = []
    for it in items:
        t = dt.datetime.strptime(it["at"], "%Y-%m-%dT%H:%M:%SZ")
        t += dt.timedelta(minutes=utc_offset_minutes)
        out.append({"owner": it["owner"], "date": t.date(), "count": it["count"]})
    return out


# --- Allowlist filter (the privacy boundary) --------------------------------


def filter_items(items, allowlist, hard_exclude=HARD_EXCLUDE):
    """Keep only contributions whose repo owner is on the allowlist and not
    hard-excluded. Returns (kept, stats) where stats holds counts only."""
    allow = {a.strip().lower() for a in allowlist if a and a.strip()}
    kept = []
    stats = {"kept": 0, "dropped": 0, "hard_excluded": 0}
    for it in items:
        owner = (it["owner"] or "").lower()
        if any(h in owner for h in hard_exclude):
            stats["hard_excluded"] += it["count"]
            stats["dropped"] += it["count"]
        elif owner not in allow:
            stats["dropped"] += it["count"]
        else:
            kept.append(it)
            stats["kept"] += it["count"]
    return kept, stats


def load_allowlist(path):
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        raise SystemExit("allowlist must be a JSON array of owner logins")
    return data


# --- Bucketing --------------------------------------------------------------


def bucket(items, today, days=DAYS):
    start = today - dt.timedelta(days=days - 1)
    counts = defaultdict(int)
    for it in items:
        if start <= it["date"] <= today:
            counts[it["date"]] += it["count"]
    weekend = sum(c for d, c in counts.items() if d.weekday() >= 5)
    weekday = sum(c for d, c in counts.items() if d.weekday() < 5)
    return dict(counts), weekend, weekday


# --- SVG --------------------------------------------------------------------

THEMES = {
    "dark": {
        "bg": "#0B1220", "border": "#1E2A40", "fg": "#E8ECF4", "muted": "#8C97AD",
        "empty": "#16213A", "teal_text": "#3FB8AF", "saffron_text": "#F5A524",
        "teal": ["#1F5F5A", "#2A8A83", "#3FB8AF", "#7EDDD4"],
        "saffron": ["#6B4A0E", "#A8750F", "#F5A524", "#FFC861"],
    },
    "light": {
        "bg": "#FFFFFF", "border": "#D5DCE8", "fg": "#0B1220", "muted": "#3A465C",
        "empty": "#EEF1F6", "teal_text": "#176B65", "saffron_text": "#8A5200",
        "teal": ["#B6E3DF", "#6CC5BD", "#2A8F87", "#176B65"],
        "saffron": ["#FDE2AE", "#F9C25C", "#E08E0B", "#A8670A"],
    },
}

W, H = 800, 224
CELL, PITCH = 11, 13.5
GX, GY = 60, 74
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class Text:
    """Lays out text as Space Grotesk outlines (no web font needed)."""

    def __init__(self):
        self.used = {}

    def width(self, s, size, weight):
        g = GLYPHS[weight]
        return sum(g["glyphs"][c][0] for c in s) * size / g["upem"]

    def draw(self, s, x, y, size, weight, fill, anchor="start"):
        g = GLYPHS[weight]
        w = self.width(s, size, weight)
        if anchor == "end":
            x -= w
        elif anchor == "middle":
            x -= w / 2
        scale = size / g["upem"]
        uses, pen = [], 0
        for c in s:
            adv, d = g["glyphs"][c]
            if d:
                gid = f"g{weight}{ord(c)}"
                self.used[gid] = d
                uses.append(f'<use href="#{gid}" x="{pen}"/>')
            pen += adv
        return (f'<g transform="translate({x:.1f} {y:.1f}) scale({scale:.5f})" fill="{fill}">'
                + "".join(uses) + "</g>")

    def defs(self):
        return "".join(f'<path id="{i}" d="{d}"/>' for i, d in sorted(self.used.items()))


def _level(c, m):
    if c <= 0:
        return 0
    return max(1, min(4, -(-4 * c // m)))  # ceil(4c/m)


def render_svg(counts, weekend, weekday, today, theme, days=DAYS):
    t = THEMES[theme]
    tx = Text()
    start = today - dt.timedelta(days=days - 1)
    first_sunday = start - dt.timedelta(days=(start.weekday() + 1) % 7)
    m = max(counts.values()) if counts else 1
    cells, labels, last_label_col = [], [], -9
    d = start
    while d <= today:
        col = (d - first_sunday).days // 7
        row = (d.weekday() + 1) % 7
        c = counts.get(d, 0)
        lv = _level(c, m)
        if lv == 0:
            fill = t["empty"]
        else:
            fill = t["saffron" if d.weekday() >= 5 else "teal"][lv - 1]
        cells.append(f'<rect x="{GX + col * PITCH:.1f}" y="{GY + row * PITCH:.1f}" '
                     f'width="{CELL}" height="{CELL}" rx="2.5" fill="{fill}"/>')
        if d.day == 1 and col - last_label_col >= 3:
            labels.append(tx.draw(MONTHS[d.month - 1], GX + col * PITCH, GY - 9, 10, "500", t["muted"]))
            last_label_col = col
        d += dt.timedelta(days=1)
    for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        labels.append(tx.draw(name, GX - 8, GY + r * PITCH + 9, 10, "500", t["muted"], "end"))

    # Caption with colour key (weekdays teal, weekends saffron).
    x, y, size = 28, 40, 19
    cap = []
    for seg, fill in (("Side-project activity", t["fg"]), (" · ", t["muted"]),
                      ("Weekdays", t["teal_text"]), (" · ", t["muted"]),
                      ("Weekends", t["saffron_text"])):
        cap.append(tx.draw(seg, x, y, size, "700", fill))
        x += tx.width(seg, size, "700")

    # Footer: totals on the left, colour key on the right.
    fy = H - 26
    totals = tx.draw(f"{weekend:,} weekend / {weekday:,} weekday contributions, last 12 months",
                     28, fy, 12.5, "500", t["fg"])
    key, kx = [], W - 28
    for name, scale, fill in (("Weekends", t["saffron"], t["saffron_text"]),
                              ("Weekdays", t["teal"], t["teal_text"])):
        for sw in reversed([t["empty"]] + scale):
            kx -= CELL
            key.append(f'<rect x="{kx}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{sw}"/>')
            kx -= 3
        kx -= 6
        key.append(tx.draw(name, kx, fy, 11.5, "500", fill, "end"))
        kx -= tx.width(name, 11.5, "500") + 22

    desc = (f"Side-project activity in the last 12 months: {weekend} weekend and "
            f"{weekday} weekday contributions. Weekdays in teal, weekends in saffron.")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-labelledby="t d">'
        f'<title id="t">Side-project activity</title><desc id="d">{desc}</desc>'
        f'<defs>{tx.defs()}</defs>'
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{t["bg"]}" stroke="{t["border"]}"/>'
        + "".join(cap) + "".join(labels) + "".join(cells) + totals + "".join(key) + "</svg>\n"
    )


# --- Entry point ------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/contrib-allowlist.json")
    ap.add_argument("--out", default="out")
    ap.add_argument("--login", default=os.environ.get("CONTRIB_LOGIN") or os.environ.get("GITHUB_REPOSITORY_OWNER"))
    args = ap.parse_args(argv)

    # CONTRIB_TOKEN (fine-grained PAT, own account only) is optional; only needed
    # to count private PERSONAL repos. Otherwise the workflow's GITHUB_TOKEN is used.
    token = os.environ.get("CONTRIB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token or not args.login:
        raise SystemExit("Need GITHUB_TOKEN (or CONTRIB_TOKEN) and --login / GITHUB_REPOSITORY_OWNER")
    offset = int(os.environ.get("CONTRIB_UTC_OFFSET_MINUTES", "0"))

    allowlist = load_allowlist(args.config)
    now = dt.datetime.utcnow().replace(microsecond=0)
    today = (now + dt.timedelta(minutes=offset)).date()
    start = dt.datetime.combine(today - dt.timedelta(days=DAYS - 1), dt.time()) - dt.timedelta(minutes=offset)
    stats = {"truncated_windows": 0}
    raw = fetch_window(lambda q, v: graphql(token, q, v), args.login, start, now, stats)
    kept, fstats = filter_items(to_dated(raw, offset), allowlist)
    counts, weekend, weekday = bucket(kept, today)

    # Counts only. Never repo names.
    print(f"contributions kept={fstats['kept']} dropped={fstats['dropped']} "
          f"(hard-excluded={fstats['hard_excluded']}) truncated_windows={stats['truncated_windows']}")
    os.makedirs(os.path.join(args.out, "assets"), exist_ok=True)
    for theme in ("dark", "light"):
        with open(os.path.join(args.out, "assets", f"contrib-{theme}.svg"), "w") as f:
            f.write(render_svg(counts, weekend, weekday, today, theme))
    print(f"wrote {weekend} weekend / {weekday} weekday")


if __name__ == "__main__":
    main()
