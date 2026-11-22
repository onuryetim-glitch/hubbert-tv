import json,sys,os,time
import commons
ep=sys.argv[1]; q=json.load(open(f"bolum{ep}_sorgular.json"))
out=f"medya/b{ep}"; os.makedirs(out,exist_ok=True)
manifest=[]
for sc,d in q.items():
    got={"video":[],"image":[]}
    for kind,maxn,qs in (("video",1,d["video"]),("image",3,d["image"])):
        seen=set()
        for qq in qs:
            if len(got[kind])>=maxn: break
            for it in commons.search(qq,kind,10):
                if it["url"] in seen: continue
                if kind=="video" and (it["w"]<640 or it["size"]>15e6): continue
                if kind=="image" and (it["w"]<1000):  continue
                f=commons.fetch(it,kind,out)
                if not f: continue
                seen.add(it["url"]); got[kind].append(dict(file=f,kind=kind,scene=int(sc),query=qq,**{k:it[k] for k in("title","lic","artist","page","w","h")}))
                if len(got[kind])>=maxn: break
    print("sahne",sc,"video",len(got["video"]),"görsel",len(got["image"]),flush=True)
    manifest+=got["video"]+got["image"]
json.dump(manifest,open(f"{out}/manifest.json","w"),ensure_ascii=False,indent=1)
print("toplam",len(manifest))
