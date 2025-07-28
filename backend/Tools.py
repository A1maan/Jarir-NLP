from VaDGen import hybrid_search_catalog
from VaDGen import create_catalog_index
from typing import TypedDict, List, Dict, Any, Optional
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
import json
from pathlib import Path


llm = init_chat_model("google_genai:gemini-2.5-flash")


# Define the catalog index for laptops
LAPTOP_CSV_PATH = Path(__file__).parent.parent / "Jarir-scraper" / "jarir_gaming_pcs.csv"
LAPTOP_SPEC_COLUMNS = ["brand", "model", "cpu_model", "gpu_model", "ram", "storage"]  
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
laptop_catalog = create_catalog_index(LAPTOP_CSV_PATH, LAPTOP_SPEC_COLUMNS, EMBEDDING_MODEL)

# Define the catalog index for laptops




def check_gaming_laptops(specs: Dict[str, str]) -> str:
    """
    specs: e.g.
      {"brand":"Acer",
       "model":"Predator",
       "cpu_model":"i7-12700H",
       "gpu_model":"RTX3070",
       "ram":"16GB",
       "storage":"512GB"}
    """
    # 1) get the top 5 candidates via our hybrid search
    candidates = hybrid_search_catalog(specs, laptop_catalog, top_k=5)
    if not candidates:
        return "No similar products  found."

    # grab the DataFrame out of the catalog
    df = laptop_catalog["df"]

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
    res = llm.invoke([
        SystemMessage(content="You are an expert at matching products to user specs."),
        HumanMessage(content=prompt)
    ])
    llm_output = res.content  # e.g. JSON string of id+reason
    ranking = json.loads(llm_output)
    return {
      "results": rows,      # full spec dicts
      "ranking": ranking    # id + match_level + reason
    }