from VaDGen import hybrid_search_catalog
from VaDGen import create_catalog_index
from typing import Set, TypedDict, List, Dict, Any, Optional
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
import json
import pandas as pd


llm = init_chat_model("google_genai:gemini-2.5-flash")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# Define the catalog index for  gaming laptops
GAMING_CSV_PATH = "../Jarir-scraper/jarir_gaming_pcs.csv"
GAMING_SPEC_COLUMNS = ["brand", "model", "cpu_model", "gpu_model", "ram", "storage"]  
gaming_laptop_catalog = create_catalog_index(GAMING_CSV_PATH, GAMING_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_gaming_laptops(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
    specs: e.g.
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"i7-12700H",
       "gpu_model":"RTX3070",
       "ram":"16GB",
       "storage":"512GB"}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, gaming_laptop_catalog, top_k=10)
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
LAPTOP_SPEC_COLUMNS = ["brand", "model", "cpu_model", "gpu_model", "ram", "storage", "renewed"]  
LAPTOP_catalog = create_catalog_index(LAPTOP_CSV_PATH, LAPTOP_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_laptops(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"Intel Core Ultra 7",
       "gpu_model":"Qualcomm Adreno GPU",
       "ram":"16GB",
       "storage":"512GB",
       "renewed"":"renewed or new"}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, LAPTOP_catalog, top_k=10)
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
TABLET_SPEC_COLUMNS = ["brand", "model", "cpu_clock","ram", "storage","color", "renewed"]  
TABLET_catalog = create_catalog_index(TABLET_CSV_PATH, TABLET_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_tablets(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_clock":"1.8 GHz",
       "ram":"16GB",
       "storage":"512GB",
       "color":"Black"
       "renewed":"renewed or new"}

    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, TABLET_catalog, top_k=10)
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
twoin1_SPEC_COLUMNS = ["brand", "model", "cpu_model","gpu_model","ram", "storage"]  
twoin1_catalog = create_catalog_index(twoin1_CSV_PATH, twoin1_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_twoin1(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"",
       "ram":"16GB",
       "storage":"512GB",
       "gpu_model":""}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, twoin1_catalog, top_k=10)
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
DESKTOPS_SPEC_COLUMNS = ["brand", "model", "cpu_model","gpu_model","ram", "storage"]  
DESKTOPS_catalog = create_catalog_index(DESKTOPS_CSV_PATH, DESKTOPS_SPEC_COLUMNS, EMBEDDING_MODEL)





def check_desktops(specs: Dict[str, str]):
    """
    Give the specs as a dictionary with the following keys:
   - a Python dict, e.g:
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"",
       "ram":"16GB",
       "storage":"512GB",
       "gpu_model":""}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, DESKTOPS_catalog, top_k=10)
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
    
    



#---------------------------------------------------------
# Get available models for the required brand

csv_paths = [GAMING_CSV_PATH, LAPTOP_CSV_PATH, TABLET_CSV_PATH , twoin1_CSV_PATH , DESKTOPS_CSV_PATH]

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
      ['gaming', 'laptop', 'tablet', 'twoin1_laptop', 'desktops']
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
    These are the available product_type ['gaming', 'laptop', 'tablet', 'twoin1_laptop', 'desktops']
    Given a product type, returns a dict mapping each brand
    to the list of models available under that product_type.
    """
    return product_type_map.get(product_type, {})