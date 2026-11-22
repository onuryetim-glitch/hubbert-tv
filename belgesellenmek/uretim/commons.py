import time, requests, re, os, json, hashlib, html
API="https://commons.wikimedia.org/w/api.php"
S=requests.Session(); S.headers["User-Agent"]="belgesellenmek-pipeline/1.0 (educational documentary; contact via channel)"
OK_LIC=re.compile(r"^(cc0|cc[- ]by(?!-nc)|cc[- ]by[- ]sa|public domain|pd|attribution|gfdl)",re.I)
def clean(s): return html.unescape(re.sub(r"<[^>]+>","",s or "")).strip()
def search(q, kind="image", limit=12):
    """kind: image|video"""
    ft = "video" if kind=="video" else "bitmap"
    p=dict(action="query",format="json",generator="search",gsrnamespace=6,gsrsearch=f"{q} filetype:{ft}",gsrlimit=limit,
           prop="imageinfo",iiprop="url|size|mime|extmetadata|mediatype",iiurlwidth=1600)
    r=None
    for t in range(5):
        time.sleep(1.2)
        try:
            r=S.get(API,params=p,timeout=30).json(); break
        except Exception: time.sleep(4*(t+1))
    if r is None: return []
    out=[]
    for pg in (r.get("query",{}).get("pages",{}) or {}).values():
        ii=(pg.get("imageinfo") or [None])[0]
        if not ii: continue
        m=ii.get("extmetadata",{})
        lic=clean(m.get("LicenseShortName",{}).get("value",""))
        if not OK_LIC.match(lic) and "public domain" not in lic.lower(): continue
        if "nc" in lic.lower().split() or "-nc" in lic.lower() or "nd" in lic.lower().replace("and","").split("-"): continue
        out.append(dict(title=pg["title"],url=ii["url"],thumb=(ii.get("thumburl") or ii["url"]).split("?")[0].replace("thumb.wikimedia.org","upload.wikimedia.org"),w=ii["width"],h=ii["height"],
            size=ii.get("size",0),mime=ii["mime"],lic=lic,artist=clean(m.get("Artist",{}).get("value","")),
            page=ii["descriptionurl"],index=pg.get("index",99)))
    out.sort(key=lambda x:x["index"]); return out
def fetch(item, kind, outdir, maxmb=40):
    os.makedirs(outdir,exist_ok=True)
    ext=os.path.splitext(item["url"])[1].lower() if kind=="video" else ".jpg"
    fn=os.path.join(outdir,hashlib.md5(item["url"].encode()).hexdigest()[:12]+ext)
    if os.path.exists(fn): return fn
    u=item["url"] if kind=="video" else item["thumb"]
    if kind=="video" and item["size"]>maxmb*1e6: return None
    for t in range(4):
        time.sleep(1); r=S.get(u,timeout=180)
        if r.status_code==200: break
        time.sleep(5*(t+1))
    else: return None
    open(fn,"wb").write(r.content); return fn
if __name__=="__main__":
    import sys
    for k in ("image","video"):
        for it in search(sys.argv[1],k,8)[:5]:
            print(k,it["lic"],it["w"],it["h"],it["size"]//1000,"KB",it["title"][:60])
