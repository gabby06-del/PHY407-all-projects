
"""
Site IA audit crawler for natural-resources.canada.ca/forests-forestry

Crawls from a start page, then writes:
  pages.csv    one row per crawled page (type, depth, nav counts, metadata)
  links.csv    every link found in page content (source, target, category)
  assets.csv   downloadable/non-page targets with content-type and size
  summary.txt  formats, document types, categories, secondary nav, top-down
               vs bottom-up IA evidence, and inconsistencies

Usage:
  /opt/anaconda3/bin/python site_audit.py
  /opt/anaconda3/bin/python site_audit.py --depth 3 --max-pages 200
  /opt/anaconda3/bin/python site_audit.py --start https://natural-resources.canada.ca/forests-forestry
"""
import argparse
import csv
import os
import re
import time
from collections import Counter, defaultdict
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode

import requests
from bs4 import BeautifulSoup

DEFAULT_START = "https://natural-resources.canada.ca/forests-forestry"
# Hosts we crawl. Everything else is recorded and classified, but not fetched.
CRAWL_SUFFIXES = ("natural-resources.canada.ca", "nrcan.gc.ca", "rncan.gc.ca")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
}

FORMAT_GROUPS = {
    "document": {"pdf", "doc", "docx", "ppt", "pptx", "odt", "rtf", "txt", "epub"},
    "data/spreadsheet": {"csv", "xls", "xlsx", "json", "xml", "geojson", "kml", "kmz",
                         "shp", "tif", "tiff", "gdb", "nc", "gpkg"},
    "compressed": {"zip", "gz", "tar", "tgz", "7z", "rar", "bz2"},
    "image": {"png", "jpg", "jpeg", "gif", "svg", "webp"},
    "video": {"mp4", "webm", "mov", "avi", "wmv", "m4v"},
    "audio": {"mp3", "wav", "ogg", "m4a"},
}
EXT_TO_GROUP = {e: g for g, exts in FORMAT_GROUPS.items() for e in exts}
HTML_EXTS = {"", "html", "htm", "aspx", "php", "cfm"}
SKIP_TEXT = {"language selection", "search", "menu", "you are here", "about this site",
             "government of canada corporate", "contact us"}


# ---------- helpers ----------
def clean(url):
    """Drop fragments and utm_* params so the same page isn't counted twice."""
    p = urlparse(url)
    q = [(k, v) for k, v in parse_qsl(p.query) if not k.lower().startswith("utm_")]
    return urlunparse((p.scheme, p.netloc.lower(), p.path, p.params, urlencode(q), ""))


def host_of(url):
    return (urlparse(url).hostname or "").lower()


def ext_of(url):
    m = re.search(r"\.([a-z0-9]{2,5})$", urlparse(url).path.lower())
    return m.group(1) if m else ""


def host_ok(url, suffixes):
    h = host_of(url)
    return any(h == s or h.endswith("." + s) for s in suffixes)


def classify_link(url, suffixes):
    """Format/category of a link target, judged from the URL alone."""
    ext, host, path = ext_of(url), host_of(url), urlparse(url).path.lower()
    if ext in EXT_TO_GROUP:
        return EXT_TO_GROUP[ext]
    if any(k in host for k in ("ostr", "collections")) or "/collections/" in path:
        return "database/repository"
    if (host.startswith("apps") or "cwfis" in host or "tidcf" in host
            or any(k in path for k in ("/calc/", "interactive-map", "/viewer", "/app/"))):
        return "web app/tool"
    if not host_ok(url, suffixes):
        return "external page"
    return "html page"


def group_from_content_type(ct):
    ct = (ct or "").lower()
    if "pdf" in ct or "msword" in ct or "officedocument" in ct:
        return "document"
    if any(k in ct for k in ("csv", "json", "xml", "excel", "spreadsheet", "tiff")):
        return "data/spreadsheet"
    if any(k in ct for k in ("zip", "gzip", "tar", "x-7z", "rar")):
        return "compressed"
    if ct.startswith("image/"):
        return "image"
    if ct.startswith("video/"):
        return "video"
    if ct.startswith("audio/"):
        return "audio"
    return None


def classify_page(url, title, hub_links):
    p, t = urlparse(url).path.lower(), (title or "").lower()
    if hub_links >= 6:
        return "hub/landing page"
    rules = [
        ("publication", "publication"), ("report", "report"),
        ("funding", "funding program"), ("program", "funding program"),
        ("calculator", "tool/calculator"), ("tool", "tool/calculator"),
        ("herbarium", "collection"), ("insectarium", "collection"),
        ("collection", "collection"), ("glossary", "reference"),
        ("identify", "reference"), ("research-centres", "research centre"),
        ("corporate", "corporate"), ("careers", "corporate"), ("news", "news"),
        ("price", "market data"), ("statistics", "market data"),
    ]
    for key, label in rules:
        if key in p or key in t:
            return label
    return "content page"


