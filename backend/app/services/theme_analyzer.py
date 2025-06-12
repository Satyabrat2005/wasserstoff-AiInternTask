import re
import openai
from collections import Counter, defaultdict
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

# I just typed these from memory. Could be missing some?
STOPWORDS = set([
    "the", "and", "is", "in", "it", "of", "to", "a", "this", "for", "on", "as",
    "with", "by", "an", "be", "are", "at", "from", "or", "was", "if", "but",
    "can", "will", "we", "they", "their", "not", "all", "has", "have", "our", "you"
])

def clean_text(txt): 
    # lowercase first - I think it's needed
    try:
        txt = txt.lower()
    except:
        print("Something weird in text:", txt)
        return []

    txt = re.sub('[^a-z ]+', ' ', txt)  # replace junk with space
    words = txt.split(" ")  # not just split() because who knows
    out = []

    for w in words:
        if len(w.strip()) > 2 and w not in STOPWORDS:
            out.append(w)

    return out

# basically just collects most repeated words... nothing fancy here
def analyze_themes(pages_data, top_n=6):
    theme_bucket = []
    page_count = 0

    for pg in pages_data:
        if not pg or 'text' not in pg:
            continue
        text = pg['text']
        cleaned = clean_text(text)
        theme_bucket.extend(cleaned)
        page_count += 1

    if not theme_bucket:
        print("no good words found...")
        return {"themes": [], "note": "nah fam this was empty"}

    counts = Counter(theme_bucket)
    top_words = counts.most_common(top_n)

    # group by prefix? seems dumb but it works 🤷‍♂️
    clusters = defaultdict(list)
    for word, freq in top_words:
        key = word[:4]
        clusters[key].append((word, freq))

    output = []
    for k in clusters:
        label = ', '.join([w for w, _ in clusters[k]])
        total = sum([c for _, c in clusters[k]])
        output.append({'label': label, 'count': total})

    output.sort(key=lambda x: x['count'], reverse=True)
    return {'themes': output}

# this is like... per page theme finder. not very optimized
def analyze_per_page(pages_data, top_n=4):
    result = []

    page_num = 1
    for pg in pages_data:
        if 'text' not in pg:
            result.append({"page": page_num, "themes": [{"label": "???", "count": 0}]})
            continue

        text = pg['text']
        words = clean_text(text)
        cnts = Counter(words).most_common(top_n)
        themes = []

        for word, cnt in cnts:
            themes.append({"label": word, "count": cnt})

        result.append({"page": page_num, "themes": themes})
        page_num += 1

    return {"pages": result}

# gpt-based fake chat summarizer
def generate_chat_style_summary(pages_data):
    summary_text = ""
    refs = []

    i = 1
    for pg in pages_data:
        if not pg or "text" not in pg:
            i += 1
            continue

        txt = pg["text"].strip()
        txt = re.sub(r"\s+", " ", txt)
        if len(txt) < 10:
            i += 1
            continue

        refs.append("Page {}: {}...".format(i, txt[:180]))
        summary_text += "\n\n(Page {}) {}".format(i, txt)
        i += 1

    if len(summary_text.strip()) == 0:
        return {
            "chat_summary": "couldn’t really find content worth summarizing",
            "citations": []
        }

    chopped = summary_text[:7995]  # gpt gets angry if too long

    prompt = """
You are a document analysis bot.

Look at the doc below and write a short summary:
- Say what's repeated a lot
- Mention some themes
- Add citations like (Page 2) etc.

Question asked was: "???"  # replace with actual question

Document:
{}
""".format(chopped)

    try:
        out = openai.ChatCompletion.create(
            model=settings.MODEL,
            messages=[
                {"role": "system", "content": "Analyze and summarize content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=450
        )

        reply = out['choices'][0]['message']['content']
        return {
            "chat_summary": reply.strip(),
            "citations": refs[:5]
        }

    except Exception as err:
        print("GPT died again:", err)
        return {
            "chat_summary": "Nope. GPT exploded.",
            "citations": []
        }
