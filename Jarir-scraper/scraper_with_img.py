#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarir product scraper — tablets, laptops, desktops, CPUs & gaming PCs
PATCH 2025-08-01
    • adds `image_url` column via <meta property="og:image"> or JSON fallback
"""

import time, re, html, itertools, json5, pandas as pd, requests
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ───────────────────────── constants ──────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.jarir.com/sa-en/",
}

BASE_API   = "https://www.jarir.com/api/catalogv2/product/store/sa-en"
BASE_FRONT = "https://www.jarir.com/sa-en/"

CATEGORIES = {
    "tablets"      : (1329, "jarir_tablets_raw.csv"),
    "2in1_laptops" : (1330, "jarir_2in1_laptops_raw.csv"),
    "laptops"      : (1331, "jarir_laptops_raw.csv"),
    "desktops"     : (1332, "jarir_desktops_raw.csv"),
    "cpu"          : (1333, "jarir_cpu_raw.csv"),
    "gaming_pcs"   : (1334, "jarir_gaming_pcs_raw.csv"),
}

PAGE_SIZE, REQ_TIMEOUT, MAX_RETRIES, MAX_WORKERS = 12, 20, 2, 12

# ───────────────── helper: balanced JSON blob ────────────────
def _extract_product_blob(txt: str) -> str:
    m = re.search(r'\bproduct\s*:', txt)
    if not m:  raise ValueError("no 'product:' token found")
    start = txt.find("{", m.end())
    if start == -1: raise ValueError("no opening brace after 'product:'")
    depth, i = 1, start + 1
    while depth and i < len(txt):
        depth += txt[i] == "{"
        depth -= txt[i] == "}"
        i += 1
    if depth: raise ValueError("unbalanced braces in product blob")
    return txt[start:i]

# ───────────────── category detection ─────────────────────────
def detect_category(raw: dict) -> str:
    p = (raw.get("ptyp") or "").lower()
    if "tablet"  in p: return "tablet"
    if "laptop"  in p: return "laptop"
    if "desktop" in p: return "desktop"
    return "other"

# ───────────────── field maps ────────────────────────────────
COMMON = {
    # SKU
    "sku":                "sku",
    # hardware
    "prse":               "cpu_model",
    "prsd":               "cpu_clock",
    "grpc":               "gpu_model",
    "symm":               "ram",
    "jarir_capa":         "storage",
    "tsca":               "storage",
    # platform / OS
    "opsy":               "os",
    "nepl":               "ai_coprocessor",
    "apai":               "ai_enabled",
    # product info
    "ptyp":               "product_type",
    "brand":              "brand",
    "model":              "model",
    "url_path":           "url_path",
    # colour & weight
    "jarir_colo":         "color",
    "weig":               "weight_kg",
    "weight":             "weight_kg",
    # pricing
    "price":              "regular_price_sar",
    "special_price":      "sale_price_sar",
    "jarir_mega_discount":"discount_percent",
}

LAPTOP_ONLY = {
    "scsz":       "screen_size_inch",
    "gere":       "release_date",
    "scty":       "screen_refresh_rate_hz",
    "mxrs":       "screen_resolution",
    "touc":       "touchscreen",
    "nesu":       "network_speed",
    "aufe":       "audio_feature",
    "feat":       "special_features",
    "jarir_cars": "webcam",
}

TABLET_ONLY = {
    "scsz": "screen_size_inch",
    "scre": "screen_type",
    "scty": "screen_refresh_rate_hz",
    "feat": "special_features",
    "nsim": "sim_slots",
}

MAPS = {
    "desktop": COMMON,
    "laptop" : {**COMMON, **LAPTOP_ONLY},
    "tablet" : {**COMMON, **TABLET_ONLY},
    "other"  : COMMON,
}

# ───────────────── tidy helper ───────────────────────────────
def tidy(raw: dict) -> dict:
    fmap, out = MAPS[detect_category(raw)], {}
    for old, new in fmap.items():
        val = raw.get(old)
        if val not in (None, "", "n/a") and new not in out:
            out[new] = val

    if "discount_percent" not in out and {"regular_price_sar","sale_price_sar"} <= out.keys():
        r, s = out["regular_price_sar"], out["sale_price_sar"]
        out["discount_percent"] = round(100 * (r - s) / r)

    url_val = urljoin(BASE_FRONT, out.pop("url_path")) if "url_path" in out else None
    # **NEW**: pull through image_url
    out["image_url"] = raw.get("image_url", "")

    # ───────────────── column ordering ───────────────────────
    first = ["product_type","brand","model","sku"]
    group = ["discount_percent","regular_price_sar","sale_price_sar"]
    middle = sorted(c for c in set(out.keys()) - set(first+group+["product_url"]))
    last   = ["product_url", "image_url"]   # ← put image_url here

    ordered = first + group + middle + last

    final = {col: out.get(col, "") for col in ordered}
    if url_val:
        final["product_url"] = url_val

    return final

# ───────────────── session setup ───────────────────────────
def make_session() -> requests.Session:
    s = requests.Session(); s.headers.update(HEADERS)
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=MAX_RETRIES, backoff_factor=0.6,
        status_forcelist=[502,503,504], allowed_methods=["GET"]
    )))
    return s
SESSION = make_session()

# ───────────────── fetch links via API ─────────────────────
def fetch_links_via_api(cat_id: int) -> list[str]:
    SESSION.get(BASE_FRONT, timeout=REQ_TIMEOUT)
    links, total = [], float("inf")
    for off in itertools.count(0, PAGE_SIZE):
        if off >= total: break
        url = f"{BASE_API}/category_ids/{cat_id}/aggregation/true/size/{PAGE_SIZE}/from/{off}/sort-priority/asc"
        payload = SESSION.get(url, timeout=REQ_TIMEOUT).json()
        total   = payload.get("totalHits", total)

        def _walk(node):
            if isinstance(node, dict):
                if "url_path" in node and isinstance(node.get("id"), int):
                    yield node["url_path"]
                for v in node.values(): yield from _walk(v)
            elif isinstance(node, list):
                for it in node: yield from _walk(it)

        paths = list(_walk(payload))
        if not paths: break
        links.extend(urljoin(BASE_FRONT, p) for p in paths)
    return list(dict.fromkeys(links))

# ───────────────── hero-image extractor ────────────────────
def extract_image_url(soup: BeautifulSoup, orig: dict) -> str:
    tag = soup.find("meta", property="og:image")
    if tag and tag.has_attr("content"):
        return tag["content"]

    for key in ("media_gallery", "mediaGallery"):
        gallery = orig.get(key) or []
        if isinstance(gallery, list):
            for item in gallery:
                if isinstance(item, dict) and item.get("isMain"):
                    url = item.get("url")
                    if url:
                        return url if url.startswith("http") else "https:" + url

    media = orig.get("media") or {}
    for k in ("heroImage", "imageUrl", "thumbnailUrl", "url"):
        val = media.get(k)
        if isinstance(val, str) and val:
            return val if val.startswith("http") else "https:" + val
    return ""

# ───────────────── parse one product ───────────────────────
def parse_specs_raw(product_url: str) -> dict:
    for i in range(3):
        try:
            r = SESSION.get(product_url, timeout=(5, REQ_TIMEOUT)); r.raise_for_status()
            break
        except (ReadTimeout, ConnectTimeout):
            if i < 2: time.sleep(0.5*(i+1)); continue
            raise
        except HTTPError as e:
            if getattr(e.response, "status_code", 0) >= 500 and i < 2:
                time.sleep(0.5*(i+1)); continue
            raise

    soup = BeautifulSoup(r.text, "html.parser")
    tag  = next((s for s in soup.find_all("script")
                 if "product" in s.get_text() and "original" in s.get_text()), None)
    if not tag: raise RuntimeError("<script> with product blob not found")

    blob = html.unescape(_extract_product_blob(tag.get_text())) \
                .replace("!0", "false").replace("!1", "true")
    data = json5.loads(blob)

    orig = data.get("original") or data["product"]["original"]
    spec = orig.pop("productSpecification", {}) or {}
    if not isinstance(spec, dict): spec = {}

    out = {**orig, **spec}
    out["product_url"] = product_url
    out["image_url"]   = extract_image_url(soup, orig)
    return out

# ───────────────── scrape one category ────────────────────
def scrape_category(name: str, cid: int, csv_raw: str) -> None:
    print(f"\n🟡 Scraping {name} (cat_id={cid}) …")
    links = fetch_links_via_api(cid)
    print(f" → {len(links)} product links")
    rows, fails, done = [], [], 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        fut2url = {ex.submit(parse_specs_raw, u): u for u in links}
        for fut in as_completed(fut2url):
            url = fut2url[fut]; done += 1
            if done % 10 == 0: print(f" … {done}/{len(links)}")
            try: rows.append(fut.result())
            except Exception as e:
                fails.append(url); print(f" ✘ {url} — {e}")

    # retry fails once more
    for u in fails[:]:
        try: rows.append(parse_specs_raw(u)); fails.remove(u)
        except: pass

    if rows:
        df = pd.DataFrame([tidy(r) for r in rows])
        out = csv_raw.replace("_raw", "")
        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f" ✅ Saved {out} ({len(df)} rows, {len(fails)} fails)")
    else:
        print(" ⚠️ No rows scraped!")

# ───────────────── main ─────────────────────────────────
if __name__ == "__main__":
    start = time.time()
    for name, (cid, fname) in CATEGORIES.items():
        scrape_category(name, cid, fname)
    print(f"\n⏱️ Finished in {time.time() - start:.1f}s")
