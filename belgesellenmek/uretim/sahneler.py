import re,sys
def _lo(x): return x.replace("I","ı").replace("İ","i").lower()
def _up(x): return x.replace("i","İ").replace("ı","I").upper()
def tr_title(t): return " ".join((_up(w[0])+_lo(w[1:])) if w else w for w in t.split(" "))

def parse(ep):
    t=open(f"../senaryolar/bolum{ep}.md",encoding="utf-8").read()
    parts=re.split(r"\*\*\[SAHNE (\d+) — ([^\]]*?)\]\*\*",t)
    sc=[]
    for i in range(1,len(parts),3):
        n=int(parts[i]); head=parts[i+1]; body=parts[i+2]
        title=tr_title(re.sub(r",?\s*\d+:\d+\s*[–-]\s*\d+:\d+.*$","",head.split("—")[0]).strip())
        g=re.search(r"GÖRSEL:(.*)",body)
        m=re.search(r"ANLATIM:(.*?)(?=\n- 🎵|\n---|\Z)",body,re.S)
        a=[re.sub(r"^\s*>\s?","",l) for l in (m.group(1).split("\n") if m else [])]
        sc.append(dict(n=n,title=title,gorsel=g.group(1).strip() if g else "",text=" ".join(x.strip() for x in a if x.strip())))
    return sc
if __name__=="__main__":
    for s in parse(sys.argv[1]): print(s["n"],s["title"],len(s["text"]),"kar")
