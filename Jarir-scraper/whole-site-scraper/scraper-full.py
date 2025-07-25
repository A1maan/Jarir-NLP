#!/usr/bin/env python3
"""
Fast scraper for three Jarir categories via the hidden catalog-v2 API,
with enhanced spec extraction (JSON+HTML fallback), limited to 50 products each.
  • office-supplies    (ID=6)
  • school-supplies    (ID=146)
  • toys-kids-learning (ID=235)
"""

import re
import html
import json5
import itertools
import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ───────────────────────── config ─────────────────────────
MAX_WORKERS          = 20
LINK_FETCH_PAGE_SIZE = 100
PRODUCT_LIMIT        = 50  # only scrape the first 50 products per category
BASE_FRONT           = "https://www.jarir.com/sa-en/"
BASE_API_PRODUCT     = "https://www.jarir.com/api/catalogv2/product/store/sa-en"
CATEGORIES = [
    ("office-supplies",    6),
    ("school-supplies",    146),
    ("toys-kids-learning", 235),
]
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": BASE_FRONT,
}

# ───────────────── session + retries ──────────────────────
session = requests.Session()
session.headers.update(HEADERS)
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429,500,502,503,504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.mount("http://",  adapter)
session.get(BASE_FRONT, timeout=15)  # seed cookies


# ─────────── hidden-API paginator ────────────────────────
def fetch_links_via_api(cat_id: int, page_size: int = LINK_FETCH_PAGE_SIZE) -> list[str]:
    links = []
    for offset in itertools.count(0, page_size):
        url = (
            f"{BASE_API_PRODUCT}/category_ids/{cat_id}/aggregation/true"
            f"/size/{page_size}/from/{offset}/sort-priority/asc"
        )
        r = session.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()

        def _collect(node):
            if isinstance(node, dict):
                if "url_path" in node:
                    yield node["url_path"]
                for v in node.values():
                    yield from _collect(v)
            elif isinstance(node, list):
                for item in node:
                    yield from _collect(item)

        paths = list(_collect(data))
        if not paths:
            break

        links.extend(urljoin(BASE_FRONT, p) for p in paths)

        # stop fetching once we've got enough
        if len(links) >= PRODUCT_LIMIT:
            break

    return list(dict.fromkeys(links))[:PRODUCT_LIMIT]


# ───────── brace‐balancer for inline product blob ─────────
def _extract_product_blob(txt: str) -> str:
    m = re.search(r'\bproduct\s*:', txt)
    start = txt.find("{", m.end())
    depth, i = 1, start + 1
    while depth and i < len(txt):
        depth += txt[i] == "{"
        depth -= txt[i] == "}"
        i += 1
    return txt[start:i]


# ─────────────────── field‐rename map ─────────────────────
REMAP = {
    "jarir_prcr":"cpu_model","prse":"cpu_model","prsd":"cpu_clock",
    "grpc":"gpu_model","symm":"ram","jarir_capa":"storage","tsca":"storage",
    "price":"regular_price_sar","special_price":"sale_price_sar",
    "jarir_mega_discount":"discount_percent","item_warranty_code":"warranty_code",
    "opsy":"os","osar":"os_arch","nepl":"ai_coprocessor","apai":"ai_enabled",
    "cote":"connectivity","port":"ports","seri":"series","ptyp":"product_type",
    "jarir_colo":"color","cofa":"color","widt":"width_cm","heig":"height_cm",
    "dept":"depth_cm","weig":"weight_kg","weight":"weight_kg",
    "scsz":"screen_size_inch","gere":"release_date",
    "scty":"screen_refresh_rate_hz","mxrs":"screen_resolution",
    "touc":"touchscreen","fing":"fingerprint_reader",
    "nesu":"network_speed","aufe":"audio_feature","feat":"special_features",
    "jarir_cars":"webcam","vren":"vr_ready",
}


# ─────────── tidy / auto‐map specs ─────────────────────────
def tidy(raw: dict) -> dict:
    dyn_keys = raw.get("productSpecification", {}) \
                 .get("attributes", "") \
                 .split(",")
    dyn_keys = [k.strip() for k in dyn_keys if k.strip()]
    out = {}
    for k, new in REMAP.items():
        if k in raw and raw[k] not in (None, "", "n/a"):
            out[new] = raw[k]
    for k in dyn_keys:
        if k in raw and k not in REMAP:
            out[k] = raw[k]
    if {"regular_price_sar","sale_price_sar"} <= out.keys() \
       and "discount_percent" not in out:
        r, s = out["regular_price_sar"], out["sale_price_sar"]
        out["discount_percent"] = round(100 * (r - s) / r)
    return out


# ───────────── scrape one product page ───────────────────
def scrape_product(url: str) -> dict:
    r = session.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    tag = next((t for t in soup.find_all("script")
                if 'product' in t.text and 'original' in t.text), None)
    if not tag:
        raise RuntimeError("product blob not found")
    blob = _extract_product_blob(tag.text)
    blob = html.unescape(blob).replace('!0','false').replace('!1','true')
    prod = json5.loads(blob)
    original = prod.get("original") or prod["product"]["original"]

    spec = tidy(original)
    spec["product_url"] = url

    table = soup.find("table")
    if table and table.find("th") and table.find("td"):
        for row in table.select("tr"):
            th = row.find("th"); td = row.find("td")
            if not th or not td: continue
            label = th.get_text(strip=True)
            val   = td.get_text(strip=True)
            key   = re.sub(r"\W+", "_", label.lower()).strip("_")
            if key and key not in spec:
                spec[key] = val

    return spec


# ───────── retry wrapper ──────────────────────────────────
def scrape_with_retries(url: str, retries: int = 2, delay: float = 1.0) -> dict:
    for attempt in range(retries + 1):
        try:
            return scrape_product(url)
        except Exception:
            if attempt < retries:
                time.sleep(delay)
                continue
            raise


# ───────────────────────── main ───────────────────────────
if __name__ == "__main__":
    all_start = time.time()

    for slug, cat_id in CATEGORIES:
        print(f"\n=== {slug} (ID={cat_id}) ===")
        t0 = time.time()

        # fetch and limit to PRODUCT_LIMIT
        links = fetch_links_via_api(cat_id)
        print(f"Fetched {len(links)} links (limited to {PRODUCT_LIMIT}) in {time.time()-t0:.1f}s")

        print(f"Scraping {len(links)} pages...")
        rows = []; succ = fail = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(scrape_with_retries, u): u for u in links}
            for fut in as_completed(futures):
                url = futures[fut]
                try:
                    rows.append(fut.result()); succ += 1
                    if succ % 10 == 0:
                        print(f"  → scraped {succ}/{len(links)}")
                except Exception:
                    fail += 1

        print(f"Done: {succ} OK, {fail} failed in {time.time()-t0:.1f}s")

        if rows:
            df = pd.DataFrame(rows)
            out = f"jarir_{slug}.csv"
            df.to_csv(out, index=False, encoding="utf-8-sig")
            print(f"✔ Saved {len(rows)} rows → {out}")

    print(f"\nAll categories done in {time.time()-all_start:.1f}s")
