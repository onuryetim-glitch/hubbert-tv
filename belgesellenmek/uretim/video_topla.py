"""Pexels + Pixabay'den sahneye uygun telifsiz VİDEO klipleri indirir. Anahtarlar ortam değişkeninden: PEXELS_API_KEY, PIXABAY_API_KEY"""
import os,sys,json,time,hashlib,requests
from sahneler import parse
EN={"Phyllium":"leaf insect","Phyllium giganteum":"leaf insect","Kallima inachus":"butterfly wings","Furcifer pardalis":"chameleon","Chamaeleo calyptratus":"chameleon","Trioceros jacksonii":"chameleon",
"Thaumoctopus mimicus":"octopus","Pterois volitans":"lionfish","Laticauda colubrina":"sea snake","Didelphis virginiana":"opossum","Didelphis marsupialis":"opossum","Eristalis tenax":"hoverfly","Vespula vulgaris":"wasp",
"Limenitis archippus":"butterfly","Danaus plexippus":"monarch butterfly","Myrmarachne":"jumping spider","Lampropeltis triangulum":"snake","Pavo cristatus":"peacock","Ptilonorhynchus violaceus":"bowerbird",
"Photinus pyralis":"fireflies","Pygoscelis papua":"penguin","Pelecanus occidentalis":"pelican","Mantis religiosa":"praying mantis","Pisaura mirabilis":"spider","Photuris":"fireflies","Sepia officinalis":"cuttlefish",
"Sepia apama":"cuttlefish","Lophius piscatorius":"anglerfish","Antennarius":"frogfish","Cuculus canorus":"cuckoo bird","Acrocephalus scirpaceus":"reed warbler bird feeding chick","Aptenodytes forsteri":"emperor penguin",
"Hippocampus":"seahorse","Crocodylus niloticus":"crocodile","Pipa pipa":"frog","Chelonia mydas":"sea turtle","Enteroctopus dofleini":"octopus","Cephalopoda":"octopus underwater","Melanocetus johnsonii":"deep sea",
"Teuthida":"squid","Lophiiformes":"deep sea fish","Myctophidae":"deep sea fish","Cnidaria":"jellyfish","Vampyroteuthis infernalis":"deep sea","Octopoda":"octopus","Architeuthis dux":"squid underwater","Osedax":"deep sea",
"Balaenoptera musculus":"whale underwater","Riftia pachyptila":"deep sea","Bathymodiolus":"deep sea","Alvinella pompejana":"deep sea","Siboglinidae":"deep sea","Vestimentifera":"deep sea",
"Corvus moneduloides":"crow","Corvus corax":"raven","Corvus macrorhynchos":"crow","Corvus brachyrhynchos":"crow","Octopus vulgaris":"octopus","Pan troglodytes":"chimpanzee","Tursiops truncatus":"dolphin",
"Loxodonta africana":"elephant","Pica pica":"magpie","Psittacus erithacus":"parrot","Odontodactylus scyllarus":"shrimp","Gonodactylus":"shrimp","Alpheus":"shrimp","Brachinus":"beetle","Tardigrada":"microscope",
"Turritopsis dohrnii":"jellyfish","Turritopsis":"jellyfish","Hydrozoa":"jellyfish","Electrophorus electricus":"electric eel","Electrophorus":"electric eel","Gymnotiformes":"eel","Atta cephalotes":"leafcutter ants",
"Apis mellifera":"honey bees","Eciton burchellii":"ants","Heterocephalus glaber":"mole rat","Bathyergidae":"mole rat","Fukomys":"mole rat","Canis lupus":"wolf","Suricata suricatta":"meerkat","Bradypus variegatus":"sloth",
"Choloepus hoffmanni":"sloth","Phascolarctos cinereus":"koala","Panthera leo":"lion","Formica rufa":"ants","Stercorarius skua":"seabird","Fregata magnificens":"frigatebird","Larus argentatus":"seagull",
"Aphelocoma californica":"jay bird","Acinonyx jubatus":"cheetah","Lycaon pictus":"wild dog","Anax imperator":"dragonfly","Orcinus orca":"orca","Falco peregrinus":"falcon","Falco eleonorae":"falcon","Aquila chrysaetos":"eagle",
"Vulpes vulpes":"fox","Megaptera novaeangliae":"humpback whale","Procyon lotor":"raccoon","Haliaeetus leucocephalus":"bald eagle","Gymnogyps californianus":"vulture","Panthera tigris":"tiger"}
PX=os.environ.get("PEXELS_API_KEY",""); PB=os.environ.get("PIXABAY_API_KEY","")
def get(url,**kw):
    for i in range(5):
        time.sleep(0.8)
        try: r=requests.get(url,timeout=60,**kw)
        except Exception: time.sleep(5); continue
        if r.status_code==429: time.sleep(40); continue
        return r
