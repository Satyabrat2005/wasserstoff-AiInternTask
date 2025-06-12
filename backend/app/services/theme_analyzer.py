import re
from collections import Counter, defaultdict

# yeah, didn’t bother with nltk – handpicked stopwords
STOPWORDS = {
    "the", "and", "is", "in", "it", "of", "to", "a", "that", "this", "for", "on",
    "as", "with", "by", "an", "be", "are", "at", "from", "or", "was", "if", "but",
    "can", "will", "we", "they", "their", "not", "all", "has", "have", "our", "you"
}

# basic cleaner, just gets rid of crap and keeps lowercase words that matter
def clean_text(txt):
    txt = txt.lower()
    txt = re.sub(r'[^a-z\s]', ' ', txt)  # strip non-letter stuff
    words = txt.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return words

# main thing – scans all pages, finds common-ish themes
def analyze_themes(pages_data, top_n=5):
    bag = []

    for pg in pages_data:
        raw = pg.get("text", "")
        bag.extend(clean_text(raw))

    if not bag:
        return {"themes": [], "note": "found nothing useful lol"}

    counts = Counter(bag)
    common = counts.most_common(top_n)

    # okay this is janky – we group by 4-letter prefix. close enough.
    theme_map = defaultdict(list)
    for word, count in common:
        prefix = word[:4]
        theme_map[prefix].append((word, count))

    themes = []
    for _, group in theme_map.items():
        total = sum(cnt for _, cnt in group)
        label = ", ".join(w for w, _ in group)
        themes.append({"label": label, "count": total})

    themes.sort(key=lambda x: x["count"], reverse=True)
    return {"themes": themes}


# new thing – do that ^ but page by page
def analyze_per_page(pages_data, top_n=4):
    result = []

    for i, pg in enumerate(pages_data, start=1):
        txt = pg.get("text", "")
        words = clean_text(txt)
        counts = Counter(words).most_common(top_n)

        themes = [{"label": w, "count": c} for w, c in counts]
        result.append({
            "page": i,
            "themes": themes
        })

    return {"pages": result}
