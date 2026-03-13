"""
rsvp.metrics
============
Approximations of the three RSVP field quantities over text patches.

Mathematical grounding
----------------------
Each patch p_i carries:

    Φ_i  — scalar density   = mean token information content
    v_i  — vector flow      = embedding of the patch
    S_i  — entropy          = Shannon entropy over token frequencies

Scalar density:
    Φ_i = (1/|p_i|) Σ_{w∈p_i} I(w),   I(w) = -log P(w)
    Approximated here by inverse document frequency weighting.

Vector flow displacement:
    |v_i| = ‖E(p_{i+1}) − E(p_i)‖
    Approximated by cosine distance between TF-IDF vectors.

Entropy:
    S_i = −Σ_{w∈V} p(w) log p(w)
    Standard Shannon entropy over unigram token distribution in patch.

Curvature:
    κ_i = ‖v_i − v_{i−1}‖
    Rate of change of the directional field.
"""

from __future__ import annotations
import math
import re
from collections import Counter
from typing import List, Optional

WORD = re.compile(r"\w+")

# Approximate IDF from common English frequencies.
# Real deployments should load a corpus IDF table.
_COMMON_TOKENS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "may",
    "might", "shall", "can", "not", "it", "he", "she", "they", "we", "i",
    "you", "this", "that", "these", "those", "from", "by", "as", "so",
    "if", "then", "than", "into", "out", "up", "down", "about", "what",
    "which", "who", "how", "when", "where", "there", "here", "all", "no",
    "just", "my", "your", "his", "her", "our", "their", "its", "me", "him",
}


def _tokenize(text: str) -> List[str]:
    return WORD.findall(text.lower())


def entropy(text: str) -> float:
    """
    Shannon entropy of unigram token distribution within text.
    Returns 0.0 for empty or single-token input.

    S = −Σ p(w) log₂ p(w)
    """
    tokens = _tokenize(text)
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    total = sum(counts.values())
    H = 0.0
    for c in counts.values():
        p = c / total
        H -= p * math.log2(p)
    return H


def scalar_density(text: str, corpus_size: int = 1_000_000) -> float:
    """
    Mean information content of tokens in text.
    Rare tokens (not in common-word list) are assigned high I(w).
    Common tokens receive log2(1000) ≈ 10 as a low-information baseline.

    Φ = (1/N) Σ I(w)
    """
    tokens = _tokenize(text)
    if not tokens:
        return 0.0
    total_I = 0.0
    for w in tokens:
        if w in _COMMON_TOKENS:
            total_I += math.log2(1_000)          # low rarity → low Φ
        else:
            total_I += math.log2(corpus_size)    # high rarity → high Φ
    return total_I / len(tokens)


def embed(text: str) -> List[float]:
    """
    Produce a lightweight TF-IDF-style embedding for a text patch.
    Returns a fixed-dimensional vector based on token frequency profiles.

    In production this should be replaced by a proper sentence transformer
    or word embedding model. This stub is deterministic and dependency-free.
    """
    tokens = _tokenize(text)
    if not tokens:
        return [0.0] * 16
    counts = Counter(tokens)
    total = sum(counts.values())
    # Project onto 16 dimensions via deterministic hash bucketing
    vec = [0.0] * 16
    for w, c in counts.items():
        tf = c / total
        idf = 0.5 if w in _COMMON_TOKENS else 5.0
        bucket = hash(w) % 16
        vec[bucket] += tf * idf
    # L2-normalise
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def displacement(v1: List[float], v2: List[float]) -> float:
    """
    Euclidean distance between two embedding vectors.
    Represents |v_i| = ‖E(p_{i+1}) − E(p_i)‖.
    """
    if not v1 or not v2:
        return 0.0
    n = min(len(v1), len(v2))
    return math.sqrt(sum((v1[k] - v2[k]) ** 2 for k in range(n)))


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Cosine similarity between two embedding vectors."""
    if not v1 or not v2:
        return 0.0
    n = min(len(v1), len(v2))
    dot = sum(v1[k] * v2[k] for k in range(n))
    n1 = math.sqrt(sum(x * x for x in v1)) or 1.0
    n2 = math.sqrt(sum(x * x for x in v2)) or 1.0
    return dot / (n1 * n2)


class Metrics:
    """
    Unified interface to RSVP field approximations.
    Pass an instance of this to Document.compute_fields().
    """

    def scalar(self, text: str) -> float:
        return scalar_density(text)

    def entropy(self, text: str) -> float:
        return entropy(text)

    def embed(self, text: str) -> List[float]:
        return embed(text)

    def displacement(self, v1: List[float], v2: List[float]) -> float:
        return displacement(v1, v2)

    def similarity(self, v1: List[float], v2: List[float]) -> float:
        return cosine_similarity(v1, v2)
