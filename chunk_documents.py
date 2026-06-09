"""
chunk_documents.py
------------------
Milestone 3 — Document ingestion, cleaning, and chunking.

Two chunking strategies, chosen by source type:

  FORUM FILES (Quora, Reddit, CLN, networklessons)
  -------------------------------------------------
  The natural unit is a single comment or answer — one person's opinion
  in response to the thread question.  Splitting across comment boundaries
  destroys that context.  Strategy:
    1. Segment the file into individual comments using source-specific
       delimiter patterns.
    2. Clean each comment (strip author metadata, boilerplate).
    3. If the comment body fits within CHUNK_SIZE, keep it as one chunk.
    4. If it's longer, apply recursive character splitting (same logic as
       below) so the context stays within one comment.

  PDF STUDY GUIDE (ccna_studyguide.pdf)
  --------------------------------------
  Dense reference material structured by section/paragraph — not opinions.
  Recursive character splitting on paragraph breaks (\n\n) works well.
  Needs heavier cleaning: page headers repeat every page, form-feed (\x0c)
  characters mark page boundaries, and the copyright footer appears ~30 times.

Chunk size : 500 characters
Overlap    : 50  characters  (applied only when a comment/paragraph is split)
"""

import os
import re
import json
from pathlib import Path
from pdfminer.high_level import extract_text as pdf_extract_text

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).resolve().parent
DOCS_DIR   = Path(os.environ.get("DOCS_DIR", BASE_DIR / "documents"))
if not DOCS_DIR.exists():
    fallback_docs_dir = Path("/mnt/user-data/uploads")
    if fallback_docs_dir.exists():
        DOCS_DIR = fallback_docs_dir

OUTPUT     = Path(os.environ.get("OUTPUT_PATH", BASE_DIR / "chunks.json"))
CHUNK_SIZE = 500
OVERLAP    = 50

# Map filename → source type
FORUM_FILES = [
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
]
PDF_FILES = ["ccna_studyguide.pdf"]


# ── Shared utilities ──────────────────────────────────────────────────────────

def normalise_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def collapse_blank_lines(text: str, max_blank: int = 2) -> str:
    pattern = r"\n{" + str(max_blank + 1) + r",}"
    return re.sub(pattern, "\n\n", text)


# ── Recursive character splitter ──────────────────────────────────────────────

_SEPARATORS = ["\n\n", "\n", " ", ""]


def _split_on_sep(text: str, sep: str, size: int) -> list:
    parts   = text.split(sep) if sep else list(text)
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


def recursive_split(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP,
                    seps: list = None) -> list:
    if seps is None:
        seps = _SEPARATORS
    sep, rest = seps[0], seps[1:]

    raw = _split_on_sep(text, sep, size)
    final = []
    for chunk in raw:
        if len(chunk) > size and rest:
            final.extend(recursive_split(chunk, size, overlap, rest))
        else:
            final.append(chunk)

    if overlap == 0 or len(final) <= 1:
        return final

    overlapped = [final[0]]
    for i in range(1, len(final)):
        tail      = final[i - 1][-overlap:]
        space_pos = tail.find(" ")
        if space_pos != -1:
            tail = tail[space_pos + 1:]
        if tail and not final[i].startswith(tail):
            combined = (tail + " " + final[i]).strip()
        else:
            combined = final[i]
        overlapped.append(combined)
    return overlapped


# ── PDF pipeline ──────────────────────────────────────────────────────────────

# Patterns that repeat on (almost) every PDF page — not knowledge content
_PDF_BOILERPLATE = re.compile(
    r"CCNA Study Guide v[\d.]+ \u2013 Aaron Balchunas[ \t]*\n"  # page header
    r"|All original material copyright.*?Updated material may be found at http://www\.routeralley\.com\.\s*"
    r"|_{10,}\s*"                     # long underline separators
    r"|\* \* \*\s*",                  # section dividers
    re.DOTALL,
)

_PDF_PAGE_NUM = re.compile(r"^\s*\d{1,3}\s*$", re.MULTILINE)  # bare page numbers


