import re
from collections import Counter, defaultdict

# rough stopwords list, didn’t use nltk for now
STOPWORDS = {
    "the", "and", "is", "in", "it", "of", "to", "a", "that", "this", "for", "on",
    "as", "with", "by", "an", "be", "are", "at", "from", "or", "was", "if", "but",
    "can", "will", "we", "they", "their", "not", "all", "has", "have", "our"
}

def clean_text(txt):
    txt = txt.lower()
    txt = re.sub(r'[^a-z\s]', ' ', txt)
    words = txt.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return words

def analyze_themes(pages_data, top_n=5):
    words_list = []

    for page in pages_data:
        raw = page.get("text", "")
        words = clean_text(raw)
        words_list += words

    if not words_list:
        return {"themes": [], "note": "no words found"}

    freq = Counter(words_list)
    common_words = freq.most_common(top_n)

    # kind of grouping same-ish words by prefix
    theme_groups = defaultdict(list)
    for word, count in common_words:
        key = word[:4]
        theme_groups[key].append((word, count))

    final_themes = []
    for key, group in theme_groups.items():
        total = sum(c for _, c in group)
        labels = [w for w, _ in group]
        final_themes.append({
            "label": ", ".join(labels),
            "count": total
        })

    final_themes.sort(key=lambda x: x["count"], reverse=True)
    return {"themes": final_themes}
