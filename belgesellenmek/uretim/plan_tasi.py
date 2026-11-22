"""Eski senaryodaki cümle numaralı planı yeni senaryoya taşır: python3 plan_tasi.py EP ESKI_MD"""
import sys,json,os,re,shutil
ep,old=sys.argv[1],sys.argv[2]
import sync
from sahneler import parse
new={s["n"]:sync.split_sents(re.sub(r"\s+"," ",s["text"]).replace("…","...")) for s in parse(ep)}
os.makedirs("/tmp/old/senaryolar",exist_ok=True); None
cwd=os.getcwd(); os.chdir("/tmp/old/uretim"); sys.path.insert(0,cwd)
import importlib,sahneler; importlib.reload(sahneler)
oldp={s["n"]:sync.split_sents(re.sub(r"\s+"," ",s["text"]).replace("…","...")) for s in sahneler.parse(ep)}
os.chdir(cwd)
P=json.load(open(f"bolum{ep}_plan.json"))
def mp(n,i):
    o=oldp[n]; k=min(max(int(i)-1,0),len(o)-1); t=o[k]; nw=new[n]
    if t in nw: return nw.index(t)+1
    for j,x in enumerate(nw):
        if x.startswith(t[:25]): return j+1
    print("EŞLEŞMEDİ",n,i,t[:40]); return int(i)
for k,sh in P["scenes"].items():
    n=int(k)
    for x in sh:
        v=x["s"]; b=int(v); fr=v-b
        x["s"]=round(mp(n,b)+fr,2) if fr else mp(n,b)
json.dump(P,open(f"bolum{ep}_plan.json","w"),ensure_ascii=False,indent=1)
print("ok",{k:[x["s"] for x in v] for k,v in P["scenes"].items()})
