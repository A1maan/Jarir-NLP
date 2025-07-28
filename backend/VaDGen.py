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
    if missing:
        raise ValueError(f"Missing expected columns in CSV: {missing}")

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




def hybrid_search_catalog(
    specs: Dict[str, str],
    catalog: Dict[str, Any],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    General hybrid search over any catalog dict.

    specs: dict of field→value to match (e.g. {"series":"Predator","cpu_model":"i7-12700H"})
    catalog: {
      "df": DataFrame,
      "embed_model": SentenceTransformer,
      "embeddings": np.ndarray,
      "index": faiss.IndexFlatIP,
      "metadata": DataFrame  # must have "id" plus all possible spec columns
    }
    """
    df          = catalog["df"]
    embed_model = catalog["embed_model"]
    embeddings  = catalog["embeddings"]
    index       = catalog["index"]
    metadata    = catalog["metadata"]
    dim         = embeddings.shape[1]

    # 1) keep only non‐empty specs
    specs = {k: v for k, v in specs.items() if v}

    # 2) pandas filter on exactly those keys
    sub = df
    for col, val in specs.items():
        sub = sub[sub[col].astype(str).str.lower() == val.lower()]

    if not sub.empty:
        candidate_idx, level = sub.index.to_list(), "exact"
    else:
        # 3) relaxed: drop the last key if more than one
        keys = list(specs.keys())
        if len(keys) > 1:
            relaxed = dict(specs)
            relaxed.pop(keys[-1])
            sub2 = df
            for col, val in relaxed.items():
                sub2 = sub2[sub2[col].astype(str).str.lower() == val.lower()]
            if not sub2.empty:
                candidate_idx, level = sub2.index.to_list(), "partial"
            else:
                candidate_idx, level = list(range(len(df))), "vector"
        else:
            candidate_idx, level = list(range(len(df))), "vector"

    # 4) build query vector
    query_text = " ".join(specs.values()) if specs else ""
    q_vec = embed_model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(q_vec)

    # 5) FAISS search
    if level == "vector":
        D, I = index.search(q_vec, top_k)
    else:
        sub_emb = embeddings[np.array(candidate_idx)]
        tmp = faiss.IndexFlatIP(dim)
        tmp.add(sub_emb)
        D, I = tmp.search(q_vec, min(len(candidate_idx), top_k))
        I = [[candidate_idx[i] for i in hits] for hits in I]

    # 6) format results using only the keys you actually queried
    results = []
    for score, idx in zip(D[0], I[0]):
        # lookup by row‐index
        row = metadata.loc[metadata["id"] == int(df.loc[idx, "id"])].iloc[0]
        entry = {
            "id":           int(row["id"]),
            "score":        float(score),
            "matched_level": level,
        }
        # only include the fields you passed in specs
        for k in specs.keys():
            entry[k] = row[k]
        results.append(entry)

    return results




