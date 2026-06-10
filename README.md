# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->


| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->


---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What study resources do CCNA learners most commonly recommend? | Boson ExSim, JITL, Packet Tracer, Official CCNA book | CCNA learners commonly recommend the "CCNA 200-301 Official Cert Guide Library, 2nd Edition" [Source: cln-1.txt] and Wendell Odom's "Free CCNA Course" YouTube Playlist [Source: cln-1.txt] as study resources. Additionally, Todd Lammle's CCNA study guide is highly recommended [Source: quora-1.txt] and [Source: quora-3.txt], with users finding it useful for its clear explanations and exercises. | | |
| 2 | How long do most people study before taking the CCNA exam? | Roughly 3-6 months for beginners, some pass in 45-60 days | Most learners can prepare for the CCNA exam in a 10–12 week timeline [Source: cln-1.txt]. However, the time it takes to prepare can vary depending on the candidate's experience, with new IT professionals possibly needing more than five months [Source: quora-1.txt] and experienced network administrators potentially passing in less than three months [Source: quora-1.txt]. Additionally, some students have been known to pass the exam in as little as 8 weeks [Source: quora-2.txt] or 6 weeks with prior practical experience [Source: quora-2.txt]. | | |
| 3 | How important is Packet Tracer for CCNA exam preparation? | Hands-on learning is a crucial part of passing and packet tracer is important for that| Packet Tracer is useful for CCNA v1.1 certification [Source: cln-3.txt]. It is a quick and convenient way to build virtual labs to practice and solidify theoretical knowledge [Source: cln-3.txt]. However, it is not the only option, as other emulators like CML, GNS3, EVE-NG, or real hardware can also be used [Source: cln-3.txt]. The certification exam does not include any questions about Packet Tracer [Source: cln-3.txt]. Using Packet Tracer, along with other practice tools like Boson practice exams, can help make you better prepared for the actual CCNA exam [Source: cln-1.txt]. | | |
| 4 | What mistakes do people make when studying for the CCNA that cause them to fail the first time? | Memorization, lack of hands-on labs, subnetting | One mistake people make when studying for the CCNA is not studying consistently, as the CCNA exam covers a lot of ground and requires frequent and consistent study and practice [Source: quora-2.txt]. Another mistake is not identifying and focusing on their weaknesses, which can be done by taking a practice exam [Source: quora-2.txt]. Additionally, not having a dedicated study schedule and being unable to keep to it can also lead to failure [Source: quora-2.txt]. It is also mentioned that relying solely on the material provided by WGU may not be enough, as one person felt like they studied hard but still did not pass the first time [Source: quora-2.txt]. | | |
| 5 | What are the best free resources available for CCNA preparation? | JITL, Packet Tracer | To prepare for the CCNA exam, there are free resources available that can complement your studies. One such resource is Wendell Odom's "Free CCNA Course" YouTube Playlist [Source: cln-1.txt]. This playlist aligns perfectly with the CCNA 200-301 Official Cert Guide Library, 2nd Edition [Source: cln-1.txt]. Additionally, there are other free resources, practice tools, and materials that can help deepen your understanding of the exam topics [Source: cln-1.txt]. 

Note that while other passages mention useful study materials, such as Todd Lamle's book [Source: quora-3.txt] and Rene/Andrew's videos [Source: networklessons-1.txt], they are not specified as free resources. | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
