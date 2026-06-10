"""
embed_and_store.py
------------------
Milestone 4 — Embedding + Vector Store

Loads chunks produced by chunk_documents.py, embeds them with
all-MiniLM-L6-v2 (sentence-transformers, runs fully locally),
and stores them in ChromaDB Cloud with source metadata for retrieval.

Metadata stored per chunk
-------------------------
  source          filename (e.g. "reddit-1.txt")
  platform        derived platform ("reddit", "quora", "cln",
                  "networklessons", "studyguide")
  doc_type        "forum" or "reference"
  chunk_index     position of this chunk within its source file
  char_count      character length of the chunk text

.env variables required
-----------------------
  CHROMA_API_KEY    from chromadb.com dashboard
  CHROMA_TENANT     from chromadb.com dashboard
  CHROMA_DATABASE   from chromadb.com dashboard
  CHROMA_COLLECTION name for your collection (default: ccna_chunks)
  GROQ_API_KEY      not needed here, used in Milestone 5

Usage
-----
  python embed_and_store.py            # embed all chunks and upload to cloud
  python embed_and_store.py --skip-ingest --query "How long should I study?"
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb

# ── Configuration ─────────────────────────────────────────────────────────────

load_dotenv()

CHUNKS_FILE      = Path("chunks.json")
CHROMA_API_KEY   = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT    = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE  = os.getenv("CHROMA_DATABASE")
COLLECTION_NAME  = os.getenv("CHROMA_COLLECTION", "ccna_chunks")
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K            = 5       # from planning.md
BATCH_SIZE       = 64      # chunks per embedding batch; also used for upsert batches


def _check_env() -> None:
    """Fail fast with a clear message if any required .env values are missing."""
    missing = [k for k, v in {
        "CHROMA_API_KEY":  CHROMA_API_KEY,
        "CHROMA_TENANT":   CHROMA_TENANT,
        "CHROMA_DATABASE": CHROMA_DATABASE,
    }.items() if not v]
    if missing:
        sys.exit(
            f"ERROR: missing environment variables: {', '.join(missing)}\n"
            "Make sure your .env file is in the same directory and contains "
            "CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE."
        )


# ── Platform / doc-type metadata helpers ─────────────────────────────────────

def derive_metadata(source: str) -> dict:
    """
    Turn a filename into structured metadata fields so retrieval results
    can be filtered or displayed with context.

    Examples
    --------
    "reddit-1.txt"          → platform="reddit",         doc_type="forum"
    "quora-2.txt"           → platform="quora",          doc_type="forum"
    "cln-3.txt"             → platform="cln",            doc_type="forum"
    "networklessons-1.txt"  → platform="networklessons",  doc_type="forum"
    "ccna_studyguide.pdf"   → platform="studyguide",     doc_type="reference"
    """
    s = source.lower()
    if s.startswith("reddit"):
        return {"platform": "reddit", "doc_type": "forum"}
    if s.startswith("quora"):
        return {"platform": "quora", "doc_type": "forum"}
    if s.startswith("cln"):
        return {"platform": "cln", "doc_type": "forum"}
    if s.startswith("networklessons"):
        return {"platform": "networklessons", "doc_type": "forum"}
    if s.endswith(".pdf"):
        return {"platform": "studyguide", "doc_type": "reference"}
    return {"platform": "unknown", "doc_type": "unknown"}


# ── Embedding ─────────────────────────────────────────────────────────────────

def load_embedder() -> SentenceTransformer:
    print(f"  Loading embedder : {EMBED_MODEL_NAME}  (runs locally, no API key needed)")
    model = SentenceTransformer(EMBED_MODEL_NAME)
    print(f"  Max sequence len : {model.max_seq_length} tokens")
    return model


def embed_in_batches(model: SentenceTransformer, texts: list) -> list:
    """
    Embed texts in batches and return a flat list of vectors.
    Prints progress so you can see it working across all 2,000+ chunks.
    """
    all_embeddings = []
    total = len(texts)
    start = time.time()

    for i in range(0, total, BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        vecs  = model.encode(batch, show_progress_bar=False).tolist()
        all_embeddings.extend(vecs)
        done    = min(i + BATCH_SIZE, total)
        elapsed = time.time() - start
        print(f"  Embedded {done:>5} / {total}  ({elapsed:.1f}s)", end="\r", flush=True)

    print(f"  Embedded {total} / {total}  ({time.time() - start:.1f}s total)  ✓")
    return all_embeddings


# ── ChromaDB Cloud client ─────────────────────────────────────────────────────

def get_collection(rebuild: bool = False):
    """
    Connect to ChromaDB Cloud and return the collection.

    rebuild=True  → delete and recreate the collection (re-run ingest).
    rebuild=False → connect to the existing collection for queries.
    """
    client = chromadb.CloudClient(
        api_key  = CHROMA_API_KEY,
        tenant   = CHROMA_TENANT,
        database = CHROMA_DATABASE,
    )

    if rebuild:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"  Deleted existing collection '{COLLECTION_NAME}'")
        except Exception:
            pass  # collection didn't exist yet, that's fine

    # cosine similarity is the right distance metric for sentence-transformer
    # embeddings — it measures semantic direction rather than raw magnitude
    collection = client.get_or_create_collection(
        name     = COLLECTION_NAME,
        metadata = {"hnsw:space": "cosine"},
    )
    return collection


# ── Ingestion ─────────────────────────────────────────────────────────────────

def load_chunks() -> list:
    if not CHUNKS_FILE.exists():
        sys.exit(f"ERROR: {CHUNKS_FILE} not found. Run chunk_documents.py first.")
    with open(CHUNKS_FILE, encoding="utf-8") as f:
        return json.load(f)


def ingest(rebuild: bool = True) -> None:
    _check_env()

    print("\n── Loading chunks ───────────────────────────────────────────────────────")
    chunks = load_chunks()
    print(f"  Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    # Embed locally first — all 2,020 chunks become vectors before anything
    # touches the network, so a cloud hiccup doesn't waste embedding time
    print("\n── Embedding (local) ────────────────────────────────────────────────────")
    model      = load_embedder()
    texts      = [c["text"] for c in chunks]
    embeddings = embed_in_batches(model, texts)

    # Build parallel lists: ids, metadatas, texts, embeddings
    ids       = []
    metadatas = []
    for chunk in chunks:
        ids.append(f"{chunk['source']}_chunk_{chunk['chunk_index']}")
        meta = {
            "source":      chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "char_count":  chunk["char_count"],
        }
        meta.update(derive_metadata(chunk["source"]))
        metadatas.append(meta)

    # Upload to ChromaDB Cloud in batches
    print(f"\n── Uploading to ChromaDB Cloud ───────────────────────────────────────────")
    print(f"  Tenant     : {CHROMA_TENANT}")
    print(f"  Database   : {CHROMA_DATABASE}")
    print(f"  Collection : {COLLECTION_NAME}")

    collection = get_collection(rebuild=rebuild)

    for i in range(0, len(chunks), BATCH_SIZE):
        collection.upsert(
            ids        = ids[i : i + BATCH_SIZE],
            embeddings = embeddings[i : i + BATCH_SIZE],
            documents  = texts[i : i + BATCH_SIZE],
            metadatas  = metadatas[i : i + BATCH_SIZE],
        )
        done = min(i + BATCH_SIZE, len(chunks))
        print(f"  Uploaded {done:>5} / {len(chunks)}", end="\r", flush=True)

    print(f"  Uploaded {len(chunks)} / {len(chunks)}  ✓")
    print(f"\n  Collection count: {collection.count()} documents")


# ── Retrieval ─────────────────────────────────────────────────────────────────

def retrieve(query: str, k: int = TOP_K, doc_type: str = None) -> list:
    """
    Embed the query locally (same model used at ingest), then ask ChromaDB
    Cloud for the top-k most similar chunks by cosine similarity.

    Parameters
    ----------
    query    : natural language question from the user
    k        : number of chunks to return (default: TOP_K = 5 from planning.md)
    doc_type : optional filter — "forum", "reference", or None for all sources

    Returns
    -------
    List of dicts, each containing:
        text        the chunk text to pass to the LLM
        source      original filename
        platform    reddit / quora / cln / networklessons / studyguide
        doc_type    "forum" or "reference"
        chunk_index position of chunk within its source file
        distance    cosine distance (0 = identical, 1 = unrelated)
    """
    _check_env()

    model     = SentenceTransformer(EMBED_MODEL_NAME)
    query_vec = model.encode([query]).tolist()

    collection   = get_collection(rebuild=False)
    where_filter = {"doc_type": doc_type} if doc_type else None

    results = collection.query(
        query_embeddings = query_vec,
        n_results        = k,
        where            = where_filter,
        include          = ["documents", "metadatas", "distances"],
    )

    return [
        {
            "text":        text,
            "source":      meta["source"],
            "platform":    meta["platform"],
            "doc_type":    meta["doc_type"],
            "chunk_index": meta["chunk_index"],
            "distance":    round(dist, 4),
        }
        for text, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


# ── CLI helpers ───────────────────────────────────────────────────────────────

def print_results(results: list, query: str) -> None:
    print(f"\n  Query  : \"{query}\"")
    print(f"  Top-{len(results)} results (cosine distance — lower = more relevant)\n")
    for i, r in enumerate(results, 1):
        print(f"  {'─' * 66}")
        print(f"  [{i}] {r['source']}  chunk {r['chunk_index']}  "
              f"({r['platform']} / {r['doc_type']})  dist={r['distance']}")
        print(f"  {'─' * 66}")
        preview = r["text"][:400].replace("\n", " ")
        print(f"  {preview}{'…' if len(r['text']) > 400 else ''}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed chunks and store/query ChromaDB Cloud")
    parser.add_argument("--query", "-q", type=str, default=None,
                        help="Search the collection with a natural language query")
    parser.add_argument("--k", type=int, default=TOP_K,
                        help=f"Number of results to return (default: {TOP_K})")
    parser.add_argument("--skip-ingest", action="store_true",
                        help="Skip embedding/upload and go straight to a query")
    parser.add_argument("--filter", type=str, choices=["forum", "reference"], default=None,
                        help="Restrict results to one doc_type")
    args = parser.parse_args()

    if not args.skip_ingest:
        ingest(rebuild=True)

    if args.query:
        results = retrieve(args.query, k=args.k, doc_type=args.filter)
        print_results(results, args.query)
    elif args.skip_ingest:
        print("\nProvide --query to search. Example:")
        print('  python embed_and_store.py --skip-ingest --query "How long to study for CCNA?"')
    else:
        print("\nIngest complete. To query without re-uploading:")
        print('  python embed_and_store.py --skip-ingest --query "How long to study for CCNA?"')
