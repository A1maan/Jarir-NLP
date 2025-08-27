#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jarir product scraper  —  unified scraper for tablets, laptops, desktops, CPUs, and gaming PCs
Features:
- Merged categories including gaming PCs (cat_id=1334)
- Includes SKU column
- Removed series, reordered columns (product_type, brand, model, sku)
- Excluded connectivity for tablets
- Grouped discount fields together
- Excludes non-product links to avoid category pages
"""

import time
import re
import html
import itertools
import json5
import pandas as pd
import requests
from requests.exceptions import ReadTimeout, ConnectTimeout, HTTPError
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ────────────────────────── constants ──────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.jarir.com/sa-en/",
}

BASE_API   = "https://www.jarir.com/api/catalogv2/product/store/sa-en"
BASE_FRONT = "https://www.jarir.com/sa-en/"

# Unified categories (including gaming PCs = 1334)
CATEGORIES = {
    "tablets"      : (1329, "jarir_tablets_raw.csv"),
    "2in1_laptops" : (1330, "jarir_2in1_laptops_raw.csv"),
    "laptops"      : (1331, "jarir_laptops_raw.csv"),
    "desktops"     : (1332, "jarir_desktops_raw.csv"),
    "cpu"          : (1333, "jarir_cpu_raw.csv"),
    "gaming_pcs"   : (1334, "jarir_gaming_pcs_raw.csv"),
}

PAGE_SIZE    = 12
REQ_TIMEOUT  = 20
MAX_RETRIES  = 2
MAX_WORKERS  = 12

# ─────────────────── helper: balanced JSON blob ───────────────────
def _extract_product_blob(script_text: str) -> str:
    m = re.search(r'\bproduct\s*:', script_text)
    if not m:
        raise ValueError("no 'product:' token found")
    start = script_text.find("{", m.end())
    if start == -1:
        raise ValueError("no opening brace after 'product:'")
    depth, i = 1, start + 1
    while depth and i < len(script_text):
        if script_text[i] == "{": depth += 1
        elif script_text[i] == "}": depth -= 1
        i += 1
    if depth != 0:
        raise ValueError("unbalanced braces in product blob")
    return script_text[start:i]

# ─────────────────── MAPPING (commented keys) ───────────────────
def detect_category(raw: dict) -> str:
    ptyp = (raw.get("ptyp") or "").lower()
    if "tablet"  in ptyp: return "tablet"
    if "laptop"  in ptyp: return "laptop"
    if "desktop" in ptyp: return "desktop"
    return "other"

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
    # color
    "jarir_colo":         "color",
    # weight
    "weig":               "weight_kg",
    "weight":             "weight_kg",
    # pricing fields
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
    "laptop":  {**COMMON, **LAPTOP_ONLY},
    "tablet":  {**COMMON, **TABLET_ONLY},
    "other":   COMMON,
}

# ─────────────────── tidy helper with ordering ───────────────────
def tidy(raw: dict) -> dict:
    cat = detect_category(raw)
    fmap = MAPS[cat]
    out = {}
    for old, new in fmap.items():
        val = raw.get(old)
        if val not in (None, "", "n/a") and new not in out:
            out[new] = val
    # exclude connectivity on tablets (not mapped)
    # derive discount percent if missing
    if "discount_percent" not in out and {"regular_price_sar","sale_price_sar"} <= out.keys():
        r,s = out["regular_price_sar"], out["sale_price_sar"]
        out["discount_percent"] = round(100*(r-s)/r)
    # build product_url
    url_val = None
    if "url_path" in out:
        url_val = urljoin(BASE_FRONT, out.pop("url_path"))
    # column ordering
    first = ["product_type","brand","model","sku"]
    group = ["discount_percent","regular_price_sar","sale_price_sar"]
    last  = ["product_url"]
    all_cols = set(out.keys())|{"product_url"}
    middle = sorted(c for c in all_cols if c not in first+group+last)
    ordered = first+group+middle+last
    final = {col: out.get(col,"") for col in ordered}
    if url_val: final["product_url"] = url_val
    return final

# ─────────────────── session setup ───────────────────
def make_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(HEADERS)
    retry_cfg = Retry(total=MAX_RETRIES, backoff_factor=0.6,
                      status_forcelist=[502,503,504], allowed_methods=["GET"],
                      raise_on_status=False)
    sess.mount("https://", HTTPAdapter(max_retries=retry_cfg))
    return sess
SESSION = make_session()

# ─────────────────── fetch product links (API) ───────────────────
def fetch_links_via_api(cat_id: int, page_size: int = PAGE_SIZE) -> list[str]:
    SESSION.get(BASE_FRONT, timeout=REQ_TIMEOUT)
    links, total = [], float('inf')
    for offset in itertools.count(0,page_size):
        if offset>=total: break
        url = f"{BASE_API}/category_ids/{cat_id}/aggregation/true/size/{page_size}/from/{offset}/sort-priority/asc"
        r = SESSION.get(url, timeout=REQ_TIMEOUT); r.raise_for_status()
        payload = r.json(); total = payload.get('totalHits',total)
        def _collect(node):
            if isinstance(node,dict):
                # only product nodes have numeric 'id'
                if 'url_path' in node and isinstance(node.get('id'),int):
                    yield node['url_path']
                for v in node.values(): yield from _collect(v)
            elif isinstance(node,list):
                for it in node: yield from _collect(it)
        paths = list(_collect(payload))
        if not paths: break
        links.extend(urljoin(BASE_FRONT,p) for p in paths)
    return list(dict.fromkeys(links))

# ─────────────────── parse single product ───────────────────
def parse_specs_raw(product_url: str) -> dict:
    for i in range(3):
        try:
            resp = SESSION.get(product_url, timeout=(5,REQ_TIMEOUT)); resp.raise_for_status()
            break
        except (ReadTimeout,ConnectTimeout):
            if i<2: time.sleep(0.5*(i+1)); continue
            raise
        except HTTPError as e:
            st = getattr(e.response,'status_code',None)
            if st and st>=500 and i<2: time.sleep(0.5*(i+1)); continue
            raise
    soup = BeautifulSoup(resp.text,'html.parser')
    tag = next((s for s in soup.find_all('script') if 'product' in s.get_text() and 'original' in s.get_text()),None)
    if not tag: raise RuntimeError('product blob <script> not found')
    blob = _extract_product_blob(tag.get_text())
    blob = html.unescape(blob).replace('!0','false').replace('!1','true')
    data = json5.loads(blob)
    orig = data.get('original') or data['product']['original']
    spec = orig.pop('productSpecification',{}) or {}
    if not isinstance(spec,dict): spec={}
    out = {**orig,**spec}
    out['product_url'] = product_url
    return out

# ─────────────────── scrape category ───────────────────
def scrape_category(name:str,cat_id:int,csv:str)->None:
    print(f"\n🟡 Scraping {name} (cat_id={cat_id}) …")
    links = fetch_links_via_api(cat_id)
    print(f" → {len(links)} product links")
    rows,fails,done=[],[],0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        fut2url={ex.submit(parse_specs_raw,u):u for u in links}
        for fut in as_completed(fut2url):
            url=fut2url[fut]; done+=1
            if done%10==0: print(f" … {done}/{len(links)}")
            try: rows.append(fut.result())
            except Exception as e: fails.append(url); print(f" ✘ {url} — {e}")
    for u in fails[:]:
        try: rows.append(parse_specs_raw(u)); fails.remove(u)
        except: pass
    if rows:
        cleaned=[tidy(r) for r in rows]
        df=pd.DataFrame(cleaned)
        out=csv.replace('_raw','')
        df.to_csv(out,index=False,encoding='utf-8-sig')
        print(f" ✅ Saved {out} ({len(df)} rows, {len(fails)} fails)")
    else: print(" ⚠️ No rows scraped!")

# ─────────────────── main ───────────────────
if __name__=='__main__':
    t0=time.time()
    for name,(cid,fname) in CATEGORIES.items():
        scrape_category(name,cid,fname)
    print(f"\n⏱️ Finished in {time.time()-t0:.1f}s")

