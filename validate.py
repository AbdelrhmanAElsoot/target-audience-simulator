import json
import re
import sys

SEVERITY = {"blocker", "friction"}
CATEGORY = {"price", "trust", "hygiene", "convenience", "alternatives", "other"}
RESOLVE = {"design", "messaging", "fundamental"}
STANCE = {"supportive", "skeptical", "hostile", "neutral"}
TYPES = {"post", "reply", "quote"}
MODES = {"web", "user_supplied", "none"}
EVIDENCE = {"sourced", "inferred", "assumption"}
RELIABILITY = {"high", "medium", "low"}
COMP_TYPES = {"direct", "indirect", "substitute"}
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
MIN_SOURCES = {"web": 5, "user_supplied": 2}
MIN_COMPETITORS = 3
MIN_SIGNALS = 3
MIN_DAY_ENTRIES = 8
MIN_DAY_SPAN_MIN = 12 * 60


def arabic_ratio(text):
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return None
    return sum(1 for ch in letters if "؀" <= ch <= "ۿ") / len(letters)


def as_list(x):
    return x if isinstance(x, list) else []


def check_language(data, errs):
    lang = data["meta"].get("language")
    if lang not in ("ar", "en"):
        return
    texts = [t.get("text", "") for t in as_list(data["feed"]) if isinstance(t, dict) and t.get("author") != "brand"]
    for o in as_list(data["objections"]):
        texts += [o.get(k, "") for k in ("title", "suggested_fix", "validation_question")]
    for u in as_list(data["unspoken_objections"]):
        texts += [u.get(k, "") for k in ("title", "why_it_might_exist", "validation_question")]
    texts += [x for x in as_list(data["next_steps"]) if isinstance(x, str)]
    texts += [s.get("title", "") for s in as_list(data["strengths"])]
    for p in as_list(data["personas"]):
        texts.append(p.get("bio", ""))
        texts += [e.get("activity", "") for e in as_list(p.get("day")) if isinstance(e, dict)]
    if isinstance(data.get("market"), dict):
        texts.append(data["market"].get("summary", ""))
        texts += [x for x in as_list(data["market"].get("implications")) if isinstance(x, str)]
    for c in as_list(data["competitors"]):
        texts.append(c.get("what_they_offer", ""))
    ratios = [r for r in (arabic_ratio(x) for x in texts if isinstance(x, str)) if r is not None]
    if not ratios:
        return
    bad = [r for r in ratios if (r < 0.5 if lang == "ar" else r > 0.2)]
    if len(bad) > max(1, len(ratios) // 10):
        want = "Arabic" if lang == "ar" else "English"
        errs.append(f"meta.language is '{lang}' but {len(bad)} of {len(ratios)} text fields are not {want}; the report must be entirely in the brief's language")


def validate(data):
    errs = []

    def need(obj, keys, where):
        if not isinstance(obj, dict):
            errs.append(f"{where}: expected an object")
            return False
        for k in keys:
            if k not in obj:
                errs.append(f"{where}: missing '{k}'")
        return True

    def refs(ids, sids, where, required=False):
        if not isinstance(ids, list):
            errs.append(f"{where}: source_ids must be a list")
            return
        if required and not ids:
            errs.append(f"{where}: needs at least one source id")
        for i in ids:
            if i not in sids:
                errs.append(f"{where}: unknown source {i}")

    tops = ("meta", "sources", "market", "competitors", "personas", "feed", "objections",
            "unspoken_objections", "strengths", "sentiment", "next_steps", "research_gaps")
    for top in tops:
        if top not in data:
            errs.append(f"missing top-level '{top}'")
    if errs:
        return errs

    need(data["meta"], ["product_name", "language", "one_liner", "generated_on", "research_mode"], "meta")
    if data["meta"].get("language") not in ("ar", "en"):
        errs.append("meta.language must be 'ar' or 'en'")
    mode = data["meta"].get("research_mode")
    if mode not in MODES:
        errs.append("meta.research_mode must be 'web', 'user_supplied' or 'none'")
    if "assumptions" in data["meta"] and not isinstance(data["meta"]["assumptions"], list):
        errs.append("meta.assumptions must be a list of strings")

    if not as_list(data["research_gaps"]):
        errs.append("research_gaps is empty: state what you could not find or verify (use a note that no research was run if mode is 'none')")

    # sources
    sids = set()
    for s in as_list(data["sources"]):
        if need(s, ["id", "title", "url", "accessed", "type", "reliability", "note"], f"source {s.get('id') if isinstance(s, dict) else '?'}"):
            if s["id"] in sids:
                errs.append(f"source {s['id']}: duplicate id")
            sids.add(s["id"])
            if s.get("reliability") not in RELIABILITY:
                errs.append(f"source {s['id']}: bad reliability")
    if mode == "none":
        if sids:
            errs.append("research_mode 'none' cannot list sources")
        if as_list(data["competitors"]):
            errs.append("research_mode 'none' cannot list competitors (they would be unsourced)")
    elif mode in MIN_SOURCES:
        if len(sids) < MIN_SOURCES[mode]:
            errs.append(f"research_mode '{mode}' needs at least {MIN_SOURCES[mode]} sources; found {len(sids)}")
        if len(as_list(data["competitors"])) < MIN_COMPETITORS:
            errs.append(f"expected at least {MIN_COMPETITORS} competitors or substitutes")

    # market
    if need(data["market"], ["summary", "signals", "price_benchmarks", "implications"], "market"):
        for i, sg in enumerate(as_list(data["market"].get("signals"))):
            if need(sg, ["claim", "source_ids"], f"market.signals[{i}]"):
                refs(sg["source_ids"], sids, f"market.signals[{i}]", required=True)
        for i, pb in enumerate(as_list(data["market"].get("price_benchmarks"))):
            if need(pb, ["item", "price", "unit", "source_ids"], f"market.price_benchmarks[{i}]"):
                refs(pb["source_ids"], sids, f"market.price_benchmarks[{i}]", required=True)
        if mode in MIN_SOURCES and len(as_list(data["market"].get("signals"))) < MIN_SIGNALS:
            errs.append(f"market.signals needs at least {MIN_SIGNALS} sourced signals")

    # competitors
    cids = set()
    for c in as_list(data["competitors"]):
        where = f"competitor {c.get('id') if isinstance(c, dict) else '?'}"
        if need(c, ["id", "name", "type", "what_they_offer", "price_note", "strengths", "weaknesses", "customer_voice", "source_ids"], where):
            cids.add(c["id"])
            if c.get("type") not in COMP_TYPES:
                errs.append(f"{where}: bad type")
            refs(c["source_ids"], sids, where, required=True)
            for j, v in enumerate(as_list(c.get("customer_voice"))):
                if need(v, ["quote", "source_ids"], f"{where} customer_voice[{j}]"):
                    refs(v["source_ids"], sids, f"{where} customer_voice[{j}]", required=True)

    # personas
    pids = set()
    pkeys = ["id", "name", "handle", "segment", "bio", "stance", "age", "occupation", "location",
             "monthly_budget", "current_alternatives", "pain_points", "buying_triggers", "grounding", "day"]
    for p in as_list(data["personas"]):
        where = f"persona {p.get('id') if isinstance(p, dict) else '?'}"
        if not need(p, pkeys, where):
            continue
        pids.add(p["id"])
        if p.get("stance") not in STANCE:
            errs.append(f"{where}: bad stance")
        for a in as_list(p.get("current_alternatives")):
            if a not in cids:
                errs.append(f"{where}: current_alternatives references unknown competitor {a}")
        grounding = as_list(p.get("grounding"))
        if mode == "none" and grounding:
            errs.append(f"{where}: grounding must be empty when research_mode is 'none'")
        if mode in MIN_SOURCES and not grounding:
            errs.append(f"{where}: needs at least one grounding fact from a source")
        for j, g in enumerate(grounding):
            if need(g, ["fact", "source_ids"], f"{where} grounding[{j}]"):
                refs(g["source_ids"], sids, f"{where} grounding[{j}]", required=True)

        day = p.get("day")
        if not isinstance(day, list) or len(day) < MIN_DAY_ENTRIES:
            errs.append(f"{where}: day needs at least {MIN_DAY_ENTRIES} entries from waking up to sleep")
            continue
        prev, offset, first = None, 0, None
        for i, e in enumerate(day):
            w = f"{where} day[{i}]"
            if not need(e, ["time", "activity", "evidence", "source_ids"], w):
                continue
            if e["evidence"] not in EVIDENCE:
                errs.append(f"{w}: bad evidence '{e['evidence']}'")
            if e["evidence"] == "sourced":
                if mode == "none":
                    errs.append(f"{w}: 'sourced' is not allowed when research_mode is 'none'")
                refs(e["source_ids"], sids, w, required=True)
            else:
                refs(e["source_ids"], sids, w)
            t = str(e["time"])
            if not TIME_RE.match(t):
                errs.append(f"{w}: time '{t}' must be HH:MM in 24h with ASCII digits")
                continue
            base = int(t[:2]) * 60 + int(t[3:])
            m = base + offset
            if prev is not None and m < prev:
                if offset == 0:
                    offset = 1440
                    m = base + offset
                if m < prev:
                    errs.append(f"{w}: times must run in order from waking up to sleep ('{t}' is out of order)")
                    continue
            if first is None:
                first = m
            prev = m
        if first is not None and prev is not None and prev - first < MIN_DAY_SPAN_MIN:
            errs.append(f"{where}: the day must span at least 12 hours (waking up to sleep)")

    # feed
    tids = set()
    for t in as_list(data["feed"]):
        need(t, ["id", "author", "type", "reply_to", "text", "likes", "reposts"], f"tweet {t.get('id') if isinstance(t, dict) else '?'}")
        tids.add(t.get("id"))
        if t.get("author") != "brand" and t.get("author") not in pids:
            errs.append(f"tweet {t.get('id')}: unknown author {t.get('author')}")
        if t.get("type") not in TYPES:
            errs.append(f"tweet {t.get('id')}: bad type")
    for t in as_list(data["feed"]):
        if t.get("reply_to") and t["reply_to"] not in tids:
            errs.append(f"tweet {t['id']}: reply_to {t['reply_to']} not found")
    if not 20 <= len(data["feed"]) <= 40:
        errs.append(f"feed has {len(data['feed'])} posts; expected roughly 25 to 30")

    # objections
    for o in as_list(data["objections"]):
        where = f"objection {o.get('id') if isinstance(o, dict) else '?'}"
        need(o, ["id", "title", "raised_by", "category", "severity", "mentions", "resolvability",
                 "suggested_fix", "validation_question", "evidence"], where)
        if o.get("severity") not in SEVERITY:
            errs.append(f"{where}: bad severity")
        if o.get("category") not in CATEGORY:
            errs.append(f"{where}: bad category")
        if o.get("resolvability") not in RESOLVE:
            errs.append(f"{where}: bad resolvability")
        for pid in as_list(o.get("raised_by")):
            if pid not in pids:
                errs.append(f"{where}: unknown persona {pid}")
        for tid in as_list(o.get("evidence")):
            if tid not in tids:
                errs.append(f"{where}: unknown tweet {tid}")
        if "source_ids" in o:
            refs(o["source_ids"], sids, where)

    counts = {}
    for t in as_list(data["feed"]):
        counts[t.get("author")] = counts.get(t.get("author"), 0) + 1
    for pid in pids:
        if counts.get(pid, 0) < 2:
            errs.append(f"persona {pid} posts fewer than 2 times")
    if not any(o.get("severity") == "blocker" for o in as_list(data["objections"])):
        errs.append("no objection marked 'blocker'; a simulation with no purchase-blocking objection is likely too polite")
    if not any(t.get("reply_to") for t in as_list(data["feed"])):
        errs.append("feed has no replies; personas must interact")

    for u in as_list(data["unspoken_objections"]):
        need(u, ["title", "why_it_might_exist", "validation_question"], "unspoken_objection")
        if "source_ids" in u:
            refs(u["source_ids"], sids, f"unspoken_objection '{u.get('title')}'")

    check_language(data, errs)

    for k in ("supportive", "neutral", "skeptical", "hostile"):
        if k not in data["sentiment"]:
            errs.append(f"sentiment: missing '{k}'")

    return errs


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python validate.py data.json")
    with open(sys.argv[1], encoding="utf-8") as f:
        errors = validate(json.load(f))
    if errors:
        print("Validation failed:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("OK: payload is valid")
