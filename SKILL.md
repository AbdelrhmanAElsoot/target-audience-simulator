---
name: target-audience-simulator
description: Reads whatever brief the business owner sends, asks for whatever is missing, researches competitors, market and audience from real web sources, builds evidence-tagged personas with a full day in their life, simulates their reaction to a realistic launch announcement post, and produces a PDF with ranked objections and cheap checks the owner can run on their own.
---

# Target Audience Simulator (Research-backed Objection Discovery)

This skill is an objection-discovery tool, not market research and not a forecast. It researches first, builds personas from what it found, simulates their reaction, and reports ranked objections plus quick checks the owner can run on their own. Its job is to make the owner's life easier: it does the heavy lifting, and nothing in the output should require the owner to run interviews. Every fact in the report either points to a source you opened or is labelled `inferred` or `assumption`.

## Input

There is no form and no template. The brief is whatever the business owner sends: a `.md`, `.docx`, `.txt`, screenshots, voice notes, or plain text pasted in the chat. Read a `.docx` with `pandoc -t markdown file.docx`. Your first job is to mine that file for everything it contains and answer what you can from it; only then do you ask for the rest.

## Language rule

The report language is the language the brief is written in, not the language of the market. An English brief about an Egyptian product gets an English report and an English feed; an Arabic brief gets an Arabic report in natural Egyptian-flavored dialect.
- Decide from the free-text answers in the brief (ignore template labels and product names). Set `meta.language` to `ar` or `en`.
- Every field the reader sees must be in that language: feed posts, objections, market text, competitor text, persona profiles and daily routines, next steps, assumptions. Brand names, handles and source titles may stay as they are.
- If the brief is genuinely mixed or unclear, follow the language the owner is writing in the chat. An explicit user instruction always wins.
- Search in the audience's language and in English; write the report in the brief's language.

## Steps

0. **Intake: mine the brief, then ask for the rest.** Read everything the owner sent first and extract every fact you can; answer from the file itself what you can, and ask only about what is genuinely missing or ambiguous — never re-ask what the brief says. Treat this as interviewing the owner until, together, you hold a full brief.
   - Sort every unknown into one of three buckets before doing anything:
      1. **Owner-knows:** practical facts about the product and the audience's real life that the owner can answer and the web usually cannot (sizes and prices, how it sells, where the audience actually lives, whether their housing includes food, kitchen access, who cooks, real schedules, real budgets). Never assume these. Ask the owner, and if they do not know, the item becomes an explicit hypothesis, not a silent guess.
      2. **Research-can-find:** public facts the web can answer (competitor prices, market size, official statistics, public reviews). Defer these to step 1; do not bother the owner with them.
      3. **Nobody-knows:** judgement calls no one can answer (future reactions, taste preferences of strangers). Treat as hypotheses from the start and record them in `meta.assumptions`.
   - Keep asking until this checklist is covered — this is what "taking a full brief" means:
      - **The product as it actually is:** every size or SKU with its real price (numbers, never tiers like "mid-tier"), what is inside the pack, shelf life and whether it is chilled or frozen, the prep promise, and how it is produced and by whom.
      - **How it actually sells:** the channel (subscription, one-off orders, retail), delivery area and fees, minimums, how customers order, the current stage (idea / pre-launch / running), any traction or past attempts, and any launch offer.
      - **The audience as they actually live:** 3 or more segments, each with budget, where they actually live, whether their housing includes food, kitchen access, who cooks, who pays versus who uses, and what they use today instead.
      - **Why this report:** the decision it should inform, the competitors the owner already knows and fears, and what they suspect the market thinks of them.
   - How to ask: one round, grouped by the four checklist topics above, ordered by how much a wrong guess would distort the result, each question with a suggested default or 2 to 3 options. Use the interactive question tool if one exists, otherwise a short numbered list in the user's language.
   - If the brief already covers the checklist, skip the questions and say so in one line.
   - If the user says to just run it, or nobody can answer (unattended run), proceed with defaults and record every guess in `meta.assumptions`. Never invent a number silently.
   - Save the answers into the brief under "Clarifications" (for a `.docx`, write them to a new `.md` next to it).
   - Also settle the **research mode**: `web` if you have web search and page-fetch tools; `user_supplied` if you have none but the user gives links, files or pasted data (read them and list them as sources); `none` if neither. Tell the user which mode you are in.

