import datetime as dt
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contrib as c  # noqa: E402


def item(owner, day, n=1):
    return {"owner": owner, "date": day, "count": n}


D = dt.date(2026, 10, 5)


class AllowlistFilter(unittest.TestCase):
    def test_keeps_only_allowlisted_owner(self):
        kept, s = c.filter_items([item("gauzpan", D, 3), item("someone-else", D, 5)], ["gauzpan"])
        self.assertEqual([k["owner"] for k in kept], ["gauzpan"])
        self.assertEqual(s, {"kept": 3, "dropped": 5, "hard_excluded": 0})

    def test_owner_match_is_case_insensitive_and_exact(self):
        kept, _ = c.filter_items([item("GauzPan", D), item("gauzpan-labs", D)], ["gauzpan"])
        self.assertEqual([k["owner"] for k in kept], ["GauzPan"])  # no prefix/substring match

    def test_empty_allowlist_keeps_nothing(self):
        kept, s = c.filter_items([item("gauzpan", D, 4)], [])
        self.assertEqual(kept, [])
        self.assertEqual(s["dropped"], 4)

    def test_hard_exclude_wins_even_if_allowlisted(self):
        items = [item("Nutanix", D, 7), item("nutanix-dev", D, 2), item("gauzpan", D, 1)]
        kept, s = c.filter_items(items, ["gauzpan", "nutanix", "Nutanix-Dev"])
        self.assertEqual([k["owner"] for k in kept], ["gauzpan"])
        self.assertEqual(s, {"kept": 1, "dropped": 9, "hard_excluded": 9})

    def test_missing_owner_is_dropped(self):
        kept, s = c.filter_items([item(None, D, 2), item("", D, 1)], ["gauzpan"])
        self.assertEqual(kept, [])
        self.assertEqual(s["dropped"], 3)

    def test_load_allowlist_rejects_bad_shape(self):
        import json, tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"owners": ["x"]}, f)
        with self.assertRaises(SystemExit):
            c.load_allowlist(f.name)
        os.unlink(f.name)


class PrivacyRules(unittest.TestCase):
    def test_never_requests_aggregate_calendar_or_repo_names(self):
        q = c.QUERY
        self.assertNotIn("contributionCalendar", q)
        self.assertNotIn("totalContributions", q)
        self.assertNotRegex(q, r"\bname\b|nameWithOwner|\burl\b")

    def test_uses_all_four_by_repository_breakdowns(self):
        for f in ("commitContributionsByRepository", "pullRequestContributionsByRepository",
                  "issueContributionsByRepository", "pullRequestReviewContributionsByRepository"):
            self.assertIn(f, c.QUERY)

    def test_svg_contains_no_owner_or_repo_strings(self):
        counts, we, wd = c.bucket([item("gauzpan", D, 3)], D)
        for theme in ("dark", "light"):
            svg = c.render_svg(counts, we, wd, D, theme)
            self.assertNotIn("gauzpan", svg.lower())
            self.assertNotIn("nutanix", svg.lower())


def fake_run(pages):
    """pages: callable(from_iso, to_iso) -> contributionsCollection dict."""
    def run(query, variables):
        return {"user": {"contributionsCollection": pages(variables["from"], variables["to"])}}
    return run


def empty_cc():
    return {f: [] for f, _ in c.BLOCKS}


def repo(owner, nodes, has_next=False):
    return {"repository": {"owner": {"login": owner}},
            "contributions": {"pageInfo": {"hasNextPage": has_next}, "nodes": nodes}}


