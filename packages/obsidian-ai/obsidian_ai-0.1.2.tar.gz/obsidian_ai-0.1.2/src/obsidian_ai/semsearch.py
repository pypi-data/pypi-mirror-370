from __future__ import annotations

import json
import time
from dataclasses import dataclass

import numpy as np
from loguru import logger

from .infrastructure.config import config
from .infrastructure.file_system import iter_text_files

# Constants
MAX_FILE_BYTES = 1_000_000  # 1MB file size limit
from .local_embed import LocalVectorizer


def _ensure_cache_dir() -> None:
    config.cache_dir.mkdir(parents=True, exist_ok=True)


def _signature() -> str:
    items = []
    for p in iter_text_files(config.brain_dir, config.ignore_patterns):
        try:
            st = p.stat()
        except Exception:
            continue
        items.append((str(p), int(st.st_mtime_ns), int(st.st_size)))
    items.sort()
    total = 0
    for _, mt, sz in items:
        total ^= (mt & 0xFFFFFFFF) ^ (sz & 0xFFFFFFFF)
    return str(total)


@dataclass
class ChunkRec:
    path: str
    start: int
    preview: str


def _chunk_text(text: str, max_len: int = 1000) -> list[tuple[int, str]]:
    paras = [p.strip() for p in text.splitlines() if p.strip()]
    chunks: list[tuple[int, str]] = []
    buf: list[str] = []
    start = 0
    pos = 0
    for para in paras:
        if sum(len(x) for x in buf) + len(para) + len(buf) > max_len and buf:
            chunk = "\n".join(buf)
            chunks.append((start, chunk))
            buf = []
            start = pos
        buf.append(para)
        pos += len(para) + 1
    if buf:
        chunks.append((start, "\n".join(buf)))
    return chunks or [(0, text[:max_len])]


def build_or_load_index() -> tuple[np.ndarray, np.ndarray, list[ChunkRec]]:
    _ensure_cache_dir()
    index_npz = config.cache_dir / "index_v1.npz"
    meta_json = config.cache_dir / "meta_v1.json"
    sig = _signature()
    if index_npz.exists() and meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text())
            if meta.get("signature") == sig:
                data = np.load(index_npz, allow_pickle=True)
                matrix = data["matrix"]
                idf = data["idf"]
                paths = data["paths"].tolist()
                starts = data["starts"].tolist()
                previews = data["previews"].tolist()
                recs = [ChunkRec(path=p, start=s, preview=pr) for p, s, pr in zip(paths, starts, previews)]
                return matrix, idf, recs
        except Exception:
            logger.warning("Embedding cache invalid; rebuilding")

    vec = LocalVectorizer(dim=512, ngram_min=3, ngram_max=5)
    chunk_indices: list[list[int]] = []
    all_recs: list[ChunkRec] = []
    for p in iter_text_files(config.brain_dir, config.ignore_patterns):
        try:
            if p.stat().st_size > MAX_FILE_BYTES:
                continue
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for start, chunk in _chunk_text(t, max_len=1200):
            idxs = vec.indices(chunk)
            chunk_indices.append(idxs)
            all_recs.append(ChunkRec(path=str(p), start=start, preview=chunk[:240]))

    if not chunk_indices:
        matrix = np.zeros((0, vec.dim), dtype=np.float32)
        idf = np.ones(vec.dim, dtype=np.float32)
        meta_json.write_text(json.dumps({"signature": sig, "built_at": time.time()}))
        np.savez_compressed(index_npz, matrix=matrix, idf=idf, paths=[], starts=[], previews=[])
        return matrix, idf, all_recs

    idf = vec.fit_idf(chunk_indices)
    mtx = np.zeros((len(chunk_indices), vec.dim), dtype=np.float32)
    for i, idxs in enumerate(chunk_indices):
        mtx[i, :] = vec.tfidf_norm(idxs, idf)

    paths = np.array([r.path for r in all_recs], dtype=object)
    starts = np.array([r.start for r in all_recs], dtype=object)
    previews = np.array([r.preview for r in all_recs], dtype=object)
    np.savez_compressed(index_npz, matrix=mtx, idf=idf, paths=paths, starts=starts, previews=previews)
    meta_json.write_text(json.dumps({"signature": sig, "built_at": time.time()}))
    return mtx, idf, all_recs


def semantic_search(query: str, k: int = 10) -> str:
    matrix, idf, recs = build_or_load_index()
    if matrix.shape[0] == 0:
        return json.dumps({"query": query, "results": []})
    vec = LocalVectorizer(dim=matrix.shape[1], ngram_min=3, ngram_max=5)
    qidx = vec.indices(query)
    qvec = vec.tfidf_norm(qidx, idf)
    sims = matrix @ qvec
    topk = max(1, min(int(k or 10), 25))
    order = np.argsort(-sims)[:topk]
    out = []
    for i in order:
        i = int(i)
        out.append(
            {
                "path": recs[i].path,
                "start": int(recs[i].start),
                "score": round(float(sims[i]), 4),
                "preview": recs[i].preview,
            }
        )
    return json.dumps({"query": query, "results": out})


def semantic_tool_spec() -> dict:
    return {
        "type": "function",
        "name": "semantic_search",
        "description": "Semantic search across notes using a local TF-IDF hash embedding (read-only).",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": ["integer", "null"]},
            },
            "required": ["query", "k"],
            "additionalProperties": False,
        },
    }
