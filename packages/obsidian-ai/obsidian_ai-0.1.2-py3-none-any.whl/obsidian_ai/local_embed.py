from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

import numpy as np


@dataclass
class LocalVectorizer:
    dim: int = 512
    ngram_min: int = 3
    ngram_max: int = 5

    def _hash(self, s: str) -> int:
        # Simple 64-bit FNV-1a hashing
        h = 1469598103934665603
        for ch in s:
            h ^= ord(ch)
            h *= 1099511628211
            h &= (1 << 64) - 1
        return int(h % self.dim)

    def indices(self, text: str) -> list[int]:
        t = text.lower()
        L = len(t)
        idxs: list[int] = []
        for n in range(self.ngram_min, self.ngram_max + 1):
            if L < n:
                continue
            for i in range(L - n + 1):
                gram = t[i : i + n]
                idxs.append(self._hash(gram))
        return idxs

    def tf(self, idxs: Iterable[int]) -> np.ndarray:
        v = np.zeros(self.dim, dtype=np.float32)
        for i in idxs:
            v[i] += 1.0
        return v

    def fit_idf(self, chunks_indices: list[list[int]]) -> np.ndarray:
        df = np.zeros(self.dim, dtype=np.float32)
        for idxs in chunks_indices:
            seen = set(idxs)
            for i in seen:
                df[i] += 1.0
        N = float(max(1, len(chunks_indices)))
        idf = np.log((N + 1.0) / (df + 1.0)) + 1.0
        return idf.astype(np.float32)  # type: ignore[no-any-return]

    def tfidf_norm(self, idxs: list[int], idf: np.ndarray) -> np.ndarray:
        v = self.tf(idxs)
        v *= idf
        n = np.linalg.norm(v)
        return v / n if n else v
