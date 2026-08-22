from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def load_documents():
    docs = []
    for path in sorted(DATA.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        deprecated = "DEPRECATED" in text.upper() or "DO NOT USE FOR CURRENT" in text.upper()
        docs.append({"name": path.name, "text": text, "deprecated": deprecated})
    return docs

def chunks(text, size=180, overlap=35):
    words = text.split()
    out = []
    start = 0
    while start < len(words):
        out.append(" ".join(words[start:start+size]))
        if start + size >= len(words):
            break
        start += size - overlap
    return out

def score(query, passage):
    q = set(re.findall(r"[a-z0-9_-]+", query.lower()))
    p = set(re.findall(r"[a-z0-9_-]+", passage.lower()))
    return len(q & p)

def search_documents(query, k=6):
    results = []
    for doc in load_documents():
        if doc["deprecated"]:
            continue
        for i, chunk in enumerate(chunks(doc["text"])):
            s = score(query, chunk)
            if s:
                results.append({"source": doc["name"], "chunk": i, "score": s, "text": chunk})
    return sorted(results, key=lambda x: x["score"], reverse=True)[:k]
