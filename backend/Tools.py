from VaDGen import hybrid_search_catalog
from VaDGen import create_catalog_index
from typing import Set, TypedDict, List, Dict, Any, Optional
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_core.tools import tool
import json
import pandas as pd
from typing import List, Dict, Any
from langchain_core.tools import tool
from agent_core import display_product_recommendations
from pydantic import BaseModel, Field, ConfigDict, AliasChoices


llm = init_chat_model("google_genai:gemini-2.5-flash")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# Define the catalog index for  gaming laptops
GAMING_CSV_PATH = "../Jarir-scraper/jarir_gaming_pcs.csv"
GAMING_SPEC_COLUMNS = ["brand", "model", "cpu_model", "gpu_model", "ram", "storage","price"]  
gaming_laptop_catalog = create_catalog_index(GAMING_CSV_PATH, GAMING_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_gaming_laptops(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
    specs: e.g.
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"i7-12700H",
       "gpu_model":"RTX3070",
       "ram":"16 GB RAM",
       "storage":"512GB"
       "price":""}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, gaming_laptop_catalog)
    if not candidates:
        return "No similar products  found."

    # grab the DataFrame out of the catalog
    df = gaming_laptop_catalog["df"]

    rows = []
    for c in candidates:
        # find the matching row by its id
        row = (
            df.loc[df["id"] == c["id"]]
              .iloc[0]                   # get the single matching record
              .to_dict()
        )
        rows.append(row)

    # prompt = f"""
    # I need a product matching these specs: {specs}.
    # Here are 5 candidate products:
    # {rows}
    # Please rank them from best to worst match and briefly explain why.
    # Return only JSON in the form:
    #   [
    #     {{"id":..., "match_level":"exact|partial|vector", "reason":"…"}}, 
    #     …
    #   ]
    # """

    # # 3) invoke the LLM for the final ranking
    # res = llm.invoke([
    #     SystemMessage(content="You are an expert at matching products to user specs."),
    #     HumanMessage(content=prompt)
    # ])
    # llm_output = res.content  # e.g. JSON string of id+reason
    # ranking = json.loads(llm_output)
    # return {
    #   "results": rows,      # full spec dicts
    #   "ranking": ranking    # id + match_level + reason
    # }
    return{
        "results": rows,
    }


#-------------------------------------------------------------------------------------------------
# Define the catalog index for  laptops

LAPTOP_CSV_PATH = "../Jarir-scraper/jarir_laptops.csv"
LAPTOP_SPEC_COLUMNS = ["brand", "model", "cpu_model", "gpu_model", "ram", "storage", "renewed","price"]  
LAPTOP_catalog = create_catalog_index(LAPTOP_CSV_PATH, LAPTOP_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_laptops(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"Intel Core Ultra 7",
       "gpu_model":"Qualcomm Adreno GPU",
       "ram":"16 GB RAM",
       "storage":"512GB",
       "renewed"":"renewed or new",
       "price":""}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, LAPTOP_catalog)
    if not candidates:
        return "No similar products  found."

    # grab the DataFrame out of the catalog
    df = LAPTOP_catalog["df"]

    rows = []
    for c in candidates:
        # find the matching row by its id
        row = (
            df.loc[df["id"] == c["id"]]
              .iloc[0]                   # get the single matching record
              .to_dict()
        )
        rows.append(row)

    # prompt = f"""
    # I need a product matching these specs: {specs}.
    # Here are 5 candidate products:
    # {rows}
    # Please rank them from best to worst match and briefly explain why.
    # Return only JSON in the form:
    #   [
    #     {{"id":..., "match_level":"exact|partial|vector", "reason":"…"}}, 
    #     …
    #   ]
    # """

    # # 3) invoke the LLM for the final ranking
    # res = llm.invoke([
    #     SystemMessage(content="You are an expert at matching products to user specs."),
    #     HumanMessage(content=prompt)
    # ])
    # llm_output = res.content  # e.g. JSON string of id+reason
    # ranking = json.loads(llm_output)
    # return {
    #   "results": rows,      # full spec dicts
    #   "ranking": ranking    # id + match_level + reason
    # }
    return{
        "results": rows,
    }
    
    
    
    
    
    
    
    
