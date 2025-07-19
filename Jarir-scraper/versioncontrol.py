import time, re, html, requests, pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json5
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
    "Accept-Language": "en-US,en;q=0.9",
}

# ───────────────────────── helpers ──────────────────────────
def get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")



def get_product_links(category_url: str) -> list[str]:
    soup = get_soup(category_url)
    anchors = soup.select("a.product-tile__link[data-testid='productLink']")
    return [urljoin(BASE_URL, a["href"]) for a in anchors if a.get("href")]

# ────────────────────────── specs ───────────────────────────




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
    product_links = get_product_links(CATEGORY_URL)
    print(f"Found {len(product_links)} product links")

    all_specs = []
    for i, link in enumerate(product_links, 1):
        try:
            spec_dict = parse_specs(link)
            spec_dict["Product URL"] = link
            all_specs.append(spec_dict)
            print(f"[{i}/{len(product_links)}] ✔ scraped {link}")
        except Exception as e:
            print(f"[{i}/{len(product_links)}] ✘ {link} — {e}")
        time.sleep(1)       # polite crawl

    pd.DataFrame(all_specs).to_csv("jarir_pc_specs.csv",
                                   index=False, encoding="utf-8-sig")
    print("✅ Saved specs to jarir_pc_specs.csv")
