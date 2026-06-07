# The Unofficial Guide — Project 1

---

## Domain

This project covers student-generated knowledge about university campus dining halls — including reviews of food quality, wait times, meal plan tips, dietary options, and late-night eating strategies. This knowledge is valuable because official university dining websites only list menus and hours, not honest student experiences like which stations run out of food, which dining hall has the shortest lines, or how to maximize meal plan value. Students currently have to dig through Reddit threads, word of mouth, and scattered blog posts to find this information.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| #   | Source                     | Type               | URL or file path                            |
| --- | -------------------------- | ------------------ | ------------------------------------------- |
| 1   | Yelp Reviews               | Student reviews    | documents/raw/01_main_dining_hall_yelp.txt  |
| 2   | Google Maps Reviews        | Student reviews    | documents/raw/02_south_cafe_google.txt      |
| 3   | Reddit r/CampusLife        | Forum thread       | documents/raw/03_reddit_dining_thread1.txt  |
| 4   | Reddit r/DormLife          | Forum thread       | documents/raw/04_reddit_dining_thread2.txt  |
| 5   | Student Union Review Board | Student reviews    | documents/raw/05_north_grill_reviews.txt    |
| 6   | Student Blog               | Guide              | documents/raw/06_meal_plan_guide.txt        |
| 7   | Campus Newspaper           | Comparison article | documents/raw/07_dining_hall_comparison.txt |
| 8   | Student Accessibility Blog | Dietary guide      | documents/raw/08_special_diets_guide.txt    |
| 9   | Student Forum              | Late-night guide   | documents/raw/09_late_night_food_guide.txt  |
| 10  | Orientation Blog           | Freshman tips      | documents/raw/10_freshman_dining_tips.txt   |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**
The corpus is a mix of short student reviews (2–4 sentences each) and longer guide-style content. A 500-character chunk captures one complete review or one coherent tip while staying focused on a single topic. Larger chunks (1000+ characters) would mix unrelated topics like wait times and dietary restrictions, making retrieval imprecise. Smaller chunks (200 characters) would plit reviews mid-sentence and lose meaning. The 50-character overlap ensures key facts that fall near chunk boundaries — like a specific dining hall name or wait time — appear in both adjacent chunks so retrieval can find them from either direction. Preprocessing removed document header metadata (Source, URL, Date collected lines) to keep chunks focused on substantive student content.

**Final chunk count:** 56 chunks across 10 documents

## Sample Chunks

**Chunk 1** (source: 03_reddit_dining_thread1.txt)

```
Post: "Honest review of every dining hall after 2 semesters" (upvotes: 847)
Author: u/seniorsurvival_guide

After two full years eating on campus, here's my honest breakdown:
Main Hall: Best variety, worst wait times. Go early or go late, never at noon.
The Thursday special (usually steak or salmon) is actually restaurant quality.
```

**Chunk 2** (source: 06_meal_plan_guide.txt)

```
Critical rule: Meal Swipes expire every Sunday at midnight. Dining Dollars roll over semester to semester but not year to year. If you have leftover swipes on Sunday night, use them to grab food to stockpile for your dorm room.
```

**Chunk 3** (source: 08_special_diets_guide.txt)

```
Halal: One dedicated station at Main Hall, open daily 11am-2pm and 5pm-8pm. Runs out fast — arrive within the first 30 minutes of service. No halal options at South Cafe or North Grill.
```

**Chunk 4** (source: 07_dining_hall_comparison.txt)

```
Consistency: 6/10 — Hit or miss depending on the day and time. Thursday evening is consistently the best meal of the week. Monday lunches are often disappointing. Wait Times: 4/10 — The biggest weakness. Average wait of 18 minutes during peak hours.
```

**Chunk 5** (source: 10_freshman_dining_tips.txt)

```
Tip 3: Never go to Main Hall between noon and 1:15pm unless you enjoy standing in line with 300 other people. Adjust your class schedule if possible to eat at 11:30am or after 1:30pm.
```

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers (local inference, no API key required)

**Production tradeoff reflection:**
For a real deployment serving thousands of students, I would evaluate OpenAI's text-embedding-3-small — it has higher accuracy on short conversational text and supports a larger context window (8191 tokens vs 256 for MiniLM), which matters when reviews contain specific named entities like dining hall names or dish names. The tradeoff is cost (API calls per query) and latency versus the free local inference of MiniLM. If the student body were multilingual, I would consider paraphrase-multilingual-MiniLM-L12-v2. For latency-sensitive mobile use cases, a smaller distilled model would be preferable even if slightly less accurate.

