"""
chunk_documents.py
------------------
Loads all source documents (forum .txt files + PDF study guide),
cleans them, and splits them into overlapping chunks matching the
spec in planning.md:

    chunk_size = 500 characters
    overlap    = 50  characters

Uses a recursive character splitter that tries to break on paragraph
boundaries first (\n\n), then single newlines, then spaces, then
individual characters — so chunks stay semantically coherent.

Output
------
- Prints a summary table to stdout
- Saves all chunks to chunks.json  (list of dicts with keys:
      source, chunk_index, text, char_count)
"""

import os
import re
import json
from pathlib import Path
from pdfminer.high_level import extract_text as pdf_extract_text

# ── Configuration ─────────────────────────────────────────────────────────────

DOCS_DIR   = Path("/mnt/user-data/uploads")
OUTPUT     = Path("/mnt/user-data/outputs/chunks.json")
CHUNK_SIZE = 500   # characters
OVERLAP    = 50    # characters

SOURCE_FILES = [
    "cln-1.txt",
    "cln-2.txt",
    "cln-3.txt",
    "networklessons-1.txt",
    "quora-1.txt",
    "quora-2.txt",
    "quora-3.txt",
    "reddit-1.txt",
    "reddit-2.txt",
    "reddit-3.txt",
    "reddit-4.txt",
    "ccna_studyguide.pdf",
]


# ── Text loading ──────────────────────────────────────────────────────────────

def load_txt(path: Path) -> str:
    """Read a plain-text / forum file."""
    return path.read_text(encoding="utf-8", errors="replace")


def load_pdf(path: Path) -> str:
    """Extract text from a PDF using pdfminer."""
    return pdf_extract_text(str(path))


def load_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return load_pdf(path)
    return load_txt(path)


# ── Cleaning ──────────────────────────────────────────────────────────────────

# Navigation / boilerplate patterns common in scraped forum pages
_BOILERPLATE = re.compile(
    r"""
    (                               # any of:
      ^Cisco\s*\n                   #   site header
    | ^Learning\s+Network\s*\n
    | ^Menu\s*\n
    | ^Login\s*\n
    | ^Join\s+now\s*\n
    | ^Search\s+Icon\s*\n
    | ^Share\s*\n
    | ^Expand\s+Post\s*\n
    | ^Selected\s+as\s+Best\s*\n
    | ^Top\s+Rated\s+Answers\s*\n
    | ^All\s+Answers\s*\n
    | ^Trending\s+Articles.*\n
    | ^Stay\s+Connected.*\n
    | ^(?:©|\(c\))\s+Copyright.*\n
    | ^Cisco\s+Logo.*\n
    | ^Privacy\s+Statement.*\n
    | ^Terms\s+&\s+Conditions.*\n
    | ^Cookie\s+Policy.*\n
    | ^Trademarks.*\n
    | ^Cisco\.com.*\n
    | ^\d+\s*\n                     #   bare vote/view counts
    | ^u\/\S+\s+avatar\s*\n         #   Reddit avatar lines
    | ^\[deleted\]\s*\n
    | ^Comment\s+(has\s+been\s+)?deleted.*\n
    | ^!RemindMe.*\n
    | ^CLICK\s+THIS\s+LINK.*\n
    | ^Info\s+Custom\s+Your\s+Reminders.*\n
    | ^Continue\s+this\s+thread\s*\n
    | ^Comments\s+Section\s*\n
    )
    """,
    re.VERBOSE | re.MULTILINE,
)


def clean_text(raw: str) -> str:
    """Normalise line endings, strip boilerplate, collapse whitespace."""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")

    # Remove boilerplate lines
    text = _BOILERPLATE.sub("", text)

    # Remove bare URL-only lines
    text = re.sub(r"^https?://\S+\s*$", "", text, flags=re.MULTILINE)

    # Collapse 3+ consecutive blank lines → 2 (preserve paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)

    return text.strip()