1. **Research (skip only in mode `none`).** Write findings to `research_notes.md` as you go (fact, number, unit, date, source id), then build the JSON from those notes. Budget: about 12 to 20 searches and page opens in total; stop when the coverage below is met or you can record what is missing.
   - **Competitors (3 to 6):** direct (same job), indirect (adjacent product), substitute (what people do today, including doing nothing or doing it themselves). For each: what they offer, price with channel and date, strengths, weaknesses, and customer voice (real reviews, forum threads, comments) if you can find any.
   - **Market:** at least 3 sourced signals (size, growth, trends, regulation, seasonality, channel behavior) and price benchmarks for the product and its substitutes. Search for the market where the product is sold.
   - **Audience:** per segment, look for spending, habits, media use, working or studying hours, and daily rhythm in surveys, official statistics, studies, forums and social posts. At least 1 sourced fact per persona.
   - **Source discipline (this is what keeps the report honest):**
     - A search result list is not evidence. Open the page and read it before citing it. Cite only what you read.
     - Copy numbers exactly, with currency, unit and the date of the data. Put the publication date and any age or sampling limit in the source `note`. Flag data older than 2 years.
     - Rate each source: `high` (official statistics, peer-reviewed study, a seller's own page for its own price), `medium` (reputable news or trade press), `low` (undated blogs, aggregators, anonymous posts, unsourced figures).
     - If sources disagree, show both. Never average them into one made-up number.
     - If a page fails or is blocked, try one different source, then record a gap. Do not retry the same blocked URL and do not use mirrors or caches to get around a block.
     - Never invent a source, URL, quote, review or statistic. A fact recalled from memory is an `assumption`, not `sourced`.
   - **Research gaps:** record everything you looked for and could not find or open (`research_gaps`). Thin evidence is a normal, useful result; an empty list is not believable.
   - **Questions for the owner:** while researching, keep a running list `questions_for_owner` of questions the research raised that the owner can answer and the web cannot (for example: can you match the competitor price you found, what is your delivery area, do you offer subscriptions, does your supplier allow X). Add one more item to the list: whether the owner already has a real launch announcement post or a draft of one (see step 3). Check each one against the three buckets in step 0: if the owner knows it, it goes on the list; if research can still find it, spend one more search on it first; only items nobody can answer stay as hypotheses.

1.5. **Second intake round (after research, before personas).** If `questions_for_owner` is not empty, go back to the business owner with the whole list — this round has no fixed cap, but keep each question concrete and decision-relevant; do not ask what research already answered. This round is also where the owner hands over their real launch announcement post, if they have one. For every answer: fold it into the brief under "Clarifications" (or the `.md` next to it) and re-open any search it invalidates (for example, if the owner says the delivery area is one district, re-check competitors in that district). For every question the owner cannot answer: turn it into an explicit hypothesis, record it in `meta.assumptions` with the wording "unconfirmed by owner", and let the personas and feed reflect it as a hypothesis to test — never as a settled fact. If the list is empty, skip this step and say so in one line.

2. **Build the personas from the research.** Start from the segments in the brief, then enrich them with what you found. For each persona fill: age, occupation, location, monthly budget (say whether it is from the brief or assumed), current alternatives (competitor ids), pain points, buying triggers, `grounding` (facts from sources, with source ids), and a **full day**.
   - **Day in the life:** 8 to 14 entries from waking up to sleep, `HH:MM` in 24h ASCII digits, in order (it may pass midnight once), spanning at least 12 hours. Cover waking, meals, commute or transitions, work or study blocks, breaks, screen time, shopping or ordering moments, social contexts and winding down. Mark where the product could enter or fail in `touchpoint`.
   - **Tag every entry:** `sourced` = a source you opened says it (cite ids); `inferred` = follows from a sourced fact or the brief; `assumption` = plausible guess. Never upgrade a guess. It is normal that most entries are `inferred` or `assumption`; the report shows the evidence split per persona.
   - Personas must differ in schedule, constraints and money, not only in opinion. A night-shift worker's day is not a student's day.
   - **Reality-check the housing and food setup.** Before locking a persona, check that their living situation is affordable and consistent: can someone on this budget actually live where you placed them, is food provided or included with their housing, and do they have a kitchen? A persona living somewhere the segment cannot afford, or whose meals are already covered by student or staff housing, is not a customer for this product — replace them with a real buyer from the same segment (for example the dorm resident whose housing does **not** include meals, or the student renting near the campus instead of in the upscale district), or ask the owner in step 1.5 if you are unsure.

3. **Simulate the feed (25 to 30 posts).**
   - **The announcement post is an artifact, not filler.** If the owner handed over a real post or draft in step 1.5, use their exact text. If not, write a realistic draft built only from the brief's facts — the real price, the real sizes, the real subscription terms, the delivery area, and how to order — in the register small local businesses actually post in: prices visible, a clear call to order, and the claims the owner would genuinely make ("أعلى جودة", "متوفر دلوقتي", "اطلب على الواتساب"). A launch offer (discount, first-N-customers deal) appears only if the brief or owner states one — never invent it.
   - Show the draft to the owner for a quick confirm or edit before simulating, since the owner is the one who would actually post it. In an unattended run, generate it from the brief's facts and record that choice in `meta.assumptions`.
   - The post is what the personas react to, so every number they should push back on must be visible in it. A generic post ("we are excited to announce...") is forbidden: a post with no price, no offer and no claim is not a launch post.
   - One announcement post from `brand`, then posts, replies, and quotes from the personas.
   - Each post must follow from that persona's pains, schedule and budget and from the market facts you found (for example a persona citing a competitor's real price or a stock problem you saw). Do not let personas raise issues that nothing in the research or brief supports unless you are deliberately testing a hypothesis.
   - Write in the natural register of the audience. For Egyptian audiences use Egyptian Arabic (mixed with Franco-Arabic where natural). Do not write formal Arabic.
   - Avoid polite, generic AI praise. Include real skepticism, price haggling, side arguments between personas, and at least one persona who changes their mind.