def clean_pdf(raw: str) -> str:
    text = raw.replace("\x0c", "\n\n")   # form-feed → paragraph break
    text = _PDF_BOILERPLATE.sub("", text)
    text = _PDF_PAGE_NUM.sub("", text)
    text = collapse_blank_lines(text, max_blank=2)
    # Strip trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def chunk_pdf(path: Path) -> list:
    raw    = pdf_extract_text(str(path))
    text   = clean_pdf(raw)
    chunks = recursive_split(text, CHUNK_SIZE, OVERLAP)
    return raw, text, chunks


# ── Forum pipeline ────────────────────────────────────────────────────────────

# ---- Comment segmenters (one per source family) ----

def segment_quora(text: str) -> list:
    """
    Quora pages: each answer starts with 'Profile photo for <Name>'.
    Split on that boundary; drop the metadata header lines, keep body.
    """
    # Split on the profile photo marker
    parts = re.split(r"Profile photo for [^\n]+\n", text)
    comments = []
    for part in parts:
        # Strip author line, Follow, time ago, "Originally Answered:" lines
        body = re.sub(
            r"^[^\n]+\n"              # author name
            r"(?: · \nFollow\n)?"     # · Follow
            r"[^\n]*\n"               # bio / time line
            r"(?:Originally Answered:[^\n]*\n)?",  # optional re-answer note
            "", part.strip(), count=1, flags=re.MULTILINE
        )
        # Drop trailing view/upvote lines
        body = re.sub(r"\n\d[\d.,K]*\s*views?\s*\nView \d.*$", "", body, flags=re.DOTALL)
        body = re.sub(r"\n\d[\d.,K]*\s*views?\s*$", "", body, flags=re.DOTALL)
        body = body.strip()
        if len(body) > 80:  # skip fragments shorter than a sentence
            comments.append(body)
    return comments


def segment_reddit(text: str) -> list:
    """
    Reddit pages: the OP post comes first (before 'Comments Section'),
    then individual comments follow.  Each comment starts with a username
    line, a bullet '•', and a time-ago line.
    """
    # Split OP post from comments
    parts = re.split(r"\nComments Section\n", text, maxsplit=1)
    segments = []

    # OP post — everything before Comments Section
    if parts[0].strip():
        op = re.sub(r"^Go to \S+\nr/\S+\n.*?\n\S+\n\n", "", parts[0].strip(),
                    count=1, flags=re.DOTALL)
        op = op.strip()
        if len(op) > 80:
            segments.append(op)

    if len(parts) < 2:
        return segments

    # Individual comments — split on the pattern: username \n • \n time-ago
    comment_blocks = re.split(
        r"\n(?:u/\S+ avatar\n)?(\S[^\n]{0,60})\n[•·]\n[^\n]+\n",
        parts[1]
    )
    # The regex captures the username as a group; odd indices are usernames,
    # even indices are comment bodies
    i = 0
    while i < len(comment_blocks):
        block = comment_blocks[i].strip()
        # Skip: very short, pure vote counts, deleted markers
        if (len(block) > 80
                and not re.fullmatch(r"\d+", block)
                and "Comment has been removed" not in block
                and "Comment deleted by user" not in block):
            # Remove trailing vote count lines
            block = re.sub(r"\n\d+\s*$", "", block).strip()
            segments.append(block)
        i += 1

    return segments


def segment_cln(text: str) -> list:
    """
    Cisco Learning Network pages: each reply starts with a username then
    a timestamp line (either a full date or a relative "N days/months ago").
    Pattern: \n<Name>\n\n(Edited )? <timestamp>
    """
    # Both "Edited June 4, 2026 at 9:20 AM" and "2 months ago" formats
    parts = re.split(
        r"\n(?:[A-Za-z][^\n]{1,80})\n\n"
        r"(?:Edited )?(?:"
        r"(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}"
        r"|\d+ (?:days?|months?|years?|hours?|minutes?) ago"
        r")",
        text
    )
    comments = []
    for part in parts:
        body = part.strip()
        if len(body) > 100:
            # Remove trailing social footer / nav lines
            body = re.sub(
                r"\n(?:X|Facebook|Instagram|LinkedIn|YouTube|Podcasts|"
                r"Certifications Center|Help|Welcome|Cisco U\. Store|"
                r"Certification Tracker|Cisco Learning Network Podcast|"
                r"Member Directory|Virtual Events|Blogs|Discussions|Events|"
                r"© Copyright|Privacy Statement|Terms|Cookie Policy|Trademarks|Cisco\.com|Cisco Logo).*$",
                "", body, flags=re.DOTALL
            ).strip()
            if len(body) > 100:
                comments.append(body)
    return comments