# ── Recursive character splitter ──────────────────────────────────────────────

SEPARATORS = ["\n\n", "\n", " ", ""]   # priority order


def _split_on_separator(text, sep, size):
    """Split text on sep; keep pieces <= size. Returns list of strings."""
    parts = text.split(sep) if sep else list(text)
    chunks  = []
    current = ""

    for part in parts:
        joiner    = sep if current else ""
        candidate = current + joiner + part
        if len(candidate) <= size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = part

    if current:
        chunks.append(current)

    return [c for c in chunks if c.strip()]


def recursive_split(text, size=CHUNK_SIZE, overlap=OVERLAP, separators=None):
    """
    Recursively split text using a priority list of separators.
    After splitting, stitch in an overlap prefix between consecutive chunks.
    """
    if separators is None:
        separators = SEPARATORS

    sep  = separators[0]
    rest = separators[1:]

    raw_chunks = _split_on_separator(text, sep, size)

    # Recurse on any chunk that is still too long
    final = []
    for chunk in raw_chunks:
        if len(chunk) > size and rest:
            final.extend(recursive_split(chunk, size, overlap, rest))
        else:
            final.append(chunk)

    if overlap == 0 or len(final) <= 1:
        return final

    # Apply overlap: prepend the tail of the previous chunk
    overlapped = [final[0]]
    for i in range(1, len(final)):
        tail = final[i - 1][-overlap:]
        # Snap to a word boundary so we don't start mid-word
        space_pos = tail.find(" ")
        if space_pos != -1:
            tail = tail[space_pos + 1:]
        # Only prepend tail if the next chunk doesn't already open with it
        if tail and not final[i].startswith(tail):
            combined = (tail + " " + final[i]).strip()
        else:
            combined = final[i]
        overlapped.append(combined)

    return overlapped


# ── Main pipeline ─────────────────────────────────────────────────────────────

def process_documents():
    all_chunks = []

    for filename in SOURCE_FILES:
        path = DOCS_DIR / filename
        if not path.exists():
            print(f"  [SKIP] {filename} — not found")
            continue

        raw    = load_document(path)
        text   = clean_text(raw)
        chunks = recursive_split(text, CHUNK_SIZE, OVERLAP)

        print(f"  {filename:<35}  {len(raw):>8} raw chars  →  {len(text):>8} cleaned  →  {len(chunks):>4} chunks")

        for idx, chunk_text in enumerate(chunks):
            all_chunks.append({
                "source":      filename,
                "chunk_index": idx,
                "text":        chunk_text,
                "char_count":  len(chunk_text),
            })

    return all_chunks


def print_sample(chunks, n=3):
    print(f"\n── Sample chunks (first {n} from cln-1.txt) ────────────────────────────")
    shown = 0
    for c in chunks:
        if c["source"] == "cln-1.txt" and shown < n:
            preview = c["text"][:280].replace("\n", " ")
            ellipsis = "…" if len(c["text"]) > 280 else ""
            print(f"\n  [chunk {c['chunk_index']}]  ({c['char_count']} chars)")
            print(f"  {preview}{ellipsis}")
            shown += 1


if __name__ == "__main__":
    print(f"\nChunk size : {CHUNK_SIZE} chars   Overlap : {OVERLAP} chars\n")
    print(f"  {'File':<35}  {'Raw':>12}  {'Cleaned':>10}  {'Chunks':>7}")
    print("  " + "─" * 72)

    chunks = process_documents()

    char_counts = [c["char_count"] for c in chunks]
    print("  " + "─" * 72)
    print(f"\n  Total chunks  : {len(chunks)}")
    print(f"  Avg size      : {sum(char_counts) // len(char_counts)} chars")
    print(f"  Min / Max     : {min(char_counts)} / {max(char_counts)} chars")

    print_sample(chunks)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\n  Saved → {OUTPUT}\n")
