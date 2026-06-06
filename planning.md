# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

This project covers student-generated knowledge about university dining halls —
including reviews of food quality, wait times, meal plan tips, dietary options,
and late-night eating strategies. This knowledge is valuable because official
university dining websites only list menus and hours, not honest student
experiences like which stations run out of food, which dining hall has the
shortest lines, or how to get the most out of a meal plan. Students currently
have to dig through Reddit threads, word of mouth, and scattered blog posts
to find this information.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source                     | Description                                                                 | URL or location                             |
| --- | -------------------------- | --------------------------------------------------------------------------- | ------------------------------------------- |
| 1   | Yelp Reviews               | Student reviews of Main Dining Hall — food quality, wait times, best dishes | documents/raw/01_main_dining_hall_yelp.txt  |
| 2   | Google Maps Reviews        | Student reviews of South Campus Cafe — coffee, grab-and-go, late night      | documents/raw/02_south_cafe_google.txt      |
| 3   | Reddit r/CampusLife        | Thread: honest review of every dining hall after 2 semesters                | documents/raw/03_reddit_dining_thread1.txt  |
| 4   | Reddit r/DormLife          | Thread: which dining hall is worth the walk, meal plan hacks                | documents/raw/04_reddit_dining_thread2.txt  |
| 5   | Student Union Review Board | Reviews of North Grill — burgers, bowls, athlete meals                      | documents/raw/05_north_grill_reviews.txt    |
| 6   | Student Blog               | Unofficial meal plan survival guide — swipes, dining dollars, strategy      | documents/raw/06_meal_plan_guide.txt        |
| 7   | Campus Newspaper           | Side-by-side comparison of all three dining halls across 5 criteria         | documents/raw/07_dining_hall_comparison.txt |
| 8   | Student Accessibility Blog | Guide to dining with dietary restrictions — vegan, halal, gluten-free       | documents/raw/08_special_diets_guide.txt    |
| 9   | Student Forum              | Complete guide to eating after 8pm — late night options and strategies      | documents/raw/09_late_night_food_guide.txt  |
| 10  | Orientation Blog           | 15 dining hall tips from seniors — compiled from 200-student survey         | documents/raw/10_freshman_dining_tips.txt   |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Reasoning:**
The documents are a mix of short student reviews (2-4 sentences each) and longer guide-style content. A 500-character chunk is large enough to capture
one complete review or one coherent tip, but small enough that each chunk stays focused on a single topic. If chunks were larger (e.g. 1000+ characters),
one chunk might mix unrelated topics — wait times AND dietary restrictions — making retrieval imprecise. If chunks were smaller (e.g. 200 characters), a
single review would be split mid-sentence and lose meaning.

The 50-character overlap ensures that if a key fact (like a specific wait time
or dining hall name) falls near the boundary between two chunks, it appears in
both — so retrieval can find it from either direction.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, no API key required, no rate limits)

**Top-k:** 4 chunks per query

**Production tradeoff reflection:**
For a real deployment serving thousands of students, I would evaluate OpenAI's text-embedding-3-small — it has higher accuracy on short conversational
text and supports a larger context window (8191 tokens vs 256 for MiniLM), which matters when reviews contain specific named entities like dining hall names
or dish names. The tradeoff is cost (API calls per query) and latency vs the free local inference of MiniLM. If the student body were multilingual, I would
consider a multilingual model like paraphrase-multilingual-MiniLM-L12-v2. For latency-sensitive use cases (mobile app), a smaller distilled model would
be preferable even if slightly less accurate.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Test Question                                                           | Expected Answer                                                                               |
| --- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 1   | What do students say about wait times at Main Dining Hall during lunch? | Lines are 15-25 min during 12-1:15pm; best to go at 11:30am or after 1:30pm.                  |
| 2   | What are the best late-night food options on campus after 8pm?          | South Cafe until 11pm, library store 24/7, food trucks until 10pm                             |
| 3   | What meal plan tips do students recommend for best value?               | Use to-go container for more food per swipe; swipes expire weekly                             |
| 4   | Which dining hall is best for students with dietary restrictions?       | Main Hall — vegan station, halal until 2pm, gluten-free with 48hr notice.                     |
| 5   | How does North Grill compare to Main Hall in food quality?              | North Grill more consistent (9/10) but less variety; Main Hall more variety but inconsistent. |

---

## Anticipated Challenges

1. **Chunk boundary splitting key facts:** Some tips span multiple sentences where the first sentence names the dining hall and the second gives the
   specific advice. If these split across a chunk boundary, retrieval may return a chunk with advice but no context about which dining hall it applies
   to. The 50-character overlap is designed to mitigate this but may not fully solve it for longer multi-sentence facts.

2. **Query vocabulary mismatch:** Students may ask using informal language ("cheapest place to eat", "fastest lunch spot") that doesn't match the
   exact words in the documents ("best value", "shortest wait times"). Semantic search with MiniLM should handle most of this, but very
   colloquial or slang-heavy queries may still retrieve off-target chunks if the embedding space doesn't map them close enough to the document text.

---

## Architecture

```ascii
+------------------+     +------------------+     +---------------------------+
|  Document        |     |   Chunking       |     |  Embedding + Vector Store |
|  Ingestion       |---->|                  |---->|                           |
|                  |     |  Recursive       |     |  all-MiniLM-L6-v2         |
|  10 x .txt files |     |  CharText        |     |  sentence-transformers    |
|  documents/raw/  |     |  Splitter        |     |  ChromaDB (local)         |
|                  |     |  size=500        |     |  + source metadata        |
|                  |     |  overlap=50      |     |                           |
+------------------+     +------------------+     +---------------------------+
                                                              |
                                                              v
+------------------+     +------------------+     +---------------------------+
|  Query Interface |     |   Generation     |     |  Retrieval                |
|                  |<----|                  |<----|                           |
|  Gradio web UI   |     |  Groq API        |     |  Semantic search          |
|  localhost:7860  |     |  llama-3.3-70b   |     |  top-k = 4 chunks         |
|                  |     |  grounded prompt |     |  ChromaDB query           |
|                  |     |  + attribution   |     |                           |
+------------------+     +------------------+     +---------------------------+
```

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I will give Claude the Documents section and Chunking Strategy section of this planning.md and ask it to implement two functions: load_documents() that reads all .txt files from documents/raw/ and returns a list of dicts with text and source filename, and chunk_documents() that uses RecursiveCharacterTextSplitter with chunk_size=500 and chunk_overlap=50. I will verify the output by printing 5 random chunks and checking that each is readable, self-contained, and under 500 characters.

**Milestone 4 — Embedding and retrieval:**
I will give Claude the Retrieval Approach section and Architecture diagram and ask it to implement embed_and_store() that embeds all chunks using all-MiniLM-L6-v2 and stores them in ChromaDB with source metadata, and retrieve() that accepts a query string and returns the top-4 most relevant chunks with their source filenames. I will verify by running 3 test queries and checking that returned chunks are visibly relevant and distance scores are below 0.5.

**Milestone 5 — Generation and interface:**
I will give Claude the grounded generation requirement (answer only from retrieved context, cite sources, refuse if not enough information) and the Gradio skeleton from the project instructions and ask it to implement the full ask() function and app.py. I will verify grounding by asking a question my documents don't cover and confirming the system refuses rather than generating a plausible answer from general knowledge.