def segment_networklessons(text: str) -> list:
    """
    Networklessons forum: split on 'post by <user>' lines, then strip the
    username / display-name / month-year header that follows each boundary.
    Format after split boundary:
        dragonsky2
        Srikanth V
        Aug 2016
        <actual content>
    """
    parts = re.split(r"\npost by \S+ on [^\n]+\n", text)
    segments = []
    for part in parts:
        # Strip up to 3 header lines: username, display name, month+year
        body = re.sub(r"^[^\n]+\n[^\n]+\n\w+ \d{4}\n", "", part.strip(), count=1)
        # Fallback: strip just 2 header lines if 3-line pattern didn't match
        body = re.sub(r"^[^\n]+\n\w+ \d{4}\n", "", body.strip(), count=1)
        body = body.strip()
        if len(body) > 100:
            segments.append(body)
    return segments


# ---- Route to the right segmenter ----

def segment_forum(filename: str, text: str) -> list:
    if filename.startswith("quora"):
        return segment_quora(text)
    if filename.startswith("reddit"):
        return segment_reddit(text)
    if filename.startswith("cln"):
        return segment_cln(text)
    if filename.startswith("networklessons"):
        return segment_networklessons(text)
    # Fallback: treat as generic paragraphs
    return [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80]


# ---- Shared forum text cleaner (runs on each segment) ----

_FORUM_NOISE = re.compile(
    r"^(?:Sort|Follow|View \d.*|[\d.,K]+ (?:views?|upvotes?)|"
    r"\d+ of \d+ answers?|Share|Expand Post|Selected as Best|"
    r"Top Rated Answers|All Answers|Comments Section|"
    r"Go to \S+|r/\S+|\[deleted\]|Comment (?:has been )?(?:removed|deleted.*)|"
    r"!RemindMe.*|CLICK THIS LINK.*|Info\s+Custom.*|"
    r"Continue this thread|· )\s*$",
    re.MULTILINE
)

_HTML_ENTITIES = [
    ("&amp;", "&"), ("&nbsp;", " "), ("&lt;", "<"),
    ("&gt;", ">"),  ("&quot;", '"'), ("&#x27;", "'"),
]


def clean_forum_segment(text: str) -> str:
    for entity, replacement in _HTML_ENTITIES:
        text = text.replace(entity, replacement)
    text = re.sub(r"\\u[0-9a-fA-F]{4}",
                  lambda m: bytes(m.group(), "utf-8").decode("unicode_escape"),
                  text)
    text = _FORUM_NOISE.sub("", text)
    text = re.sub(r"^https?://\S+\s*$", "", text, flags=re.MULTILINE)
    text = collapse_blank_lines(text, max_blank=2)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def chunk_forum(path: Path) -> tuple:
    raw  = path.read_text(encoding="utf-8", errors="replace")
    raw  = normalise_newlines(raw)

    # Light global clean before segmenting
    text = re.sub(r"^(?:Cisco|Learning Network|Menu|Login|Join now|Search Icon)\s*$",
                  "", raw, flags=re.MULTILINE)
    text = collapse_blank_lines(text)
    text = text.strip()

    segments = segment_forum(path.name, text)
    chunks   = []

    for seg in segments:
        cleaned = clean_forum_segment(seg)
        if not cleaned or len(cleaned) < 100:
            continue
        if len(cleaned) <= CHUNK_SIZE:
            chunks.append(cleaned)
        else:
            # Only split if the comment is genuinely long
            sub = recursive_split(cleaned, CHUNK_SIZE, OVERLAP)
            # Drop any overlap tails that ended up too short after splitting
            chunks.extend(c for c in sub if len(c) >= 100)

    return raw, text, chunks


