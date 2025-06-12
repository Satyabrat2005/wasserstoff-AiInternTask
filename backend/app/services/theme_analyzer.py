import re
import openai
from collections import Counter, defaultdict
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

# classic anti-word list. not even complete lol
STOPWORDS = set([
    "the", "and", "is", "in", "it", "of", "to", "a", "this", "for", "on", "as",
    "with", "by", "an", "be", "are", "at", "from", "or", "was", "if", "but",
    "can", "will", "we", "they", "their", "not", "all", "has", "have", "our", "you"
])

def clean_text(txt):
    try:
        txt = txt.lower()
    except:
        print("yo what's this:", txt)
        return []

    txt = re.sub('[^a-z ]+', ' ', txt)
    words = txt.split(" ")
    bag = []

    for word in words:
        if len(word.strip()) > 2 and word not in STOPWORDS:
            bag.append(word)

    return bag

# finds top repeated stuff in all pages
# not smart. just counting

def analyze_themes(pages_data, top_n=6):
    soup = []
    total_pages = 0

    for thing in pages_data:
        if thing and 'text' in thing:
            cleaned = clean_text(thing['text'])
            soup.extend(cleaned)
            total_pages += 1
        else:
            print("blank page or missing text")

    if not soup:
        print("uhhh nothing to analyze")
        return {"themes": [], "note": "empty vibes"}

    freq = Counter(soup)
    popular = freq.most_common(top_n)

    bucket = defaultdict(list)
    for word, count in popular:
        start = word[:4]  # grouping by first 4 letters bcz... yeah
        bucket[start].append((word, count))

    cooked = []
    for prefix in bucket:
        group_words = [w for w, _ in bucket[prefix]]
        total_count = sum([c for _, c in bucket[prefix]])
        cooked.append({
            "label": ", ".join(group_words),
            "count": total_count
        })

    cooked.sort(key=lambda x: x["count"], reverse=True)
    return {"themes": cooked}

# very per-page. barely works. meh.
def analyze_per_page(pages_data, top_n=4):
    output = []
    pg = 1

    for thing in pages_data:
        if 'text' not in thing:
            output.append({"page": pg, "themes": [{"label": "???", "count": 0}]})
            pg += 1
            continue

        text = thing['text']
        words = clean_text(text)
        freq = Counter(words).most_common(top_n)
        themes = [{"label": w, "count": c} for w, c in freq]

        output.append({"page": pg, "themes": themes})
        pg += 1

    return {"pages": output}

def extract_relevant_answers(pages_data, question: str):
    keywords = [w.lower() for w in question.split() if len(w) > 2]
    results = []

    for pg in pages_data:
        pg_num = pg.get("page", 0)
        text = pg.get("text", "")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for i, para in enumerate(paragraphs):
            if any(k in para.lower() for k in keywords):
                results.append({
                    "answer": para[:200] + "...",
                    "page": pg_num,
                    "paragraph": i + 1
                })

    return results
