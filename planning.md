# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
       The system will provide advice to students who are interested in obtaining their CCNA. It uses information from forums online from a range of timelines spanning the last 10 years. This knowledge will be valuable because although Cisco's official CCNA guide serves as a great resource for preparing for the CCNA exam, this guide can add supplemental information about tried methods from others who have successfully passed their exam or have failed and documented their experiences. It can also help to provide a structure for learners creating a study plan to establish personal benchmarks and milestones throughout their learning experience to ensure that they are on the right track. Users will be able to ask the system for guidance on how to prepare for and pass the CCNA.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500

**Overlap:** 50

**Reasoning:** A chunk size of 500 fits for roughly one paragraph and an overlap of 50 captures roughly 1-2 sentences. So the chunk sizes will recursively split roughly for each paragraph and if the paragraph splitting is off by a bit, the overlap will capture those 1-2 sentences to provide meaningful context.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 and sentence-transformers

**Top-k:** 5

**Production tradeoff reflection:**
The all-MiniLM-L6-v2 is a good choice for embedding because f the no rate limits which means that my system will essentially be able to make an indefinite amount of requests without being blocked by the server. I chose 5 chunks because a Google search suggested that 3-5 is a good number of chunks to retrieve for an accurate Q&A system. 

The context length (total size that the model can input at once) is 256 tokens for the all-MiniLM-L6-v2. The text-embedding-ada-002 can handle up to 8191 tokens but has rate limits. The all-MiniLM-L6-v2 runs locally with sentence-transformers, meaning no rate limits, no API costs, and no latency from external calls. In production with real users, I would consider switching to a model like OpenAI's text-embedding-ada-002 or a arger open-source model for better accuracy, longer context length, and multiple languages, but this would introduce API rate limits, cost per token, and external latency as tradeoffs.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What study resources do CCNA learners most commonly reccomend? | Boson ExSim, JITL, Packet Tracer, Official CCNA book|
| 2 | How long do most people study before taking the CCNA exam? | Roughly 3-6 months for beginners, some pass in 45-60 days |
| 3 | How important is Packet Tracer for CCNA exam preparation? | Hands-on learning is a crucial part of passing and packet tracer is important for that|
| 4 | What mistakes fo people make when studying for the CCNA that cause them to fail the first time? | Memorization, lack of hands-on labs, subnetting|
| 5 | What are the best free resources available for CCNA preparation? | JITL, Packet Tracer |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. I am using recursive character splitting for my chunking strategy so there is possibility for one comment to be parsed into different chunks and the whole context not being represented.

2. I could retrieve a relevant chunk but the LLM could hallucinate and say that it doesn't know based on the context provided.

---

<!-- TODO: do this diagram -->
## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
     1. Document Ingestion
     2. Chunking Strategy
     3. Vector Store, Semantic Search and Retrieval
     4. Grounded Response Generation
     5. Query Interface
     6. Evaluation Report

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
