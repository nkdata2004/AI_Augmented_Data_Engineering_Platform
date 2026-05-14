"""Column similarity functions using edit distance, BGE embeddings, and heuristics."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache

COMMON_ABBREVIATIONS = {
    "id": "identifier",
    "cust": "customer",
    "num": "number",
    "no": "number",
    "qty": "quantity",
    "amt": "amount",
    "addr": "address",
    "dob": "date of birth",
    "dt": "date",
    "ts": "timestamp",
    "val": "value",
}

DOMAIN_SYNONYMS = {
    "customer": {"client", "account", "buyer"},
    "identifier": {"id", "key", "number", "code"},
    "name": {"full name", "customer name", "client name"},
    "email": {"email address", "mail"},
    "value": {"amount", "spend", "revenue", "total", "lifetime value"},
    "date": {"day", "timestamp"},
    "status": {"state", "account status"},
}


@dataclass(frozen=True)
class SimilarityBreakdown:
    levenshtein: float
    embedding: float
    heuristic: float
    confidence: float


def split_identifier(text: str) -> list[str]:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(text))
    text = re.sub(r"[^A-Za-z0-9]+", " ", text)
    return [p.lower() for p in text.split() if p]


def normalize_column(text: str) -> str:
    tokens = split_identifier(text)
    expanded: list[str] = []

    for token in tokens:
        expanded.extend(COMMON_ABBREVIATIONS.get(token, token).split())

    return " ".join(expanded)


def semantic_text_for_embedding(text: str) -> str:
    """Prepare richer text for BGE.

    Column names are short, so we expand abbreviations and add domain synonyms
    to give the embedding model more semantic context.
    """
    normalized = normalize_column(text)
    tokens = normalized.split()
    enriched = list(tokens)

    for token in tokens:
        for root, synonyms in DOMAIN_SYNONYMS.items():
            if token == root or token in synonyms:
                enriched.append(root)
                enriched.extend(synonyms)

    return " ".join(dict.fromkeys(enriched))


def levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    prev = list(range(len(b) + 1))

    for i, ca in enumerate(a, start=1):
        cur = [i]

        for j, cb in enumerate(b, start=1):
            insert_cost = prev[j] + 1
            delete_cost = cur[j - 1] + 1
            replace_cost = prev[j - 1] + (ca != cb)
            cur.append(min(insert_cost, delete_cost, replace_cost))

        prev = cur

    return prev[-1]


def levenshtein_similarity(a: str, b: str) -> float:
    a_norm = normalize_column(a).replace(" ", "")
    b_norm = normalize_column(b).replace(" ", "")
    max_len = max(len(a_norm), len(b_norm), 1)

    return 1.0 - (levenshtein_distance(a_norm, b_norm) / max_len)


@lru_cache(maxsize=1)
def load_bge_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("BAAI/bge-small-en-v1.5")


def embedding_similarity(a: str, b: str) -> float:
    model = load_bge_model()

    texts = [
        semantic_text_for_embedding(a),
        semantic_text_for_embedding(b),
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    score = float(embeddings[0] @ embeddings[1])

    return max(0.0, min(1.0, score))


def heuristic_similarity(a: str, b: str) -> float:
    a_tokens = set(normalize_column(a).split())
    b_tokens = set(normalize_column(b).split())

    if not a_tokens or not b_tokens:
        return 0.0

    jaccard = len(a_tokens & b_tokens) / len(a_tokens | b_tokens)
    exact_bonus = 0.15 if normalize_column(a) == normalize_column(b) else 0.0
    identifier_bonus = 0.10 if "identifier" in a_tokens and "identifier" in b_tokens else 0.0

    semantic_bonus = 0.0

    for root, synonyms in DOMAIN_SYNONYMS.items():
        left = root in a_tokens or bool(a_tokens & synonyms)
        right = root in b_tokens or bool(b_tokens & synonyms)

        if left and right:
            semantic_bonus += 0.05

    return min(1.0, jaccard + exact_bonus + identifier_bonus + semantic_bonus)


def combined_similarity(a: str, b: str) -> SimilarityBreakdown:
    lev = levenshtein_similarity(a, b)
    emb = embedding_similarity(a, b)
    heu = heuristic_similarity(a, b)

    confidence = min(
        1.0,
        (0.15 * lev) + (0.70 * emb) + (0.15 * heu),
    )

    return SimilarityBreakdown(
        levenshtein=round(lev, 4),
        embedding=round(emb, 4),
        heuristic=round(heu, 4),
        confidence=round(confidence, 4),
    )