---

## Retrieval Test Results

**Query 1:** "What do students say about wait times at Main Hall during lunch?"

Top returned chunks:

- 03_reddit_dining_thread1.txt (distance: 0.3655) — "Go early or go late, never at noon. The Thursday special is actually restaurant quality."
- 10_freshman_dining_tips.txt (distance: 0.3750) — "Never go to Main Hall between noon and 1:15pm... eat at 11:30am or after 1:30pm."
- 07_dining_hall_comparison.txt (distance: 0.4150) — "Wait Times: 4/10 — Average wait of 18 minutes during peak hours."

These chunks are relevant because they all directly address Main Hall wait times and timing strategies.

**Query 2:** "What are the best late-night food options on campus after 8pm?"

Top returned chunks:

- 09_late_night_food_guide.txt (distance: 0.3313) — "Campus Convenience Store open 24/7, accepts dining dollars."
- 09_late_night_food_guide.txt (distance: 0.3471) — "Food Trucks rotate on campus until 10pm."
- 10_freshman_dining_tips.txt (distance: 0.3539) — "Use to-go box strategy before Main Hall closes at 9pm."

These chunks are relevant because they directly list late-night options with hours and locations.

**Query 3:** "What meal plan tips do students recommend for best value?"

Top returned chunks:

- 03_reddit_dining_thread1.txt (distance: 0.3527) — "Meal plan system: swipes at main halls, dollars anywhere."
- 06_meal_plan_guide.txt (distance: 0.3533) — "To-go container swipe is the single best value on campus."
- 02_south_cafe_google.txt (distance: 0.4009) — "Combo deal — entree plus drink for $7 — is the best value."

