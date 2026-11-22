import requests,time,os,json,sys,hashlib
S=requests.Session(); S.headers["User-Agent"]="belgesellenmek-pipeline/1.0 (educational documentary)"
API="https://api.inaturalist.org/v1"
def get(url,params=None,t=60):
    for i in range(6):
        time.sleep(1.3)
        try: r=S.get(url,params=params,timeout=t)
        except Exception as e: time.sleep(5); continue
        if r.status_code==429: time.sleep(int(r.headers.get("retry-after","30"))+3); continue
        return r
def taxon(name):
    r=get(API+"/taxa",{"q":name,"per_page":1}); j=r.json() if r is not None and r.status_code==200 else {}
    res=j.get("results",[]); return (res[0]["id"],res[0].get("preferred_common_name") or res[0]["name"]) if res else (None,None)
def photos(name,n,outdir):
    tid,common=taxon(name)
    if not tid: print("  taksa yok",name); return []
    r=get(API+"/observations",{"taxon_id":tid,"photo_license":"cc0,cc-by,cc-by-sa","quality_grade":"research","photos":"true","per_page":15,"order_by":"votes","license":"cc0,cc-by,cc-by-sa"})
    if r is None or r.status_code!=200: return []
    out=[]
    for o in r.json().get("results",[]):
        for p in o.get("photos",[])[:1]:
            lic=(p.get("license_code") or "").lower()
            if lic not in("cc0","cc-by","cc-by-sa"): continue
            url=p["url"].replace("square","large")
            fn=os.path.join(outdir,hashlib.md5(url.encode()).hexdigest()[:12]+".jpg")
            if not os.path.exists(fn):
                rr=get(url,None,90)
                if rr is None or rr.status_code!=200 or len(rr.content)<20000: continue
                open(fn,"wb").write(rr.content)
            out.append(dict(file=fn,kind="image",title=f"{name} ({common})",lic=lic.upper().replace("CC-BY-SA","CC BY-SA").replace("CC-BY","CC BY"),
              artist=p.get("attribution",""),page=f"https://www.inaturalist.org/observations/{o['id']}",w=1024,h=768))
        if len(out)>=n: break
    return out
if __name__=="__main__":
    ep=sys.argv[1]; plan=json.load(open(f"bolum{ep}_turler.json")); outdir=f"medya/b{ep}"; os.makedirs(outdir,exist_ok=True); man=[]
    for sc,items in plan.items():
        for name,n in items:
            ph=photos(name,n,outdir)
            for p in ph: p["scene"]=int(sc); p["query"]=name
            man+=ph; print("sahne",sc,name,len(ph),flush=True)
    json.dump(man,open(f"{outdir}/manifest.json","w"),ensure_ascii=False,indent=1); print("toplam",len(man))
