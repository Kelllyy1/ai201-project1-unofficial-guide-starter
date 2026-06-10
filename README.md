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
The system will provide advice to students who are interested in obtaining their CCNA. It uses information from forums online from a range of timelines spanning the last 10 years. This knowledge will be valuable because although Cisco's official CCNA guide serves as a great resource for preparing for the CCNA exam, this guide can add supplemental information about tried methods from others who have successfully passed their exam or have failed and documented their experiences. It can also help to provide a structure for learners creating a study plan to establish personal benchmarks and milestones throughout their learning experience to ensure that they are on the right track. Users will be able to ask the system for guidance on how to prepare for and pass the CCNA.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->
| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Cisco Learning Network | Forum | https://learningnetwork.cisco.com/s/question/0D5Kd0000BcDaO5KQK/whats-the-best-way-to-prepare-for-the-ccna-a-stepbystep-guide |
| 2 | Cisco Learning Netowrk | Forum | https://learningnetwork.cisco.com/s/question/0D5Kd0000BfjMwfKQE/best-study-methods-for-ccna-these-are-my-suggestions-please-comment-and-ill-try-to-include-yours-as-well |
| 3 | Cisco Learning Network | Forum | https://learningnetwork.cisco.com/s/question/0D5QO00002LnPzR0AV/how-important-is-packet-tracer-to-prepare-for-the-ccna-exam |
| 4 | Reddit r/ccna | Forum | https://www.reddit.com/r/ccna/comments/1o79bbf/how_to_prepare_for_the_ccna_the_most_effective/ |
| 5 | Reddit r/ccna | Forum | https://www.reddit.com/r/ccna/comments/1rx98gu/i_studied_for_45_days_heres_my_experience/ |
| 6 | Reddit r/Cisco | Forum | https://www.reddit.com/r/Cisco/comments/1dxftfv/best_way_to_study_for_ccna/ |
| 7 | Reddit r/networking | Forum | https://www.reddit.com/r/networking/comments/2ewy0p/free_ccna_study_guide_and_a_bunch_of_other_guides/ |
| 8 | Lucid Mentor | Website Blog -> pdf | https://lucidmentor.com/networking/ -> https://lucidresource.com/completed/ccna_studyguide.pdf |
| 9 | Quora | Forum | https://www.quora.com/I-m-about-to-start-studying-for-a-CCNA-any-suggestions |
| 10 | Quora | Forum | https://www.quora.com/What-is-the-best-way-to-study-and-pass-the-CCNA-exam-I-felt-like-I-studied-so-much-and-so-hard-but-did-not-pass-the-first-time-The-material-I-used-was-provided-by-WGU |
| 11 | Quora | Forum | https://www.quora.com/What-is-the-best-way-to-prepare-for-CCNA-How-to-remember-the-most-answers |
| 12 | Quora | Forum | https://www.quora.com/Which-are-the-best-latest-books-for-CCNA-exam-preparation |
| 13 | Network Lessons | Forum | https://forum.networklessons.com/t/what-is-the-best-way-to-prepare-for-ccna/713/5 |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 for PDF; Chunk per comment - split comments > 500 character size and apply overlap.

**Overlap:** 50

**Why these choices fit your documents:**

**Final chunk count:**
The improved approach was to treat my documents differently. Since I used forums for most of my documents and they consisted of comments with individual opinions replying to a centralized question, the better chunking approach was to chunk based on individual comments and then for every comment > 500 characters split them and apply overlap. The PDF was chunked based on recursive splitting.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2

**Production tradeoff reflection:**
The all-MiniLM-L6-v2 is a good choice for embedding because f the no rate limits which means that my system will essentially be able to make an indefinite amount of requests without being blocked by the server. I chose 5 chunks because a Google search suggested that 3-5 is a good number of chunks to retrieve for an accurate Q&A system. 

