"""
app.py
------
Milestone 5 — Generation + Gradio Interface

Wires together:
  retrieve()  from embed_and_store.py  (ChromaDB Cloud, top-k=5)
  Groq API    llama-3.3-70b-versatile  (generation)
  Gradio      web UI at http://localhost:7860

Grounding contract
------------------
The system prompt forbids the LLM from using any knowledge outside the
retrieved chunks.  If the chunks don't contain a clear answer the model
must say so rather than hallucinate.  Source attribution happens in two
layers:

  1. The prompt instructs the model to cite [Source: <filename>] inline.
  2. After generation the retrieved filenames are appended programmatically
     so the source list is always present even if the model forgets a citation.

Source names are the real filenames attached to each chunk by the ingestion
pipeline — no searching or guessing involved.
"""

import os
from dotenv import load_dotenv
from groq import Groq
import gradio as gr

from embed_and_store import retrieve, TOP_K

# ── Configuration ─────────────────────────────────────────────────────────────

load_dotenv()

GROQ_MODEL  = "llama-3.3-70b-versatile"
GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Human-readable labels for the source filenames stored in chunk metadata
SOURCE_LABELS = {
    "cln-1.txt":             "Cisco Learning Network — Step-by-Step Prep Guide",
    "cln-2.txt":             "Cisco Learning Network — Best Study Methods Thread",
    "cln-3.txt":             "Cisco Learning Network — Packet Tracer Discussion",
    "networklessons-1.txt":  "NetworkLessons Forum — Best Way to Prepare",
    "quora-1.txt":           "Quora — Starting CCNA Study Suggestions",
    "quora-2.txt":           "Quora — How to Study and Pass (after failing)",
    "quora-3.txt":           "Quora — How to Prepare and Remember Answers",
    "reddit-1.txt":          "Reddit r/ccna — Most Effective Prep Method",
    "reddit-2.txt":          "Reddit r/ccna — 45-Day Study Experience",
    "reddit-3.txt":          "Reddit r/Cisco — Best Way to Study",
    "reddit-4.txt":          "Reddit r/networking — Free Study Guides",
    "ccna_studyguide.pdf":   "CCNA Study Guide (Aaron Balchunas, routeralley.com)",
}


def label(filename: str) -> str:
    return SOURCE_LABELS.get(filename, filename)


# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a CCNA study advisor. Your job is to help students \
prepare for the Cisco CCNA exam.

STRICT RULES — you must follow all of these without exception:

1. Answer ONLY using the information in the retrieved context passages provided \
to you. Do not use any knowledge from your training data.

2. Every factual claim in your answer must be traceable to one of the provided \
passages. After each claim or sentence that draws from a specific passage, cite \
it inline like this: [Source: <filename>]

3. If the retrieved context does not contain enough information to answer the \
question, respond with exactly:
   "I don't have enough information in my sources to answer that question. \
Try rephrasing or asking about a related CCNA study topic."
   Do not attempt to fill gaps with general knowledge.

4. Do not say things like "based on my knowledge" or "generally speaking". \
Every statement must come from the provided passages.

5. Be concise and practical. Students want actionable advice."""


# ── Generation ────────────────────────────────────────────────────────────────

def build_context_block(chunks: list) -> str:
    """
    Format retrieved chunks into a numbered context block for the prompt.
    Each passage is labelled with its filename so the model can cite it.
    """
    lines = []
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"--- Passage {i} [filename: {chunk['source']}] ---")
        lines.append(chunk["text"])
        lines.append("")
    return "\n".join(lines)


def ask(question: str, k: int = TOP_K) -> dict:
    """
    Full RAG pipeline: retrieve → build prompt → generate → format output.

    Returns
    -------
    dict with keys:
        answer   : LLM response string with inline citations
        sources  : deduplicated list of source label strings
        chunks   : raw retrieved chunk dicts (for debugging)
    """
    # 1. Retrieve top-k chunks from ChromaDB Cloud
    chunks = retrieve(question, k=k)

    # 2. Build the context block the model will read
    context = build_context_block(chunks)

    # 3. User message: context first, then question
    #    Putting context before the question is the standard RAG pattern —
    #    it anchors the model to the sources before it sees what to answer.
    user_message = f"""Here are the retrieved passages from CCNA study sources:

{context}

Question: {question}

Answer the question using ONLY the passages above. Cite sources inline \
using [Source: <filename>] after each claim."""

    # 4. Call Groq
    response = GROQ_CLIENT.chat.completions.create(
        model    = GROQ_MODEL,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature = 0.2,   # low temperature = more faithful to sources
        max_tokens  = 1024,
    )
    answer = response.choices[0].message.content.strip()

    # 5. Programmatic source list — deduplicated, in retrieval order
    #    This guarantees sources are always shown even if the model omits a citation
    seen    = set()
    sources = []
    for chunk in chunks:
        src = chunk["source"]
        if src not in seen:
            seen.add(src)
            sources.append(label(src))

    return {"answer": answer, "sources": sources, "chunks": chunks}


# ── Gradio interface ──────────────────────────────────────────────────────────

def handle_query(question: str):
    """
    Gradio handler — calls ask() and returns the two output strings.
    Returns (answer_text, sources_text) matching the two output components.
    """
    if not question or not question.strip():
        return "Please enter a question.", ""

    try:
        result  = ask(question.strip())
        sources = "\n".join(f"• {s}" for s in result["sources"])
        return result["answer"], sources
    except Exception as e:
        return f"Error: {str(e)}", ""


with gr.Blocks(title="CCNA Study Advisor") as demo:

    gr.Markdown(
        """
        # 📡 CCNA Study Advisor
        Ask anything about preparing for the CCNA exam.
        Answers are grounded in real forum discussions and study guides —
        no hallucination, sources shown for every response.
        """
    )

    with gr.Row():
        inp = gr.Textbox(
            label       = "Your question",
            placeholder = "e.g. How long should I study before taking the CCNA?",
            lines       = 2,
        )

    btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(
        label    = "Answer",
        lines    = 10,
        interactive = False,
    )

    sources = gr.Textbox(
        label       = "Retrieved from",
        lines       = 4,
        interactive = False,
    )

    # Wire submit button and Enter key to the same handler
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Markdown(
        """
        ---
        *Answers are based only on collected forum posts and the CCNA Study Guide.
        Always verify important details with official Cisco documentation.*
        """
    )


if __name__ == "__main__":
    demo.launch()
