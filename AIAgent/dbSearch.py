import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Any
import numpy as np

def create_catalog_index(
    csv_path: str,
    spec_columns: List[str],
    embedding_model_name: str = "all-MiniLM-L6-v2"
) -> Dict[str, Any]:
    """
    Loads a CSV, builds spec-text embeddings, and a FAISS index.

    Parameters:
    - csv_path: Path to the CSV file.
    - spec_columns: List of column names to include in embeddings.
    - embedding_model_name: SentenceTransformer model name.

    Returns a dict containing:
    - df: pandas DataFrame with original data and 'spec_text'
    - embed_model: the SentenceTransformer instance
    - embeddings: numpy array of normalized embeddings
    - index: FAISS IndexFlatIP index over embeddings
    - metadata: DataFrame with 'id' and the spec_columns for lookup
    """
    # 1) Load & prepare DataFrame
    df = pd.read_csv(csv_path)
    df = df.reset_index().rename(columns={"index": "id"})
    
    # Ensure spec columns exist
    missing = [c for c in spec_columns if c not in df.columns]
    print(missing)
    if missing:
        raise ValueError(f"Missing expected columns in CSV: {missing}"+df.head().to_string())

    # Build the combined spec_text column
    df["spec_text"] = (
        df[spec_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.replace(r"\s+", " ", regex=True)
    )

    # 2) Compute embeddings
    embed_model = SentenceTransformer(embedding_model_name)
    embeddings = embed_model.encode(
        df["spec_text"].tolist(),
        convert_to_numpy=True,
        show_progress_bar=True
    )
    # Normalize for cosine-similarity
    faiss.normalize_L2(embeddings)

    # 3) Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # 4) Prepare metadata mapping
    metadata = df[["id"] + spec_columns].copy()

    return {
        "df": df,
        "embed_model": embed_model,
        "embeddings": embeddings,
        "index": index,
        "metadata": metadata
    }

def exact_search_catalog(
    specs: Dict[str, str],
    catalog: Dict[str, Any],
    top_k: int = 20,
) -> List[Dict[str, Any]]:
    """
    Multi-level exact CSV search (no embeddings), with exact-match items ranked first.

    Ranking priority
    ----------------
    1. Matches **all** provided keys (full-spec matches) – preserve dataframe order
    2. Matches N-1 keys (“drop-one” matches) – preserve dataframe order
    3. Remaining ties keep their original order in the dataframe

    Returns at most `top_k` items as [{'id': ...}, …]
    """
    df        = catalog["df"].copy()
    id_col    = "id"
    price_col = "price"

    # 1) budget filter
    try:
        df = df[df[price_col] <= float(specs["price"])]
    except (KeyError, ValueError, TypeError):
        pass

    # 2) build filter dict
    search_keys = ["brand", "model", "cpu_model", "ram", "storage", "gpu_model"]
    base = {k: specs[k] for k in search_keys if specs.get(k)}

    def _filter_exact(d: pd.DataFrame, f: Dict[str, str]) -> pd.DataFrame:
        sub = d
        for col, val in f.items():
            sub = sub[sub[col].astype(str).str.lower() == val.lower()]
        return sub

    seen_ids: set[str] = set()
    ordered_ids: list[str] = []

    # 3) full-spec pass  ➜ highest priority
    full_matches = _filter_exact(df, base)
    for _id in full_matches[id_col]:
        if _id not in seen_ids:
            ordered_ids.append(_id)
            seen_ids.add(_id)

    # 4) drop-one passes  ➜ lower priority but still exact on remaining keys
    for drop_key in base:
        filt = {k: v for k, v in base.items() if k != drop_key}
        part_matches = _filter_exact(df, filt)
        for _id in part_matches[id_col]:
            if _id not in seen_ids:
                ordered_ids.append(_id)
                seen_ids.add(_id)

    # 5) format & truncate
    return [{"id": _id} for _id in ordered_ids[:top_k]]