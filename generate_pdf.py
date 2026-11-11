import argparse
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape
from weasyprint import HTML

SKILL_DIR = Path(__file__).resolve().parent

LABELS = {
    "ar": {
        "supportive": "مؤيد", "neutral": "محايد", "skeptical": "متشكك", "hostile": "رافض",
        "blocker": "مانع للشراء", "friction": "يقلل الحماس",
        "price": "السعر", "trust": "الثقة", "hygiene": "النظافة", "convenience": "الراحة",
        "alternatives": "البدائل", "other": "أخرى",
        "design": "يُحل بالتصميم", "messaging": "يُحل بالرسالة", "fundamental": "اعتراض جوهري",
        "mentions": "ذكر", "fix": "الحل المقترح", "ask": "فحص سريع تعمله بنفسك", "why": "لماذا قد يوجد",
        "ev_sourced": "موثّق", "ev_inferred": "مستنتج", "ev_assumption": "افتراض",
        "rel_high": "موثوقية عالية", "rel_medium": "موثوقية متوسطة", "rel_low": "موثوقية ضعيفة",
        "ctype_direct": "منافس مباشر", "ctype_indirect": "منافس غير مباشر", "ctype_substitute": "بديل",
        "sec_market": "دراسة السوق", "sec_signals": "مؤشرات من المصادر", "sec_prices": "مقارنة الأسعار",
        "sec_implications": "ماذا يعني ذلك للمنتج (تحليل وليس مصدراً)",
        "sec_competitors": "المنافسون والبدائل", "sec_personas": "الشخصيات: ملف كامل ويوم كامل",
        "sec_gaps": "ما لم نستطع التحقق منه", "sec_sources": "المصادر",
        "col_item": "البند", "col_price": "السعر", "col_unit": "الوحدة", "col_claim": "المؤشر", "col_source": "المصدر",
        "col_time": "الوقت", "col_activity": "النشاط", "col_evidence": "الدليل",
        "offers": "ما يقدمه", "price_note": "الأسعار", "strengths": "نقاط القوة", "weaknesses": "نقاط الضعف",
        "voice": "صوت العملاء", "none_found": "لم نجد بيانات",
        "age": "العمر", "job": "المهنة", "place": "المكان", "budget": "الميزانية", "alts": "بدائله الحالية",
        "pains": "نقاط الألم", "triggers": "ما يدفعه للشراء", "grounding": "حقائق من المصادر",
        "day": "يوم كامل من الاستيقاظ للنوم", "touch": "علاقته بالمنتج", "evshare": "مصدر معلومات اليوم",
        "accessed": "تاريخ الفتح", "no_grounding": "لا توجد حقائق موثقة لهذه الشخصية.",
        "banner_web": "تقرير مبني على بحث: {n} مصادر فُتحت وقُرئت بتاريخ {d}. كل رقم عن السوق أو المنافسين مربوط برقم مصدر مثل [s1]. ما لا مصدر له مكتوب عليه \"مستنتج\" أو \"افتراض\".",
        "banner_user": "تقرير مبني على {n} مصادر قدمها صاحب المشروع. لم يُجرَ بحث ويب مستقل. ما لا مصدر له مكتوب عليه \"مستنتج\" أو \"افتراض\".",
        "banner_none": "تنبيه: لم يُجرَ أي بحث. الشخصيات وأي كلام عن السوق افتراضات من تقدير الموديل وليست مبنية على مصادر.",
        "assump_title": "افتراضات التقرير", "sent_title": "توزيع الانطباعات",
    },
    "en": {
        "supportive": "Supportive", "neutral": "Neutral", "skeptical": "Skeptical", "hostile": "Hostile",
        "blocker": "Blocker", "friction": "Friction",
        "price": "Price", "trust": "Trust", "hygiene": "Hygiene", "convenience": "Convenience",
        "alternatives": "Alternatives", "other": "Other",
        "design": "Fix by design", "messaging": "Fix by messaging", "fundamental": "Fundamental",
        "mentions": "mentions", "fix": "Suggested fix", "ask": "Quick check you can run yourself", "why": "Why it may exist",
        "ev_sourced": "Sourced", "ev_inferred": "Inferred", "ev_assumption": "Assumption",
        "rel_high": "High reliability", "rel_medium": "Medium reliability", "rel_low": "Low reliability",
        "ctype_direct": "Direct competitor", "ctype_indirect": "Indirect competitor", "ctype_substitute": "Substitute",
        "sec_market": "Market study", "sec_signals": "Signals from sources", "sec_prices": "Price benchmarks",
        "sec_implications": "What this means for the product (analysis, not a source)",
        "sec_competitors": "Competitors and substitutes", "sec_personas": "Personas: full profile and a full day",
        "sec_gaps": "What we could not verify", "sec_sources": "Sources",
        "col_item": "Item", "col_price": "Price", "col_unit": "Unit", "col_claim": "Signal", "col_source": "Source",
        "col_time": "Time", "col_activity": "Activity", "col_evidence": "Evidence",
        "offers": "Offer", "price_note": "Prices", "strengths": "Strengths", "weaknesses": "Weaknesses",
        "voice": "Customer voice", "none_found": "No data found",
        "age": "Age", "job": "Occupation", "place": "Location", "budget": "Budget", "alts": "Current alternatives",
        "pains": "Pain points", "triggers": "Buying triggers", "grounding": "Facts from sources",
        "day": "A full day, waking to sleep", "touch": "Link to the product", "evshare": "Evidence behind this day",
        "accessed": "Accessed", "no_grounding": "No sourced facts for this persona.",
        "banner_web": "Research-backed report: {n} sources were opened and read on {d}. Every market or competitor number points to a source id such as [s1]. Anything without a source is marked \"inferred\" or \"assumption\".",
        "banner_user": "Report built on {n} sources supplied by the product owner. No independent web research was run. Anything without a source is marked \"inferred\" or \"assumption\".",
        "banner_none": "Warning: no research was run. The personas and any statement about the market are assumptions from the model, not based on sources.",
        "assump_title": "Assumptions made", "sent_title": "Sentiment split",
    },
}