def fetch(session, url, retries=4):
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, timeout=(10, 45))
            print(f"   [{attempt}/{retries}] {r.status_code} {url}")
            if r.status_code == 200:
                return r
            if r.status_code in (403, 404, 410):
                return None
            wait = int(r.headers.get("Retry-After", 10 * attempt)) if r.status_code in (429, 503) else 5 * attempt
        except requests.exceptions.RequestException as e:
            print(f"   [{attempt}/{retries}] {type(e).__name__}: {e}")
            wait = 5 * attempt
        time.sleep(wait)
    return None


def links_in(node, base):
    out = []
    if node is None:
        return out
    for a in node.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        out.append((a.get_text(" ", strip=True), urljoin(base, href)))
    return out

def extract_page(soup, base):
    main = soup.select_one("main") or soup.find(attrs={"property": "mainContentOfPage"}) or soup.body
    d = {"main": main}

    d["global_menu"] = links_in(soup.select_one("nav.gcweb-menu, #wb-sm, nav[typeof='SiteNavigationElement']"), base)
    d["breadcrumb"] = links_in(soup.select_one("#wb-bc, ol.breadcrumb, nav[aria-label*='readcrumb']"), base)
    d["section_menu"] = links_in(soup.select_one("#wb-sec, nav.wb-sec, aside nav"), base)
    d["footer"] = links_in(soup.select_one("#wb-info, footer"), base)
    d["lang_toggle"] = links_in(soup.select_one("#wb-lng, section.wb-lng"), base)
    d["has_search"] = bool(soup.select_one("form[role='search'], #wb-srch, input[type='search']"))

    most = []
    for h in main.find_all(["h2", "h3"]):
        if "most requested" in h.get_text(strip=True).lower():
            lst = h.find_next_sibling(["ul", "ol"])
            most = links_in(lst, base)
    d["most_requested"] = most

    cats = []   # headings that carry a link = category cards
    for h in main.find_all(["h2", "h3"]):
        title = h.get_text(" ", strip=True)
        if title.lower() in SKIP_TEXT or "most requested" in title.lower():
            continue
        a = h.find("a", href=True)
        if a:
            blurb = h.find_next_sibling("p")
            cats.append((title, urljoin(base, a["href"]), blurb.get_text(" ", strip=True) if blurb else ""))
    d["categories"] = cats

    d["content_links"] = [(t, u) for t, u in links_in(main, base) if not u.startswith(base + "#")]
    d["anchors"] = [a["href"] for a in main.find_all("a", href=True) if a["href"].startswith("#") and len(a["href"]) > 1]

    meta = {}
    for m in soup.find_all("meta"):
        n = (m.get("name") or "").lower()
        if n.startswith("dcterms.") or n in ("description", "gcaaterms.sitename"):
            meta[n] = m.get("content", "")
    d["meta"] = meta
    can = soup.find("link", rel="canonical")
    d["canonical"] = clean(can["href"]) if can and can.get("href") else ""
    d["images"] = len(main.find_all("img"))
    d["tables"] = len(main.find_all("table"))
    d["iframes"] = len(main.find_all(["iframe", "embed", "object"]))
    d["video_audio"] = len(main.find_all(["video", "audio"]))
    d["forms"] = len(main.find_all("form"))
    h1 = soup.find("h1")
    d["h1"] = h1.get_text(" ", strip=True) if h1 else ""
    return d
def crawl(start, depth_limit, max_pages, delay, suffixes):
    session = requests.Session()
    session.headers.update(HEADERS)
    queue, seen = [(clean(start), 0, "")], {clean(start)}
    pages, links, redirects, failures = [], [], [], []
    hub_nav = {}

    while queue and len(pages) < max_pages:
        url, depth, parent = queue.pop(0)
        print(f"\n[{len(pages) + 1}] depth {depth}: {url}")
        time.sleep(delay)
        res = fetch(session, url)
        if not res:
            failures.append(url)
            continue
        if "html" not in res.headers.get("Content-Type", "").lower():
            continue
        final = clean(res.url)
        if final != url:
            redirects.append((url, final))
            seen.add(final)
        soup = BeautifulSoup(res.text, "html.parser")
        d = extract_page(soup, res.url)
        d.update(url=final, requested=url, depth=depth, parent=parent)
        d["page_type"] = classify_page(final, d["h1"], len(d["categories"]))
        pages.append(d)
        if depth == 0:
            hub_nav = d

        for text, target in d["content_links"]:
            t = clean(target)
            cat = classify_link(t, suffixes)
            links.append({"source": final, "text": text[:120], "target": t, "category": cat,
                          "host": host_of(t), "ext": ext_of(t)})
            crawlable = (cat == "html page" and ext_of(t) in HTML_EXTS and host_ok(t, suffixes)
                         and t not in seen)
            if crawlable and depth < depth_limit:
                seen.add(t)
                queue.append((t, depth + 1, final))
    return session, pages, links, redirects, failures, hub_nav