#-------------------------------------------------------------------------------------------------
# Define the catalog index for  Tablets

TABLET_CSV_PATH = "../Jarir-scraper/jarir_tablets.csv"
TABLET_SPEC_COLUMNS = ["brand", "model", "cpu_clock","ram", "storage","color", "renewed","price"]  
TABLET_catalog = create_catalog_index(TABLET_CSV_PATH, TABLET_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_tablets(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_clock":"1.8 GHz",
       "ram":"16 GB RAM",
       "storage":"512GB",
       "color":"Black"
       "renewed":"renewed or new",
       "price":""}

    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, TABLET_catalog)
    if not candidates:
        return "No similar products  found."

    # grab the DataFrame out of the catalog
    df = TABLET_catalog["df"]

    rows = []
    for c in candidates:
        # find the matching row by its id
        row = (
            df.loc[df["id"] == c["id"]]
              .iloc[0]                   # get the single matching record
              .to_dict()
        )
        rows.append(row)

    prompt = f"""
    I need a product matching these specs: {specs}.
    Here are 5 candidate products:
    {rows}
    Please rank them from best to worst match and briefly explain why.
    Return only JSON in the form:
      [
        {{"id":..., "match_level":"exact|partial|vector", "reason":"…"}}, 
        …
      ]
    """

    # 3) invoke the LLM for the final ranking
    # prompt = f"""
    # I need a product matching these specs: {specs}.
    # Here are 5 candidate products:
    # {rows}
    # Please rank them from best to worst match and briefly explain why.
    # Return only JSON in the form:
    #   [
    #     {{"id":..., "match_level":"exact|partial|vector", "reason":"…"}}, 
    #     …
    #   ]
    # """

    # # 3) invoke the LLM for the final ranking
    # res = llm.invoke([
    #     SystemMessage(content="You are an expert at matching products to user specs."),
    #     HumanMessage(content=prompt)
    # ])
    # llm_output = res.content  # e.g. JSON string of id+reason
    # ranking = json.loads(llm_output)
    # return {
    #   "results": rows,      # full spec dicts
    #   "ranking": ranking    # id + match_level + reason
    # }
    return{
        "results": rows,
    }
    
    
    
#-------------------------------------------------------------------------------------------------
# Define the catalog index for  2in1 laptops

twoin1_CSV_PATH = "../Jarir-scraper/jarir_twoin1_laptops.csv"
twoin1_SPEC_COLUMNS = ["brand", "model", "cpu_model","gpu_model","ram", "storage","price"]  
twoin1_catalog = create_catalog_index(twoin1_CSV_PATH, twoin1_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_twoin1(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"",
       "ram":"16 GB RAM",
       "storage":"512GB",
       "gpu_model":"",
       "price":""}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, twoin1_catalog)
    if not candidates:
        return "No similar products  found."

    # grab the DataFrame out of the catalog
    df = twoin1_catalog["df"]

    rows = []
    for c in candidates:
        # find the matching row by its id
        row = (
            df.loc[df["id"] == c["id"]]
              .iloc[0]                   # get the single matching record
              .to_dict()
        )
        rows.append(row)

    # prompt = f"""
    # I need a product matching these specs: {specs}.
    # Here are 5 candidate products:
    # {rows}
    # Please rank them from best to worst match and briefly explain why.
    # Return only JSON in the form:
    #   [
    #     {{"id":..., "match_level":"exact|partial|vector", "reason":"…"}}, 
    #     …
    #   ]
    # """

    # # 3) invoke the LLM for the final ranking
    # res = llm.invoke([
    #     SystemMessage(content="You are an expert at matching products to user specs."),
    #     HumanMessage(content=prompt)
    # ])
    # llm_output = res.content  # e.g. JSON string of id+reason
    # ranking = json.loads(llm_output)
    # return {
    #   "results": rows,      # full spec dicts
    #   "ranking": ranking    # id + match_level + reason
    # }
    return{
        "results": rows,
    }
    
    
    
    
    
    
    