def pexels(q,n=8):
    r=get("https://api.pexels.com/videos/search",params=dict(query=q,per_page=n,orientation="landscape"),headers={"Authorization":PX})
    out=[]
    if r is None or r.status_code!=200: return out
    for v in r.json().get("videos",[]):
        if v["duration"]<5 or v["duration"]>40: continue
        fs=[f for f in v["video_files"] if f.get("file_type")=="video/mp4" and f.get("width") and 1000<=f["width"]<=1920]
        if not fs: continue
        f=sorted(fs,key=lambda f:abs(f["width"]-1280))[0]
        out.append(dict(src="Pexels",url=f["link"],page=v["url"],artist=v.get("user",{}).get("name",""),dur=v["duration"],lic="Pexels License",q=q))
    return out
def pixabay(q,n=8):
    r=get("https://pixabay.com/api/videos/",params=dict(key=PB,q=q,per_page=n,safesearch="true"))
    out=[]
    if r is None or r.status_code!=200: return out
    for h in r.json().get("hits",[]):
        if h["duration"]<5 or h["duration"]>40: continue
        v=h["videos"].get("medium") or h["videos"].get("large")
        if not v or not v.get("url"): continue
        out.append(dict(src="Pixabay",url=v["url"],page=h["pageURL"],artist=h.get("user",""),dur=h["duration"],lic="Pixabay License",q=q))
    return out
def fetch(c,outdir):
    fn=os.path.join(outdir,hashlib.md5(c["url"].encode()).hexdigest()[:12]+".mp4")
    if os.path.exists(fn): return fn
    r=get(c["url"],stream=False)
    if r is None or r.status_code!=200 or len(r.content)<100000: return None
    open(fn,"wb").write(r.content); return fn
if __name__=="__main__":
    ep=sys.argv[1]; per_scene=int(sys.argv[2]) if len(sys.argv)>2 else 8
    outdir=f"medya/b{ep}"; os.makedirs(outdir,exist_ok=True)
    man=[m for m in json.load(open(f"{outdir}/manifest.json")) if m["kind"]!="video"]
    plan=json.load(open(f"bolum{ep}_turler.json")); meta=json.load(open(f"bolum{ep}_meta.json")); used=set()
    for s in parse(ep):
        n=s["n"]
        if n==meta.get("scoreboard_scene"): continue
        qs=[]
        for name,_ in plan.get(str(n),[]):
            q=EN.get(name,name)
            if q not in qs: qs.append(q)
        if not qs: qs=["nature wildlife"]
        got=0
        for q in qs*2:
            if got>=per_scene: break
            cands=(pexels(q) if PX else [])+(pixabay(q) if PB else [])
            for c in cands:
                if got>=per_scene: break
                if c["url"] in used: continue
                f=fetch(c,outdir)
                if not f: continue
                used.add(c["url"]); got+=1
                man.append(dict(file=f,kind="video",scene=n,query=c["q"],title=f"{c['q']} ({c['src']})",lic=c["lic"],artist=c["artist"],page=c["page"],w=1280,h=720))
        print(f"B{ep} sahne {n}: {got} video ({', '.join(qs)})",flush=True)
    json.dump(man,open(f"{outdir}/manifest.json","w"),ensure_ascii=False,indent=1); print("toplam",len(man))
