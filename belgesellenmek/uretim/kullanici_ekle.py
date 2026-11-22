"""medya_kullanici/bNN/sNN_*.mp4 dosyalarını bölümün manifestine VİDEO olarak ekler."""
import sys,os,re,json,glob
ep=sys.argv[1]; mf=f"medya/b{ep}/manifest.json"
man=[m for m in json.load(open(mf)) if m.get("kaynak")!="kullanici"]
n=0
for f in sorted(glob.glob(f"medya_kullanici/b{ep}/s*_*.mp4")):
    m=re.match(r"s(\d+)_",os.path.basename(f))
    if not m: continue
    man.append(dict(file=f,kind="video",scene=int(m.group(1)),query="kullanici",title="Stok video",lic="Pexels/Pixabay License",artist="",page="medya_kullanici/kaynaklar.txt",w=1280,h=720,kaynak="kullanici")); n+=1
json.dump(man,open(mf,"w"),ensure_ascii=False,indent=1); print(f"B{ep}: {n} kullanıcı klibi eklendi")