#-------------------------------------------------------------------------------------------------
# Define the catalog index for  desktops

DESKTOPS_CSV_PATH = "../Jarir-scraper/jarir_AIO.csv"
DESKTOPS_SPEC_COLUMNS = ["brand", "model", "cpu_model","gpu_model","ram", "storage","price"]  
DESKTOPS_catalog = create_catalog_index(DESKTOPS_CSV_PATH, DESKTOPS_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_desktops(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"",
       "ram":"16 GB RAM",
       "storage":"512GB",
       "gpu_model":"",
       "price":""}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, DESKTOPS_catalog)
    if not candidates:
        return "No similar products  found."

    # grab the DataFrame out of the catalog
    df = DESKTOPS_catalog["df"]

    rows = []
    for c in candidates:
        # find the matching row by its id
        row = (
            df.loc[df["id"] == c["id"]]
              .iloc[0]                   # get the single matching record
              .to_dict()
        )
        rows.append(row)

    # prompt = f"""
    # I need a product matching these specs: {specs}.
    # Here are 5 candidate products:
    # {rows}
    # Please rank them from best to worst match and briefly explain why.
    # Return only JSON in the form:
    #   [
    #     {{"id":..., "match_level":"exact|partial|vector", "reason":"…"}}, 
    #     …
    #   ]
    # """

    # # 3) invoke the LLM for the final ranking
    # res = llm.invoke([
    #     SystemMessage(content="You are an expert at matching products to user specs."),
    #     HumanMessage(content=prompt)
    # ])
    # llm_output = res.content  # e.g. JSON string of id+reason
    # ranking = json.loads(llm_output)
    # return {
    #   "results": rows,      # full spec dicts
    #   "ranking": ranking    # id + match_level + reason
    # }
    return{
        "results": rows,
    }
    
#-------------------------------------------------------------------------------------------------
# Define the catalog index for  AIO devices 

AIO_CSV_PATH = "../Jarir-scraper/jarir_AIO.csv"
AIO_SPEC_COLUMNS = ["brand", "model", "cpu_model","gpu_model","ram", "storage", "price"]  
AIO_catalog = create_catalog_index(AIO_CSV_PATH, AIO_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_AIO(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"",
       "ram":"16 GB RAM",
       "storage":"512GB",
       "gpu_model":"",
       "price":""}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, AIO_catalog)
    if not candidates:
        return "No similar products  found."

    # grab the DataFrame out of the catalog
    df = AIO_catalog["df"]

    rows = []
    for c in candidates:
        # find the matching row by its id
        row = (
            df.loc[df["id"] == c["id"]]
              .iloc[0]                   # get the single matching record
              .to_dict()
        )
        rows.append(row)

    # prompt = f"""
    # I need a product matching these specs: {specs}.
    # Here are 5 candidate products:
    # {rows}
    # Please rank them from best to worst match and briefly explain why.
    # Return only JSON in the form:
    #   [
    #     {{"id":..., "match_level":"exact|partial|vector", "reason":"…"}}, 
    #     …
    #   ]
    # """

    # # 3) invoke the LLM for the final ranking
    # res = llm.invoke([
    #     SystemMessage(content="You are an expert at matching products to user specs."),
    #     HumanMessage(content=prompt)
    # ])
    # llm_output = res.content  # e.g. JSON string of id+reason
    # ranking = json.loads(llm_output)
    # return {
    #   "results": rows,      # full spec dicts
    #   "ranking": ranking    # id + match_level + reason
    # }
    return{
        "results": rows,
    }
    
       



#---------------------------------------------------------
# Get available models for the required brand

csv_paths = [GAMING_CSV_PATH, LAPTOP_CSV_PATH, TABLET_CSV_PATH , twoin1_CSV_PATH , DESKTOPS_CSV_PATH, AIO_CSV_PATH]