The context length (total size that the model can input at once) is 256 tokens for the all-MiniLM-L6-v2. The text-embedding-ada-002 can handle up to 8191 tokens but has rate limits. The all-MiniLM-L6-v2 runs locally with sentence-transformers, meaning no rate limits, no API costs, and no latency from external calls. In production with real users, I would consider switching to a model like OpenAI's text-embedding-ada-002 or a arger open-source model for better accuracy, longer context length, and multiple languages, but this would introduce API rate limits, cost per token, and external latency as tradeoffs.

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
| 1 | What study resources do CCNA learners most commonly recommend? | Boson ExSim, JITL, Packet Tracer, Official CCNA book | CCNA learners commonly recommend the "CCNA 200-301 Official Cert Guide Library, 2nd Edition" [Source: cln-1.txt] and Wendell Odom's "Free CCNA Course" YouTube Playlist [Source: cln-1.txt] as study resources. Additionally, Todd Lammle's CCNA study guide is highly recommended [Source: quora-1.txt] and [Source: quora-3.txt], with users finding it useful for its clear explanations and exercises. | Relevant | Accurate |
| 2 | How long do most people study before taking the CCNA exam? | Roughly 3-6 months for beginners, some pass in 45-60 days | Most learners can prepare for the CCNA exam in a 10–12 week timeline [Source: cln-1.txt]. However, the time it takes to prepare can vary depending on the candidate's experience, with new IT professionals possibly needing more than five months [Source: quora-1.txt] and experienced network administrators potentially passing in less than three months [Source: quora-1.txt]. Additionally, some students have been known to pass the exam in as little as 8 weeks [Source: quora-2.txt] or 6 weeks with prior practical experience [Source: quora-2.txt]. | Partially relevant | Partially accurate |
| 3 | How important is Packet Tracer for CCNA exam preparation? | Hands-on learning is a crucial part of passing and packet tracer is important for that| Packet Tracer is useful for CCNA v1.1 certification [Source: cln-3.txt]. It is a quick and convenient way to build virtual labs to practice and solidify theoretical knowledge [Source: cln-3.txt]. However, it is not the only option, as other emulators like CML, GNS3, EVE-NG, or real hardware can also be used [Source: cln-3.txt]. The certification exam does not include any questions about Packet Tracer [Source: cln-3.txt]. Using Packet Tracer, along with other practice tools like Boson practice exams, can help make you better prepared for the actual CCNA exam [Source: cln-1.txt]. | Relevant | Accurate |
| 4 | What mistakes do people make when studying for the CCNA that cause them to fail the first time? | Memorization, lack of hands-on labs, subnetting | One mistake people make when studying for the CCNA is not studying consistently, as the CCNA exam covers a lot of ground and requires frequent and consistent study and practice [Source: quora-2.txt]. Another mistake is not identifying and focusing on their weaknesses, which can be done by taking a practice exam [Source: quora-2.txt]. Additionally, not having a dedicated study schedule and being unable to keep to it can also lead to failure [Source: quora-2.txt]. It is also mentioned that relying solely on the material provided by WGU may not be enough, as one person felt like they studied hard but still did not pass the first time [Source: quora-2.txt]. | Relevant | Accurate |
| 5 | What are the best free resources available for CCNA preparation? | JITL, Packet Tracer | To prepare for the CCNA exam, there are free resources available that can complement your studies. One such resource is Wendell Odom's "Free CCNA Course" YouTube Playlist [Source: cln-1.txt]. This playlist aligns perfectly with the CCNA 200-301 Official Cert Guide Library, 2nd Edition [Source: cln-1.txt]. Additionally, there are other free resources, practice tools, and materials that can help deepen your understanding of the exam topics [Source: cln-1.txt]. 

Note that while other passages mention useful study materials, such as Todd Lamle's book [Source: quora-3.txt] and Rene/Andrew's videos [Source: networklessons-1.txt], they are not specified as free resources. | Relevant | Accurate |

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