class Fetching(unittest.TestCase):
    def test_counts_commit_count_and_one_per_pr_issue_review(self):
        cc = empty_cc()
        cc["commitContributionsByRepository"] = [repo("gauzpan", [{"occurredAt": "2026-10-03T10:00:00Z", "commitCount": 4}])]
        cc["pullRequestContributionsByRepository"] = [repo("gauzpan", [{"occurredAt": "2026-10-03T11:00:00Z"}])]
        cc["issueContributionsByRepository"] = [repo("gauzpan", [{"occurredAt": "2026-10-04T11:00:00Z"}])]
        cc["pullRequestReviewContributionsByRepository"] = [repo("gauzpan", [{"occurredAt": "2026-10-04T12:00:00Z"}])]
        stats = {"truncated_windows": 0}
        items = c.fetch_window(fake_run(lambda a, b: cc), "gauzpan",
                               dt.datetime(2026, 10, 1), dt.datetime(2026, 10, 5), stats)
        self.assertEqual(sum(i["count"] for i in items), 7)

    def test_splits_window_when_a_repo_has_another_page(self):
        calls = []

        def pages(a, b):
            calls.append((a, b))
            span_days = (dt.datetime.strptime(b, "%Y-%m-%dT%H:%M:%SZ") -
                         dt.datetime.strptime(a, "%Y-%m-%dT%H:%M:%SZ")).days
            cc = empty_cc()
            # Pretend any window wider than 2 days is truncated.
            cc["issueContributionsByRepository"] = [repo("gauzpan", [{"occurredAt": a}], has_next=span_days > 2)]
            return cc
        stats = {"truncated_windows": 0}
        items = c.fetch_window(fake_run(pages), "gauzpan",
                               dt.datetime(2026, 1, 1), dt.datetime(2026, 1, 11), stats)
        self.assertGreater(len(calls), 1)
        self.assertEqual(stats["truncated_windows"], 0)
        self.assertGreater(len(items), 1)

    def test_timezone_offset_shifts_the_day(self):
        raw = [{"owner": "gauzpan", "at": "2026-10-03T20:00:00Z", "count": 1}]
        self.assertEqual(c.to_dated(raw, 0)[0]["date"], dt.date(2026, 10, 3))
        self.assertEqual(c.to_dated(raw, 330)[0]["date"], dt.date(2026, 10, 4))


class Bucketing(unittest.TestCase):
    def test_weekend_and_weekday_totals(self):
        sat, mon = dt.date(2026, 10, 3), dt.date(2026, 10, 5)
        counts, we, wd = c.bucket([item("x", sat, 2), item("x", mon, 5), item("x", mon, 1)], mon)
        self.assertEqual((we, wd), (2, 6))
        self.assertEqual(counts[mon], 6)

    def test_ignores_days_outside_the_window(self):
        old = D - dt.timedelta(days=400)
        _, we, wd = c.bucket([item("x", old, 9)], D)
        self.assertEqual((we, wd), (0, 0))


def luminance(hexc):
    r, g, b = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class Rendering(unittest.TestCase):
    def test_text_contrast_meets_aa_in_both_themes(self):
        for name, t in c.THEMES.items():
            for key in ("fg", "muted", "teal_text", "saffron_text"):
                self.assertGreaterEqual(contrast(t[key], t["bg"]), 4.5, f"{name}:{key}")

    def test_light_theme_is_white(self):
        self.assertEqual(c.THEMES["light"]["bg"], "#FFFFFF")

    def test_svg_is_53_weeks_by_7_and_uses_both_scales(self):
        today = dt.date(2026, 10, 5)
        counts, we, wd = c.bucket([item("x", dt.date(2026, 10, 3), 3), item("x", today, 2)], today)
        svg = c.render_svg(counts, we, wd, today, "dark")
        rects = re.findall(r'<rect x="[\d.]+" y="[\d.]+" width="11" height="11" rx="2.5" fill="(#\w+)"', svg)
        grid = rects[:365]
        self.assertEqual(len(grid), 365)
        self.assertIn(c.THEMES["dark"]["saffron"][3], grid)  # weekend max
        self.assertIn(c.THEMES["dark"]["teal"][2], grid)     # weekday, 2 of max 3 -> level 3
        cols = {float(x) for x in re.findall(r'<rect x="([\d.]+)" y="[\d.]+" width="11"', svg)[:365]}
        self.assertLessEqual(len(cols), 53)

    def test_caption_totals_and_deterministic_output(self):
        counts, we, wd = c.bucket([item("x", dt.date(2026, 10, 3), 12)], D)
        a = c.render_svg(counts, we, wd, D, "light")
        self.assertEqual(a, c.render_svg(counts, we, wd, D, "light"))
        self.assertIn("12 weekend and 0 weekday contributions", a)  # accessible <desc>; visible text is outlines
        self.assertIn('aria-labelledby="t d"', a)


if __name__ == "__main__":
    unittest.main()