def refs(ids):
    if not ids:
        return Markup("")
    return Markup('<span class="ref"><bdi class="ltr">[%s]</bdi></span>' % ", ".join(str(escape(i)) for i in ids))


def build_context(data):
    lang = data["meta"].get("language", "en")
    labels = LABELS.get(lang, LABELS["en"])
    personas = {p["id"]: p for p in data["personas"]}
    comp_names = {c["id"]: c["name"] for c in data["competitors"]}

    counts = data["sentiment"]
    total = sum(counts.values()) or 1
    sentiment_pct = {k: round(counts.get(k, 0) * 100 / total) for k in ("supportive", "neutral", "skeptical", "hostile")}

    order = {"blocker": 0, "friction": 1}
    objections_sorted = sorted(data["objections"], key=lambda o: (order.get(o["severity"], 2), -o["mentions"]))

    personas_view = []
    for p in data["personas"]:
        ev = {"sourced": 0, "inferred": 0, "assumption": 0}
        for e in p["day"]:
            ev[e["evidence"]] += 1
        n = sum(ev.values()) or 1
        personas_view.append({**p, "ev": ev, "ev_pct": {k: round(v * 100 / n, 1) for k, v in ev.items()},
                              "alt_names": [comp_names.get(a, a) for a in p["current_alternatives"]]})

    feed_view = []
    for t in data["feed"]:
        if t["author"] == "brand":
            name, handle, is_brand = data["meta"]["product_name"], "brand", True
        else:
            p = personas[t["author"]]
            name, handle, is_brand = p["name"], p["handle"], False
        feed_view.append({**t, "name": name, "handle": handle, "is_brand": is_brand,
                          "initial": (name.strip() or "?")[0]})

    mode = data["meta"].get("research_mode", "none")
    key = {"web": "banner_web", "user_supplied": "banner_user"}.get(mode, "banner_none")
    banner = labels[key].format(n=len(data["sources"]), d=data["meta"].get("generated_on", ""))

    return {
        "data": data,
        "labels": labels,
        "sentiment_pct": sentiment_pct,
        "objections_sorted": objections_sorted,
        "personas_view": personas_view,
        "feed_view": feed_view,
        "banner": banner,
        "banner_class": "warn" if mode == "none" else "ok",
    }


def build_pdf(json_path, output_pdf_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    env = Environment(loader=FileSystemLoader(str(SKILL_DIR)), autoescape=select_autoescape(["html"]))
    env.globals["refs"] = refs
    html_out = env.get_template("template.html").render(**build_context(data))
    HTML(string=html_out, base_url=str(SKILL_DIR)).write_pdf(output_pdf_path)
    print(f"PDF successfully generated at: {output_pdf_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", required=True, help="Path to simulation JSON")
    parser.add_argument("--output", default="simulation_report.pdf", help="Output PDF path")
    args = parser.parse_args()
    build_pdf(args.input_json, args.output)