4. **Extract objections.** Group the feed into distinct objections. For each, fill every field in `schema.md`: category, severity (`blocker` stops the purchase, `friction` only reduces enthusiasm), mentions, resolvability, a suggested fix, a quick-check question the owner can run on their own (open, non-leading, and cheap — something they can post in a WhatsApp status, a story poll, or the product's own page comments; no interviews), and `source_ids` when a competitor or market fact backs it.

5. **Add unspoken objections (3 to 5).** What would stop a real buyer that nobody said? Derive them from competitor weaknesses, research gaps and the personas' daily constraints (who pays, storage, seasons, delivery, trust in the seller, habits). Mark them as hypotheses.

6. **Summarise.** Fill `strengths`, `sentiment` (count of personas by stance), `market.implications` (your analysis, e.g. what the price means next to substitutes, labelled as analysis), and `next_steps` (3 to 5 concrete actions the owner can do on their own with little effort — a price change, publishing proof, a trial pack, a poll to their own customers — never "run interviews" or "find focus groups").

7. **Write and validate.**
   - Save the payload as `temp_data.json` following `schema.md` exactly.
   - Run: `python validate.py temp_data.json` and fix every error it reports.
   - Run: `python generate_pdf.py --input-json temp_data.json --output report.pdf`

8. **Report back.** Give the PDF path, then the top 3 objections (blockers first) in three short bullets, then one line on research coverage (how many sources, the biggest gaps). State clearly that these are hypotheses from a simulation, and that the quick checks in the report are ones the owner can run on their own.

## Forbidden (these make the report misleading)

- No "acceptance rate", no score out of 10, no per-feature percentages. The only numbers allowed are counts from the feed and figures copied from sources.
- No fabricated sources, URLs, reviews or statistics; no market size without a source. If you did not open it, you did not read it.
- No price or discount recommendation that is not derived from figures in the brief or sources. Say "check this price cheaply yourself (a trial pack, a poll, a comment prompt)" instead.
- No marketing-report tone. Personas are real people arguing, not reviewers writing a brief. One-line praise with no reservation is not allowed.
- Do not drop or replace a persona defined in the brief. Every persona must post at least twice.

## Self-check before saving the JSON

1. Does every number about the market or a competitor carry a source id you actually opened?
2. Is every `sourced` day entry stated by its cited source, and every other entry honestly `inferred` or `assumption`?
3. Does every objection cite tweet ids that really raise it?
4. Is there at least one `blocker`, at least one argument between personas, and at least one persona who changed their mind?
5. Is every `validation_question` open and non-leading ("what would make you...") rather than yes/no, and cheap enough that the owner can post or ask it in one message?
6. Does `research_gaps` say what you could not find?
7. Does the brand's announcement post carry the real price and real terms from the brief or the owner's own text, with nothing invented in it?

## Originality

- Derive every objection from the specific details of THIS product: its price, size, location, channel, personas and the competitors you found. If an objection would apply to any consumer product ("price is high", "no reviews"), make it concrete with a number or situation from the research, or drop it.
- Invent persona names, handles and conversation flow fresh for each run. Do not open the `tests/` folder; it contains renderer fixtures, not a style guide.
- The JSON format is defined only by `schema.md`.

## Rules

- Never claim the simulation predicts real market behavior.
- Follow the Language rule: the brief's language is the report's language.
- All paths in scripts are resolved relative to the skill folder, so run from any directory.
