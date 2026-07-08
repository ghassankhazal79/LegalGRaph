# -*- coding: utf-8 -*-
# Rebuild extracted entities and graph after changing data.
# Usage: python scripts/04_extract_entities_graph.py
import re,json,itertools
from pathlib import Path
from collections import Counter,defaultdict
AR_DIACRITICS=re.compile(r"[\u064B-\u0652\u0670]")
def norm(t):
    if not isinstance(t,str): return ""
    s=AR_DIACRITICS.sub("", t.strip())
    s=re.sub("[\u0622\u0623\u0625]","ا",s).replace("ى","ي").replace("ـ","")
    return re.sub(r"\s+"," ",s)
patterns=[
("LAW_REFERENCE", r"(?:قانون|نظام|تعليمات|قرار|امر|لائحة)\s+(?:رقم\s*)?\(?\d+\)?\s*(?:لسنة\s*\d{4})?"),
("ARTICLE", r"(?:المادة|مادة)\s*(?:\(?\d+\)?|[اأإآ]لاولى|الثانية|الثالثة|الرابعة|الخامسة|السادسة|السابعة|الثامنة|التاسعة|العاشرة)"),
("MINISTRY", r"وزارة\s+[\u0600-\u06FF\s]{2,60}?(?=،|\.|؛|\(|\)|$)"),
("UNIVERSITY", r"(?:جامعة|الجامعة)\s+[\u0600-\u06FF\s]{2,45}?(?=،|\.|؛|\(|\)|$)"),
("COLLEGE", r"(?:كلية|المعهد|معهد)\s+[\u0600-\u06FF\s]{2,45}?(?=،|\.|؛|\(|\)|$)"),
("DATE", r"\b(?:19|20)\d{2}\b|\b\d{1,2}[/-]\d{1,2}[/-](?:19|20)?\d{2}\b"),
("CONDITION", r"(?:يشترط|شرط|الشروط|على ان|يجب ان|يلزم|لا يجوز|يجوز)\s+[^\.،؛]{5,120}"),
("DEGREE", r"(?:بكالوريوس|ماجستير|دكتوراه|دبلوم|الدراسات العليا|الشهادة الجامعية الاولية|الشهادة العليا)")
]
def clean(x): return norm(x).strip(" ،؛.:-()[]{}")
def extract(text):
    text=norm(text); out=[]; seen=set()
    for lab,pat in patterns:
        for m in re.finditer(pat,text):
            val=clean(m.group(0)); key=(val,lab)
            if len(val)>=3 and key not in seen:
                seen.add(key); out.append({"text":val,"label":lab})
    return out
data=Path("data"); counter=Counter(); labels=Counter(); occ=defaultdict(list); docents=defaultdict(set)
with open(data/"docs.jsonl",encoding="utf-8") as f:
    for line in f:
        d=json.loads(line); did=d["doc_id"]; src=d.get("source")
        for e in extract(d.get("text_norm") or d.get("text") or ""):
            k=(e["text"],e["label"]); counter[k]+=1; labels[e["label"]]+=1; docents[did].add(k)
            occ[k].append({"doc_id":did,"source":src,"snippet":(d.get("text") or "")[:600]})
entities=[]
for (txt,lab),cnt in counter.most_common():
    entities.append({"id":f"E{len(entities)+1:04d}","text":txt,"label":lab,"frequency":cnt,"documents":sorted({o["doc_id"] for o in occ[(txt,lab)]}),"sources":sorted({str(o["source"]) for o in occ[(txt,lab)] if o.get("source")}),"occurrences":occ[(txt,lab)][:30]})
idmap={(e["text"],e["label"]):e["id"] for e in entities}; ec=Counter()
for ks in docents.values():
    for a,b in itertools.combinations(sorted(ks),2):
        if a in idmap and b in idmap: ec[(idmap[a],idmap[b])]+=1
nodes=[{"id":e["id"],"label":e["text"][:60],"title":f'{e["text"]} ({e["label"]}) freq={e["frequency"]}',"group":e["label"],"value":e["frequency"]} for e in entities[:250]]
allowed={n["id"] for n in nodes}
edges=[{"from":a,"to":b,"value":w,"title":f"co-occurrence: {w}"} for (a,b),w in ec.most_common(600) if a in allowed and b in allowed]
(data/"entities.json").write_text(json.dumps({"summary":{"total_entities":len(entities),"label_counts":dict(labels),"top_entities":entities[:20]},"entities":entities},ensure_ascii=False,indent=2),encoding="utf-8")
(data/"entity_graph.json").write_text(json.dumps({"nodes":nodes,"edges":edges},ensure_ascii=False,indent=2),encoding="utf-8")
print("entities",len(entities),"nodes",len(nodes),"edges",len(edges))