These chunks are relevant because they contain specific meal plan strategies and value tips.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant for university students looking for information about campus dining halls. Answer the user's question using ONLY the information
provided in the documents below. Do not use any outside knowledge. If the documents do not contain enough information to answer the question, respond with:
"I don't have enough information about that in my sources." Always end your response with a "Sources:" section listing the document filenames you used to answer the question.
```

**How source attribution is surfaced in the response:**

```
Source attribution is enforced two ways: (1) the system prompt explicitly instructs the LLM to end every response with a Sources section listing document filenames,
and (2) the app.py interface programmatically appends a separate Sources box showing the unique filenames of all retrieved chunks, independent of what the LLM writes.
This ensures sources are always visible even if the LLM omits them.
```

---

## Example Responses

**Example 1 — In-scope query with citation:**

Question: "What do students say about wait times at Main Hall during lunch?"

Response:

> According to u/seniorsurvival_guide, the best strategy for avoiding long wait
> times at Main Hall is to "go early or go late, never at noon." This implies that
> wait times are particularly long during the noon hour. The dining hall comparison
> also notes an average wait of 18 minutes during peak hours (Wait Times: 4/10).
>
> Sources: [Document 1 - 03_reddit_dining_thread1.txt]

Sources box: 10_freshman_dining_tips.txt, 07_dining_hall_comparison.txt, 03_reddit_dining_thread1.txt

**Example 2 — In-scope query with citation:**

Question: "What are the best late-night food options on campus after 8pm?"

Response:

> After 8pm, the best late-night food options include the Campus Convenience Store
> in the Library Basement (open 24/7, accepts dining dollars, has microwaveable meals
> and snacks). The $3.99 mac and cheese cups are a popular choice at 2am. Vending
> machines are available in every dorm but are limited to chips and candy.
>
> Sources: 09_late_night_food_guide.txt, 10_freshman_dining_tips.txt

**Example 3 — Out-of-scope query (refusal response):**

Question: "What is the best laptop to buy for college?"

Response:

> I don't have enough information about that in my sources.

---

## Query Interface

**Input field:** A text box labeled "Your question" with placeholder text showing
an example query. Users can type any question about campus dining.

**Output fields:**

- Answer box — displays the LLM-generated response with inline source citations
- Sources box — displays a bullet list of source document filenames retrieved

**Example buttons:** Five pre-loaded example questions that auto-fill the input box.

**Sample interaction transcript:**

Input: "What meal plan tips do students recommend for best value?"

Answer:

> According to the documents, students recommend using the CampusEats nutrition app
> to track macros. They also suggest avoiding late-night pizza and waffle stations.
> Additionally, one student recommends the combo deal at South Cafe (entree plus drink
> for $7) as the best value on campus.
> Sources: 03_reddit_dining_thread1.txt, 06_meal_plan_guide.txt, 02_south_cafe_google.txt

Sources:

> • 06_meal_plan_guide.txt
> • 02_south_cafe_google.txt
> • 03_reddit_dining_thread1.txt

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| #   | Question                                                          | Expected answer                                                                     | System response (summarized)                                         | Retrieval quality  | Response accuracy  |
| --- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------ | ------------------ |
| 1   | What do students say about wait times at Main Hall during lunch?  | Lines 15-25 min during 12-1:15pm; go at 11:30am or after 1:30pm                     | Advised to go early or late, never at noon; average 18 min wait      | Relevant           | Accurate           |
| 2   | What are the best late-night food options on campus after 8pm?    | South Cafe until 11pm, library store 24/7, food trucks until 10pm                   | Library store 24/7, food trucks, vending machines as emergency       | Relevant           | Partially accurate |
| 3   | What meal plan tips do students recommend for best value?         | Use to-go container; swipes expire weekly; dining dollars at food trucks            | CampusEats app, avoid late-night stations, $7 combo at South Cafe    | Partially relevant | Partially accurate |
| 4   | Which dining hall is best for students with dietary restrictions? | Main Hall — vegan station, halal until 2pm, gluten-free with 48hr notice            | Main Hall has halal station and salad bar; info described as limited | Relevant           | Partially accurate |
| 5   | How does North Grill compare to Main Hall in food quality?        | North Grill consistent (9/10) less variety; Main Hall more variety but inconsistent | Returned dietary restrictions answer instead of comparison           | Off-target         | Inaccurate         |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "How does North Grill compare to Main Hall in food quality?"

**What the system returned:** The system returned an answer about dietary restrictions
at Main Hall instead of a comparison between North Grill and Main Hall food quality.

**Root cause (tied to a specific pipeline stage):**
This is a retrieval failure at the embedding stage. The query contains the phrase "food quality" which semantically overlapped with chunks discussing food options for
dietary restrictions — both involve evaluating food at Main Hall. The all-MiniLM-L6-v2 model mapped "food quality" closer to the dietary restrictions chunks than to the
comparison document chunks that contained the actual quality scores (9/10 vs 6/10). The specific comparison data was in 07_dining_hall_comparison.txt but that chunk was
not retrieved in the top-4 results.

**What you would change to fix it:**
Increase top-k from 4 to 6 to cast a wider retrieval net, or add the dining hall name "North Grill" more prominently in the comparison document chunks so the
embedding model can better distinguish comparison queries from general food queries.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The chunking strategy section of planning.md — specifically the decision to use 500-character chunks with 50-character overlap — directly guided the implementation
of the custom split_text() function. Having the chunk size and overlap pre-decided meant the implementation was straightforward and the rationale was already documented,
making it easy to explain why those numbers were chosen when the LangChain import failed and a custom implementation was needed.

**One way your implementation diverged from the spec, and why:**
The spec planned to use LangChain's RecursiveCharacterTextSplitter for chunking, but the implementation diverged to a custom split_text() function. The reason was
a breaking import path change in newer versions of LangChain — the class moved from langchain.text_splitter to langchain_text_splitters, and even after installing the
correct package, the import still failed in the Python 3.14 environment. Rather than spending more time on dependency debugging, a custom implementation with identical
chunk_size=500 and overlap=50 parameters was written without any external dependencies.

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

- _What I gave the AI:_ The Documents section and Chunking Strategy section of
  planning.md, plus the requirement to load .txt files from documents/raw/
- _What it produced:_ A complete ingest.py with load_documents(), clean_text(),
  and chunk_documents() using LangChain's RecursiveCharacterTextSplitter
- _What I changed or overrode:_ Replaced the LangChain import with a custom
  split_text() function after the import path failed in Python 3.14. The chunk
  size (500) and overlap (50) parameters remained identical to the spec.

**Instance 2**

- _What I gave the AI:_ The Retrieval Approach section and Architecture diagram
  from planning.md, plus the grounding requirement (answer only from retrieved
  context, cite sources, refuse if not enough information)
- _What it produced:_ Complete retriever.py with embed_and_store() and retrieve()
  functions, and query.py with the grounded system prompt and ask() function
- _What I changed or overrode:_ The system prompt was tightened to explicitly
  say "Do not use any outside knowledge" after testing showed the model occasionally
  added general advice not present in the documents. The out-of-scope test confirmed
  the final prompt correctly triggers refusal.
