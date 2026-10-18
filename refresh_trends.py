#!/usr/bin/env python3
"""Refresh trending queries in idea-machine-app.html with live Google Trends data.
Fetches per-niche (one keyword per call) — matches what works in idea-machine-live.py.
"""
import json, re, sys, time

DEPLOY = "/opt/data/deploy/idea-machine/index.html"

ALL_NICHES = {
    "home-garden": "home garden decor",
    "tech-gadgets": "tech gadgets",
    "fitness": "fitness equipment",
    "pets": "pet accessories",
    "kitchen": "kitchen gadgets",
    "outdoor": "camping gear",
    "office": "home office",
    "beauty": "beauty skincare",
    "phone": "phone accessories",
    "gaming": "gaming accessories",
    "fashion": "fashion accessories",
    "tools": "power tools",
    "eco": "eco products",
    "baby": "baby products",
    "auto": "car accessories",
}


def get_trends():
    """Rising queries per niche, fetched one keyword at a time."""
    result = {}
    from pytrends.request import TrendReq
    p = TrendReq(hl="en-GB", tz=0, retries=2, timeout=10)
    for nid, kw in ALL_NICHES.items():
        try:
            p.build_payload([kw], cat=0, timeframe="today 3-m", geo="GB", gprop="")
            d = p.interest_over_time()
            if d is None or d.empty:
                continue
            r = p.related_queries()
            rising = r.get(kw, {}).get("rising")
            if rising is not None and not rising.empty:
                qs = []
                for _, row in rising.head(3).iterrows():
                    qs.append(f"{row.get('query','')} (+{row.get('value',0)}%)")
                result[nid] = qs
            time.sleep(0.5)
        except Exception as e:
            print(f"  {nid}: {e}")
            time.sleep(1)
    return result


def inject_trends(html, trends):
    items = ",\n  ".join(f"'{nid}': {json.dumps(qs)}" for nid, qs in trends.items())
    new_block = f"const TRENDS = {{\n  {items}\n}};"
    pattern = r"const TRENDS = \{[^}]*\};"
    if re.search(pattern, html):
        return re.sub(pattern, new_block, html, flags=re.DOTALL)
    return html


if __name__ == "__main__":
    trends = get_trends()
    if len(trends) < 5:
        print(f"Only {len(trends)} niches refreshed — keeping existing trends")
        sys.exit(0)
    html = open(DEPLOY).read()
    new_html = inject_trends(html, trends)
    open(DEPLOY, "w").write(new_html)
    total = sum(len(v) for v in trends.values())
    print(f"✅ Refreshed {len(trends)} niches, {total} queries")
    for nid, qs in list(trends.items())[:5]:
        print(f"  {nid}: {qs[:1]}")