import pandas as pd
from pathlib import Path
from typing import Dict, List

def build_brand_first_map(csv_paths: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """
    Read each CSV at the given file paths (each must have 'brand' and 'model' cols),
    and merge into one dict mapping:

        brand → { product_type → sorted list of unique models }.

    The product_type is taken from the CSV filename stem, e.g. 'tablet' for 'tablet.csv'.
    """
    brand_first_map: Dict[str, Dict[str, List[str]]] = {}

    for path in csv_paths:
        # derive product_type from filename
        product_type = Path(path).stem
        if product_type.lower().endswith("_csv_path"):
            product_type = product_type[: -len("_csv_path")]
        product_type = product_type.lower()

        # read only the brand & model columns
        df = pd.read_csv(path, usecols=['brand', 'model'])

        # for each brand, collect its models under this product_type
        for brand in df['brand'].dropna().unique():
            models = (
                df.loc[df['brand'] == brand, 'model']
                  .dropna()
                  .unique()
                  .tolist()
            )
            models = sorted(models)
            # initialize brand entry if needed
            if brand not in brand_first_map:
                brand_first_map[brand] = {}
            # assign the list under this product_type
            brand_first_map[brand][product_type] = models

    return brand_first_map


brand_model_map = build_brand_first_map(csv_paths)

def retrieve_information_about_brand(brand: str) -> Dict[str, List[str]]:
    """
    Given a brand name, returns a dict mapping each product_type
    to the list of models available under that brand.
    If the brand is not found, returns an empty dict.
    """
    return brand_model_map.get(brand, {})


#--------------------------



def build_product_type_first_map(csv_paths: List[str]) -> Dict[str, Dict[str, List[str]]]:
    """
    Read each CSV at the given file paths (each must have 'brand' and 'model' cols),
    and merge into one dict mapping:

        product_type → { brand → sorted list of unique models }.

    product_type will be one of:
      ['gaming', 'laptop', 'tablet', 'twoin1_laptop', 'desktops','AIO']
    """
    nested_map: Dict[str, Dict[str, List[str]]] = {}

    for path in csv_paths:
        # 1) derive normalized product_type
        stem = Path(path).stem.lower()            # e.g. "jarir_gaming_pcs"
        if stem.startswith("jarir_"):
            stem = stem[len("jarir_"):]           # → "gaming_pcs"
        stem = stem.replace("_pcs", "")           # → "gaming"
        # singularize where needed:
        if stem.endswith("s") and stem not in ("desktops",):
            stem = stem[:-1]                      # "laptops"→"laptop", "tablets"→"tablet"
        product_type = stem                       # now one of gaming, laptop, tablet, twoin1, desktops

        # 2) read & group
        df = pd.read_csv(path, usecols=["brand", "model"])
        brand_map: Dict[str, List[str]] = {}
        for brand in df["brand"].dropna().unique():
            models = (
                df.loc[df["brand"] == brand, "model"]
                  .dropna()
                  .unique()
                  .tolist()
            )
            brand_map[brand] = sorted(models)

        nested_map[product_type] = brand_map

    return nested_map

product_type_map = build_product_type_first_map(csv_paths)

def retrieve_information_about_product_type(product_type: str) -> Dict[str, List[str]]:
    """
    These are the available product_type ['gaming', 'laptop', 'tablet', 'twoin1_laptop', 'desktops','AIO']
    Given a product type, returns a dict mapping each brand
    to the list of models available under that product_type.
    """
    return product_type_map.get(product_type.lower(), {})





#----------------------------------------------------------
# Consolidation tool (backend version)

def _map_raw_product_to_card(product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Map a raw row (from CSV → dict) to the frontend card shape expected by
    consolidate/display tools. Uses fallback values instead of filtering out products.
    
    CSV columns: product_type,brand,model,sku,discount_percent,regular_price_sar,sale_price_sar,
    ai_coprocessor,ai_enabled,color,cpu_clock,cpu_model,gpu_model,image_url,os,ram,release_date,
    screen_refresh_rate_hz,screen_resolution,screen_size_inch,storage,touchscreen,webcam,weight_kg,
    product_url,audio_feature,special_features,price,renewed
    """
    try:
        # ID can be from various fields
        product_id = str(product.get("id") or product.get("sku") or "")
        if not product_id:
            print(f"[DEBUG] Product filtered: Missing ID/SKU - {product}")
            return None

        brand = str(product.get("brand") or "").strip()
        model = str(product.get("model") or "").strip()
        name = (brand + " " + model).strip() or "Product"

        # Image URL - use fallback if missing
        image = product.get("image_url") or ""
        if not image or not image.startswith("http"):
            image = "https://via.placeholder.com/300x200?text=No+Image"
            print(f"[DEBUG] Using placeholder image for product {product_id}: {name}")

        # Price handling - CSV has 'sale_price_sar', 'regular_price_sar', and 'price'
        price_value: Optional[float] = None
        for pf in ("sale_price_sar", "price", "regular_price_sar"):
            val = product.get(pf)
            if val not in (None, "", "NaN", "nan") and str(val).strip():
                try:
                    price_value = float(str(val).replace("SAR", "").replace(",", "").strip())
                    break
                except (ValueError, TypeError):
                    continue
        if price_value is None:
            price_value = 0.0
            print(f"[DEBUG] No valid price found for product {product_id}: {name}")

        # Product URL - use fallback if missing
        url = product.get("product_url") or ""
        if not url:
            url = "https://www.jarir.com/"
            print(f"[DEBUG] Using fallback URL for product {product_id}: {name}")

        # Build badges from available data
        badges: List[str] = []
        discount = product.get("discount_percent")
        if discount and str(discount).lower() not in ('nan', 'none', '', 'null'):
            badges.append(f"{discount} off")
        if str(product.get("renewed") or "").lower() == "renewed":
            badges.append("Renewed")
        else:
            badges.append("New")

        return {
            "id": product_id,
            "name": name,
            "image": image,
            "priceSar": price_value,
            "url": url,
            "badges": badges,
            # Keep additional fields for grouping
            "color": product.get("color"),
            "brand": brand,
            "model": model,
            "cpu_model": product.get("cpu_model"),
            "gpu_model": product.get("gpu_model"),
            "ram": product.get("ram"),
            "storage": product.get("storage"),
            "screen_size_inch": product.get("screen_size_inch"),
        }
    except Exception as e:
        print(f"Error mapping product {product.get('id', 'unknown')}: {e}")
        return None


@tool
def consolidate_products(products: Any) -> List[Dict[str, Any]]:
    """
    Consolidate raw product dicts into grouped product cards by core specs, ignoring color.
    Accepts rows directly from search tools (e.g., check_laptops). Handles missing keys gracefully.
    """
    # Coerce input: accept either a dict with 'results' or a list of dicts
    if isinstance(products, dict) and "results" in products:
        raw_list = products.get("results") or []
    else:
        raw_list = products or []

    print(f"[DEBUG] consolidate_products received {len(raw_list)} raw products")
    
    # First normalize all raw products to the card shape
    normalized: List[Dict[str, Any]] = []
    for i, p in enumerate(raw_list):
        mapped = _map_raw_product_to_card(p)
        if mapped:
            normalized.append(mapped)
        else:
            print(f"[DEBUG] Product {i} was filtered out during mapping")

    print(f"[DEBUG] After mapping: {len(normalized)} products normalized successfully")
    
    if not normalized:
        print("[DEBUG] No products after normalization - returning empty list")
        return []

    # Group by core specs
    groups: Dict[tuple, Dict[str, Any]] = {}
    for item in normalized:
        key = (
            item.get("brand"),
            item.get("model"),
            item.get("cpu_model"),
            item.get("gpu_model"),
            str(item.get("ram")),
            str(item.get("storage")),
            str(item.get("screen_size_inch")),
        )
        if key not in groups:
            groups[key] = {
                "id": item["id"],
                "name": item["name"],
                "image": item["image"],
                "prices": [item["priceSar"]],
                "urls": {str(item.get("color") or "N/A"): item["url"]},
                "badges": list(item.get("badges") or []),
                "colors": [item.get("color")],
            }
        else:
            g = groups[key]
            g["prices"].append(item["priceSar"])
            color_key = str(item.get("color") or "N/A")
            g["urls"][color_key] = item["url"]
            if item.get("color") not in g["colors"]:
                g["colors"].append(item.get("color"))

    # Build final list with min price and helpful badges
    final_list: List[Dict[str, Any]] = []
    for g in groups.values():
        price_min = min(g["prices"]) if g["prices"] else 0.0
        price_max = max(g["prices"]) if g["prices"] else 0.0
        price_str = f"{price_min} SAR" if price_min == price_max else f"{price_min} - {price_max} SAR"
        colors_label = ", ".join([c for c in g["colors"] if c]) or "N/A"

        # Clean up badges and avoid duplicates
        existing_badges = [b for b in (g["badges"] or []) if not b.startswith(("Price:", "Colors:"))]
        additional_badges = []
        if price_min != price_max:
            additional_badges.append(f"Price: {price_str}")
        if len(g["colors"]) > 1 and colors_label != "N/A":
            additional_badges.append(f"Colors: {colors_label}")
        
        final_list.append({
            "id": g["id"],
            "name": g["name"],
            "image": g["image"],
            "priceSar": price_min,
            "url": next(iter(g["urls"].values())),
            "badges": existing_badges + additional_badges,
        })

    return final_list


# simplified version of the consolidate_products tool
# it is used to get the product recommendations for the user faster

# class for the get_product_recommendations tool. allows product_type to be passed as argument
class GetProductRecommendationsArgs(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    # Accept multiple alias spellings from LLM/tooling
    product_type: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("product_type", "producttype", "productType"),
    )

    # Ignore extraneous arguments like 'products' instead of erroring
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

@tool(args_schema=GetProductRecommendationsArgs)
def get_product_recommendations(
    brand: Optional[str] = None,
    model: Optional[str] = None,
    ram: Optional[str] = None,
    storage: Optional[str] = None,
    product_type: Optional[str] = None,
) -> str:
    """
    Use this single tool to find, consolidate, and display product recommendations for the user.
    Provide any known specifications like brand, model, RAM, storage, and product type.
    Product types: laptop, gaming, tablet, twoin1, desktop, AIO
    """
    specs = {}
    if brand:
        specs["brand"] = brand
    if model:
        specs["model"] = model
    if ram:
        specs["ram"] = ram
    if storage:
        specs["storage"] = storage

    
    # Step 1: Determine which search tool to use based on product type or brand
    search_function = check_laptops  # default
    
    if product_type:
        product_type = product_type.lower()
        if product_type in ["gaming", "gaming_laptop"]:
            search_function = check_gaming_laptops
        elif product_type in ["tablet"]:
            search_function = check_tablets
        elif product_type in ["twoin1", "twoin1_laptop", "2in1"]:
            search_function = check_twoin1
        elif product_type in ["desktop", "desktops"]:
            search_function = check_desktops
        elif product_type in ["aio"]:
            search_function = check_AIO
        # else defaults to check_laptops
    # elif brand and brand.lower() == "apple":
    #     # Apple products are typically in the regular laptops category
    #     search_function = check_laptops
    
    # Step 2: Call the appropriate search tool internally
    raw_products = search_function(specs)
    
    if not raw_products:
        return "Sorry, I couldn't find any products matching those criteria."

    # Step 3: Call the consolidation tool internally (tool → use invoke with dict)
    consolidated_list = consolidate_products.invoke({"products": raw_products})

    # Step 4: Call the display tool internally to get the final JSON
    product_category = product_type or (f"{brand} laptops" if brand else "laptops")
    heading = f"Here are some recommendations for {product_category}"
    # display tool is also a tool; invoke with structured args
    final_json = display_product_recommendations.invoke({
        "heading": heading,
        "items": consolidated_list,
    })

    return final_json