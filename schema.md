# JSON Schema: simulation payload (v2, research-backed)

The agent must produce a single JSON file with exactly this structure.
`validate.py` checks it before the PDF is generated.

```json
{
  "meta": {
    "product_name": "string",
    "language": "ar | en (the language the brief is written in; all text below must be in it)",
    "one_liner": "string (value proposition in one sentence)",
    "generated_on": "YYYY-MM-DD",
    "research_mode": "web | user_supplied | none",
    "assumptions": ["string (optional: every guess made because the input did not say)"]
  },

  "sources": [
    {
      "id": "s1",
      "title": "string (page or document title)",
      "url": "string (the page you actually opened; or 'provided by user')",
      "accessed": "YYYY-MM-DD",
      "type": "retailer | news | study | official | blog | forum | other",
      "reliability": "high | medium | low",
      "note": "string (publication date, sample, limits; say if data is old or unsourced)"
    }
  ],

  "market": {
    "summary": "string (2 to 4 sentences, only what the sources support)",
    "signals": [
      { "claim": "string (a fact with its number, unit and date)", "source_ids": ["s1"] }
    ],
    "price_benchmarks": [
      { "item": "string", "price": "string (as shown in the source)", "unit": "string", "source_ids": ["s1"] }
    ],
    "implications": ["string (your analysis for this product; labelled as analysis in the report, so it needs no source)"]
  },

  "competitors": [
    {
      "id": "c1",
      "name": "string",
      "type": "direct | indirect | substitute",
      "what_they_offer": "string",
      "price_note": "string (prices exactly as found, with channel and date)",
      "strengths": ["string"],
      "weaknesses": ["string (only what a source shows or the brief states)"],
      "customer_voice": [ { "quote": "string (real review/comment text)", "source_ids": ["s1"] } ],
      "source_ids": ["s1"]
    }
  ],

  "personas": [
    {
      "id": "p1",
      "name": "string (display name)",
      "handle": "string (without @)",
      "segment": "string (which audience segment)",
      "bio": "string (one line)",
      "stance": "supportive | skeptical | hostile | neutral",
      "age": "string",
      "occupation": "string",
      "location": "string",
      "monthly_budget": "string (say if it comes from the brief or is an assumption)",
      "current_alternatives": ["competitor ids"],
      "pain_points": ["string"],
      "buying_triggers": ["string"],
      "grounding": [ { "fact": "string (a fact about this segment taken from a source)", "source_ids": ["s1"] } ],
      "day": [
        {
          "time": "HH:MM (24h, ASCII digits, in order from waking up to sleep; may pass midnight once)",
          "activity": "string",
          "evidence": "sourced | inferred | assumption",
          "source_ids": ["s1"],
          "touchpoint": "string (optional: how this moment relates to the product)"
        }
      ]
    }
  ],

  "feed": [
    {
      "id": "t1",
      "author": "persona id, or 'brand'",
      "type": "post | reply | quote",
      "reply_to": "tweet id or null",
      "text": "string",
      "likes": 0,
      "reposts": 0
    }
  ],

  "objections": [
    {
      "id": "o1",
      "title": "string (short phrasing of the objection)",
      "raised_by": ["persona ids"],
      "category": "price | trust | hygiene | convenience | alternatives | other",
      "severity": "blocker | friction",
      "mentions": 0,
      "resolvability": "design | messaging | fundamental",
      "suggested_fix": "string",
      "validation_question": "string (a quick-check question the owner can post or ask in one message — open and non-leading; no interviews assumed)",
      "evidence": ["tweet ids"],
      "source_ids": ["optional: sources behind market or competitor facts the objection relies on"]
    }
  ],

  "unspoken_objections": [
    {
      "title": "string",
      "why_it_might_exist": "string",
      "validation_question": "string",
      "source_ids": ["optional"]
    }
  ],

  "strengths": [ { "title": "string", "evidence": ["tweet ids"] } ],

  "sentiment": { "supportive": 0, "neutral": 0, "skeptical": 0, "hostile": 0 },

  "next_steps": ["string (3 to 5 concrete actions)"],

  "research_gaps": ["string (what you looked for and could not find or open; never empty)"]
}
```

## Evidence rules

- `sourced`: a source you opened states it; `source_ids` must be non-empty. `inferred`: follows logically from a sourced fact or from the brief (cite the source if one applies). `assumption`: a plausible guess. Never upgrade a guess to `sourced`.
- Most of a daily routine is normally `inferred` or `assumption`. That is expected and is shown in the report as an evidence bar per persona.
- `research_mode: none` means nothing was researched: `sources`, `competitors`, `grounding` stay empty and no entry may be `sourced`. The report prints a "not research-backed" banner.
- `web` needs at least 5 sources, 3 competitors, 3 market signals and 1 grounding fact per persona. `user_supplied` needs at least 2 sources.

## Other rules

- `sentiment` values are counts of personas (or of feed posts by stance); the template normalises them.
- Every `objections[].evidence` id must exist in `feed`; every `raised_by` id in `personas`; every `source_ids` entry in `sources`.
- `mentions` should equal the number of distinct feed posts that raise the objection.
- `unspoken_objections` are hypotheses nobody said in the feed. Derive them from competitor weaknesses, research gaps and routine constraints. Label them honestly.
- Do not output a single "acceptance rate". The report shows the sentiment split instead.