# ── Main pipeline ─────────────────────────────────────────────────────────────

def process_all() -> list:
    all_chunks = []

    print(f"\n  {'File':<35}  {'Raw':>10}  {'Segments/Chunks':>16}  {'Final chunks':>13}")
    print("  " + "─" * 80)

    for filename in FORUM_FILES:
        path = DOCS_DIR / filename
        if not path.exists():
            print(f"  [SKIP] {filename}")
            continue
        raw, _, chunks = chunk_forum(path)
        print(f"  {filename:<35}  {len(raw):>8}c  {'comment-segmented':>16}  {len(chunks):>8} chunks")
        for idx, text in enumerate(chunks):
            all_chunks.append({"source": filename, "chunk_index": idx,
                                "text": text, "char_count": len(text)})

    for filename in PDF_FILES:
        path = DOCS_DIR / filename
        if not path.exists():
            print(f"  [SKIP] {filename}")
            continue
        raw, _, chunks = chunk_pdf(path)
        print(f"  {filename:<35}  {len(raw):>8}c  {'recursive-split':>16}  {len(chunks):>8} chunks")
        for idx, text in enumerate(chunks):
            all_chunks.append({"source": filename, "chunk_index": idx,
                                "text": text, "char_count": len(text)})

    return all_chunks


def print_inspection(chunks: list) -> None:
    """
    Print 5 representative chunks — one per source family — for manual review.
    Each chunk should be readable as a standalone answer to a question.
    """
    families = ["quora-1.txt", "reddit-2.txt", "cln-1.txt",
                "networklessons-1.txt", "ccna_studyguide.pdf"]
    print("\n" + "═" * 70)
    print("  CHUNK INSPECTION — do these make sense on their own?")
    print("═" * 70)
    for source in families:
        hits = [c for c in chunks if c["source"] == source]
        if not hits:
            continue
        # Pick a mid-file chunk that's a good representative size
        mid = hits[len(hits) // 3]
        print(f"\n  ▶ {source}  [chunk {mid['chunk_index']} of {len(hits)}]  ({mid['char_count']} chars)")
        print("  " + "─" * 66)
        preview = mid["text"][:450].replace("\n", "\n  ")
        print("  " + preview + ("…" if len(mid["text"]) > 450 else ""))
    print("\n" + "═" * 70)


if __name__ == "__main__":
    print(f"\nChunk size : {CHUNK_SIZE} chars   Overlap : {OVERLAP} chars (applied only when a comment is split)")
    print("Forum files → comment-segmented first, then chunked only if comment > 500 chars")
    print("PDF         → recursive character split on paragraph breaks\n")

    chunks = process_all()

    if not chunks:
        print("\n  No chunks were produced.")
        print(f"  DOCS_DIR = {DOCS_DIR}")
        print("  Check that the source files are in the expected folder and rerun the script.\n")
        raise SystemExit(1)

    char_counts = [c["char_count"] for c in chunks]
    print("  " + "─" * 80)
    print(f"\n  Total chunks  : {len(chunks)}")
    print(f"  Avg size      : {sum(char_counts) // len(char_counts)} chars")
    print(f"  Min / Max     : {min(char_counts)} / {max(char_counts)} chars")

    # Per-source breakdown
    sources = {}
    for c in chunks:
        sources.setdefault(c["source"], []).append(c["char_count"])
    print(f"\n  {'Source':<35}  {'Chunks':>7}  {'Avg':>6}  {'Min':>5}  {'Max':>5}")
    print("  " + "─" * 60)
    for src, sizes in sources.items():
        print(f"  {src:<35}  {len(sizes):>7}  {sum(sizes)//len(sizes):>6}  {min(sizes):>5}  {max(sizes):>5}")

    print_inspection(chunks)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved → {OUTPUT}\n")
