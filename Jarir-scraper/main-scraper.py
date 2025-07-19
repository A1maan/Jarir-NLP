import time, re, html, requests, pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 10   # tune this up or down
BASE_URL = "https://www.jarir.com"
CATEGORY_URL = "https://www.jarir.com/sa-en/gaming-pc-laptop-cpu.html"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",   # <- WAF expects this
    "Referer": "https://www.jarir.com/sa-en/",
}

# ───────────────────────── helpers ──────────────────────────
def get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")




import itertools, requests
from urllib.parse import urljoin

BASE_API   = "https://www.jarir.com/api/catalogv2/product/store/sa-en"
BASE_FRONT = "https://www.jarir.com/sa-en/"

def fetch_links_via_api(cat_id: int, page_size: int = 12, max_pages: int = 200) -> list[str]:
    """
    Return all product URLs for a Jarir category using the hidden catalog API.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    # warm-up: set cookies so API calls aren’t blocked
    session.get("https://www.jarir.com/sa-en/", timeout=15)

    links: list[str] = []
    for offset in itertools.count(0, page_size):          # 0, 12, 24, ...
        if offset // page_size >= max_pages:
            break

        url = (
            f"{BASE_API}/category_ids/{cat_id}/aggregation/true"
            f"/size/{page_size}/from/{offset}/sort-priority/asc"
        )
        r = session.get(url, timeout=15)
        if r.status_code == 403:
            raise RuntimeError("API blocked — headers/cookies not accepted")
        r.raise_for_status()

        payload = r.json()

        # ── recursively collect every "url_path" in the JSON ──
        def _collect(node):
            if isinstance(node, dict):
                if "url_path" in node:
                    yield node["url_path"]
                for v in node.values():
                    yield from _collect(v)
            elif isinstance(node, list):
                for item in node:
                    yield from _collect(item)

        new_paths = list(_collect(payload))
        if not new_paths:                       # no more products → stop
            break

        links.extend(urljoin(BASE_FRONT, p) for p in new_paths)

    # dedupe in case of overlap
    return list(dict.fromkeys(links))



# ───── add below get_soup() ─────────────────────────────────────
# def get_all_product_links(category_url: str, max_pages: int = 20) -> list[str]:
#     """Follow ?p=1,2,… until a page returns no product anchors."""
#     links = []
#     for page in range(1, max_pages + 1):
#         url  = f"{category_url}?p={page}"
#         soup = get_soup(url)
#         anchors = soup.select("a.product-tile__link[data-testid='productLink']")
#         if not anchors:                      # no more products → stop
#             break
#         links.extend(urljoin(BASE_URL, a["href"]) for a in anchors if a.get("href"))
#     return list(dict.fromkeys(links))        # dedupe



# def get_product_links(category_url: str) -> list[str]:
#     soup = get_soup(category_url)
#     anchors = soup.select("a.product-tile__link[data-testid='productLink']")
#     return [urljoin(BASE_URL, a["href"]) for a in anchors if a.get("href")]

# ────────────────────────── specs ───────────────────────────


import json5, re, html, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ------------------------------------------------------------------
#  a) brace-balancer → returns the exact JS object after  “product:”
# ------------------------------------------------------------------


def _extract_product_blob(script_text: str) -> str:
    """
    Given the full <script> text, return the balanced substring
    that starts at the first '{' after 'product:' and ends at
    its matching '}'.
    """
    # locate the literal "product:" (avoid productName, etc.)
    m = re.search(r'\bproduct\s*:', script_text)
    if not m:
        raise ValueError("no 'product:' token found")
    start = script_text.find("{", m.end())
    if start == -1:
        raise ValueError("no opening brace after 'product:'")

    depth, i = 1, start + 1
    while depth and i < len(script_text):
        if script_text[i] == "{":
            depth += 1
        elif script_text[i] == "}":
            depth -= 1
        i += 1
    if depth != 0:
        raise ValueError("unbalanced braces")

    return script_text[start:i]



# ------------------------------------------------------------------
#  b) slim field map  → turn Jarir’s terse keys into something sane
# ------------------------------------------------------------------


# 1) category detector (unchanged)
def detect_category(raw: dict) -> str:
    ptyp = (raw.get("ptyp") or "").lower()
    if "laptop"  in ptyp: return "laptop"
    if "desktop" in ptyp: return "desktop"
    return "other"

# 2) COMMON keys (applies to all)
COMMON = {
    # hardware
    "jarir_prcr":  "cpu_model",
    "prse":        "cpu_model",
    "prsd":        "cpu_clock",
    "grpc":        "gpu_model",
    "symm":        "ram",
    "jarir_capa":  "storage",
    "tsca":        "storage",

    # platform / OS
    "opsy":        "os",
    "osar":        "os_arch",
    "nepl":        "ai_coprocessor",
    "apai":        "ai_enabled",
    "cote":        "connectivity",
    "port":        "ports",

    # cosmetics & misc
    "seri":        "series",
    "ptyp":        "product_type",
    "jarir_colo":  "color",
    "cofa":        "color",

    # dimensions & weight
    "widt":        "width_cm",
    "heig":        "height_cm",
    "dept":        "depth_cm",
    "weig":        "weight_kg",
    "weight":      "weight_kg",

    # price
    "price":            "regular_price_sar",
    "special_price":    "sale_price_sar",
    "jarir_mega_discount": "discount_percent",

    # misc
    "item_warranty_code": "warranty_code",
    "url_path":          "url_path",
}

DESKTOP_ONLY = {
    # nothing extra for desktops now
}

LAPTOP_ONLY = {
    "scsz": "screen_size_inch",
    "gere": "release_date",              # ← repurposed
    "scty": "screen_refresh_rate_hz",    # ← repurposed
    "mxrs": "screen_resolution",         # ← repurposed
    "touc": "touchscreen",
    "fing": "fingerprint_reader",
    "nesu": "network_speed",
    "aufe": "audio_feature",
    "feat": "special_features",
    "jarir_cars": "webcam",              # ← repurposed
    "vren": "vr_ready",
}

MAPS = {
    "desktop": {**COMMON, **DESKTOP_ONLY},
    "laptop":  {**COMMON, **LAPTOP_ONLY},
    "other":   COMMON,
}



# 3) tidy() helper
from urllib.parse import urljoin

def tidy(raw: dict) -> dict:
    cat = detect_category(raw)
    fmap = MAPS[cat]

    out = {}
    for old, new in fmap.items():
        val = raw.get(old)
        if val not in (None, "", "n/a") and new not in out:
            out[new] = val

    # derive discount if missing
    if "discount_percent" not in out and \
       {"regular_price_sar", "sale_price_sar"} <= out.keys():
        r, s = out["regular_price_sar"], out["sale_price_sar"]
        out["discount_percent"] = round(100 * (r - s) / r)

    # single, fully-qualified URL
    if "url_path" in out:
        out["product_url"] = urljoin("https://www.jarir.com/sa-en/", out.pop("url_path"))

    # ── final column order ──
    # put product_type first, product_url last, everything else in between
    first  = ["product_type", "series"]   # series now 2nd column
    last   = ["product_url"]
    middle = [c for c in out.keys() if c not in first + last]
    ordered = first + middle + last
    return {col: out.get(col, "") for col in ordered}



# ────────────────────────── specific product scraper ──────────────────────────



def parse_specs(product_url: str) -> dict:
    resp = requests.get(product_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # 1️⃣  grab the <script> tag that contains the blob
    script_tag = next(
        (s for s in soup.find_all("script")
         if 'product' in s.get_text() and 'original' in s.get_text()),
        None
    )
    if not script_tag:
        raise RuntimeError("product blob <script> not found")

    # 2️⃣  carve out the balanced object text
    blob = _extract_product_blob(script_tag.get_text())

    # 3️⃣  normalise JS booleans & HTMLEntities
    blob = html.unescape(blob)
    blob = blob.replace('!0', 'false').replace('!1', 'true')

    # 4️⃣  parse with json5  →  Python dict
    product_dict = json5.loads(blob)
    original = product_dict.get("original") or product_dict["product"]["original"]

    # 5️⃣  tidy / rename fields for CSV friendliness
    return tidy(original)




# ───────────────────────── orchestrator ─────────────────────
if __name__ == "__main__":
    product_links = fetch_links_via_api(cat_id=1334)  # gaming laptops & CPUs    
    print(f"Found {len(product_links)} product links")

    all_specs = []

    # ── parallel scraping ──────────────────────────────────────────
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(parse_specs, link): link
            for link in product_links
        }
        for fut in as_completed(futures):
            link = futures[fut]
            try:
                spec_dict = fut.result()
                # ensure the final product_url is set
                spec_dict["product_url"] = link
                all_specs.append(spec_dict)
                print(f"✔ scraped {link}")
            except Exception as e:
                print(f"✘ {link} — {e}")
    # ── end parallel ────────────────────────────────────────────────

    # now save
    pd.DataFrame(all_specs).to_csv(
        "jarir_pc_specs.csv",
        index=False,
        encoding="utf-8-sig"
    )
    print("✅ Saved specs to jarir_pc_specs.csv")