def check_assets(session, links, limit):
    targets = sorted({l["target"] for l in links if l["ext"] in EXT_TO_GROUP})[:limit]
    rows = []
    for t in targets:
        ct, size = "", ""
        try:
            r = session.head(t, timeout=(10, 20), allow_redirects=True)
            ct, size = r.headers.get("Content-Type", ""), r.headers.get("Content-Length", "")
        except requests.exceptions.RequestException as e:
            ct = f"error: {type(e).__name__}"
        rows.append({"url": t, "ext": ext_of(t), "content_type": ct, "bytes": size,
                     "group": group_from_content_type(ct) or EXT_TO_GROUP.get(ext_of(t), "")})
        time.sleep(0.5)
    return rows
def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def build_summary(pages, links, assets, redirects, failures, hub, suffixes):
    L = []
    add = L.append
    add(f"SITE AUDIT SUMMARY  ({len(pages)} pages crawled, {len(links)} content links, "
        f"{len(failures)} failed fetches)\n")

    add("1. FORMATS (by link target)")
    fmt = Counter(l["category"] for l in links)
    uniq = defaultdict(set)
    for l in links:
        uniq[l["category"]].add(l["target"])
    for k, v in fmt.most_common():
        add(f"   {k:<22} {v:>5} links  ({len(uniq[k])} unique)")
    exts = Counter(l["ext"] for l in links if l["ext"] in EXT_TO_GROUP)
    if exts:
        add("   File extensions: " + ", ".join(f"{e}={n}" for e, n in exts.most_common()))
    media_pages = sum(1 for p in pages if p["video_audio"] or p["iframes"])
    add(f"   Embedded media/iframes on {media_pages} page(s); "
        f"images on {sum(1 for p in pages if p['images'])} page(s); "
        f"tables on {sum(1 for p in pages if p['tables'])}; forms on {sum(1 for p in pages if p['forms'])}")
    if assets:
        ct = Counter((a["content_type"] or "unknown").split(";")[0] for a in assets)
        add("   Content-types of downloadable files (HEAD): " + ", ".join(f"{k}={v}" for k, v in ct.most_common()))
    add("")

    add("2. DOCUMENT / PAGE TYPES")
    for k, v in Counter(p["page_type"] for p in pages).most_common():
        add(f"   {k:<22} {v:>4}")
    add("")

    add("3. MAJOR CATEGORY LINKS (start page headings with links)")
    for title, url, blurb in hub.get("categories", []):
        add(f"   - {title}\n       {url}" + (f"\n       {blurb}" if blurb else ""))
    add("")

    add("4. SECONDARY NAVIGATION")
    add(f"   Most requested (start page): {len(hub.get('most_requested', []))}")
    for t, u in hub.get("most_requested", []):
        add(f"       {t} -> {u}")
    sec = [p for p in pages if p["section_menu"]]
    add(f"   Pages with a section/side menu: {len(sec)}")
    bc = Counter(len(p["breadcrumb"]) for p in pages)
    add("   Breadcrumb depth distribution: " + ", ".join(f"{k} levels={v}" for k, v in sorted(bc.items())))
    add(f"   Global menu items (start page): {len(hub.get('global_menu', []))}; "
        f"footer links: {len(hub.get('footer', []))}; language toggle: "
        f"{', '.join(u for _, u in hub.get('lang_toggle', [])) or 'none found'}; "
        f"search box: {hub.get('has_search')}")
    add(f"   Pages with 'Most requested' blocks: {sum(1 for p in pages if p['most_requested'])}; "
        f"with in-page jump anchors: {sum(1 for p in pages if p['anchors'])}")
    add("")

    add("5. TOP-DOWN IA SIGNALS")
    add(f"   Hierarchical breadcrumbs on {sum(1 for p in pages if p['breadcrumb'])}/{len(pages)} pages")
    add(f"   Shared global menu on {sum(1 for p in pages if p['global_menu'])}/{len(pages)} pages")
    add(f"   Hub/landing pages with category cards: {sum(1 for p in pages if len(p['categories']) >= 6)}")
    add(f"   Pages with Dublin Core metadata: {sum(1 for p in pages if p['meta'])}/{len(pages)}")
    depth_c = Counter(p["depth"] for p in pages)
    add("   Pages by crawl depth: " + ", ".join(f"d{k}={v}" for k, v in sorted(depth_c.items())))
    add("")

    add("6. BOTTOM-UP IA SIGNALS")
    inbound = defaultdict(set)
    for l in links:
        inbound[l["target"]].add(l["source"])
    multi = sorted(((len(s), t) for t, s in inbound.items() if len(s) >= 2), reverse=True)
    add(f"   Targets linked from 2+ pages (cross-linking): {len(multi)}")
    for n, t in multi[:10]:
        add(f"       {n} pages -> {t}")
    add(f"   Search/database/app entry points: "
        f"{sum(1 for l in links if l['category'] in ('database/repository', 'web app/tool'))} links across "
        f"{len({l['host'] for l in links if l['category'] in ('database/repository', 'web app/tool')})} host(s)")
    add(f"   Campaign/vanity (utm) links were normalized; see links.csv for targets per source")
    add("")

    add("7. HOSTS REFERENCED")
    for h, n in Counter(l["host"] for l in links).most_common(15):
        tag = "in scope" if any(h == s or h.endswith('.' + s) for s in suffixes) else "external"
        add(f"   {h:<45} {n:>4}  ({tag})")
    add("")

    add("8. INCONSISTENCIES")
    add(f"   Redirects encountered: {len(redirects)}")
    for a, b in redirects[:10]:
        add(f"       {a} -> {b}")
    mism = [p for p in pages if p["canonical"] and p["canonical"] != p["url"]]
    add(f"   Canonical differs from fetched URL: {len(mism)}")
    for p in mism[:10]:
        add(f"       {p['url']} (canonical {p['canonical']})")
    leak = sorted({l["target"] for l in links if "admin." in l["host"]})
    add(f"   Links to admin/staging hosts: {len(leak)}")
    for t in leak[:10]:
        add(f"       {t}")
    both = {re.sub(r"/forests?-forestry/", "/forest(s)-forestry/", u) for u in
            {l["target"] for l in links if "/forest-forestry/" in l["target"]}} & \
           {re.sub(r"/forests?-forestry/", "/forest(s)-forestry/", u) for u in
            {l["target"] for l in links if "/forests-forestry/" in l["target"]}}
    add(f"   Same page linked under both /forest-forestry/ and /forests-forestry/: {len(both)}")
    if failures:
        add(f"   Failed fetches: {len(failures)}")
        for u in failures[:10]:
            add(f"       {u}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--depth", type=int, default=2, help="link depth from the start page")
    ap.add_argument("--max-pages", type=int, default=120)
    ap.add_argument("--delay", type=float, default=1.5, help="seconds between page requests")
    ap.add_argument("--max-head", type=int, default=60, help="max file links to HEAD-check")
    ap.add_argument("--out", default=os.path.join(os.path.expanduser("~/Desktop"), "site_audit"))
    a = ap.parse_args()

    suffixes = CRAWL_SUFFIXES + (host_of(a.start),)
    os.makedirs(a.out, exist_ok=True)

    session, pages, links, redirects, failures, hub = crawl(
        a.start, a.depth, a.max_pages, a.delay, suffixes)
    if not pages:
        print("\nNo pages crawled. Check the start URL and your connection.")
        raise SystemExit(1)

    print("\nChecking downloadable file links...")
    assets = check_assets(session, links, a.max_head)

    write_csv(os.path.join(a.out, "pages.csv"),
              [{"url": p["url"], "depth": p["depth"], "parent": p["parent"], "page_type": p["page_type"],
                "h1": p["h1"], "breadcrumb_depth": len(p["breadcrumb"]), "categories": len(p["categories"]),
                "most_requested": len(p["most_requested"]), "section_menu": len(p["section_menu"]),
                "content_links": len(p["content_links"]), "images": p["images"], "tables": p["tables"],
                "iframes": p["iframes"], "modified": p["meta"].get("dcterms.modified", ""),
                "issued": p["meta"].get("dcterms.issued", ""), "canonical": p["canonical"]} for p in pages],
              ["url", "depth", "parent", "page_type", "h1", "breadcrumb_depth", "categories",
               "most_requested", "section_menu", "content_links", "images", "tables", "iframes",
               "modified", "issued", "canonical"])
    write_csv(os.path.join(a.out, "links.csv"), links, ["source", "text", "target", "category", "host", "ext"])
    write_csv(os.path.join(a.out, "assets.csv"), assets, ["url", "ext", "group", "content_type", "bytes"])

    summary = build_summary(pages, links, assets, redirects, failures, hub, suffixes)
    with open(os.path.join(a.out, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary)
    print("\n" + "=" * 70 + "\n" + summary)
    print(f"\nFiles saved in: {a.out}")


if __name__ == "__main__":
    main()