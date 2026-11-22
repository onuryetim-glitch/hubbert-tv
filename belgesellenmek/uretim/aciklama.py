import json,re,sys,wave,shutil
from sahneler import parse
NEXT={1:"Aşk ve Savaş",2:"Kötü ve Harika Ebeveynler",3:"Okyanusun Karanlık Köşeleri",4:"Akıllı Mı Dediniz?",5:"Süper Güçler",6:"Sosyal Hayat",7:"Tembeller, Hırsızlar ve Şeytani Zekâlar",8:"Avcı mı Av Mı?",9:"Gezegenin Mirası"}
for e in range(int(sys.argv[1]),int(sys.argv[2])+1):
    ep=f"{e:02d}"; src=open(f"../senaryolar/bolum{ep}.md",encoding="utf-8").read(); meta=json.load(open(f"bolum{ep}_meta.json")); man=json.load(open(f"medya/b{ep}/manifest.json"))
    def sec(pat):
        m=re.search(r"^##\s+[^\n]*(?:"+pat+r")[^\n]*\n(.*?)(?=^##\s|^---)",src,re.S|re.M|re.I); return m.group(1) if m else ""
    tt=re.findall(r"^\d\.\s+(.+)$",sec("başlı"),re.M)
    desc=sec("açıklama").strip()
    desc=re.split(r"\n\s*(?:Bölümler:|Serinin yayın|Seri finali|Kaynak türleri|⏱️|Bölüm işaretleri|Sıradaki bölüm|Serinin sıradaki)",desc)[0].strip()
    tags=sec("etiket").strip()
    t=0; ch=[]
    for s in parse(ep):
        w=wave.open(f"ses/b{ep}/s{s['n']}.wav"); L=w.getnframes()/w.getframerate()+0.6
        n=s["n"]; ttl=meta["titles"].get(str(n),"")
        if not ttl:
            ttl="Puan Tablosu" if n==meta["scoreboard_scene"] else ("Soğuk açılış" if n==1 else ("Önceki bölümde" if re.search("önceki",s["title"].lower()) else ("Veda" if e==10 and n==meta.get("cta_scene") else "Sıradaki bölüm")))
        ch.append(f"{int(t//60):02}:{int(t%60):02} {ttl}"); t+=L
    seen=set(); cred=[]
    for m in man:
        if m["page"] in seen: continue
        seen.add(m["page"]); cred.append(f"- {m['title']} — {m['artist'] or 'iNaturalist kullanıcısı'} — {m['lic']} — {m['page']}")
    nxt=(f"Serinin sıradaki bölümü: Bölüm {e+1} — {NEXT[e]}." if e<10 else "Seri finali. 2. Sezon yakında!")
    out=f"BAŞLIK (öneri): {(tt[0] if tt else '').split(' | ')[0]} | Doğa Adil Değildir #{e}\nAlternatifler: {' | '.join(tt[1:])}\n\nAÇIKLAMA\n{desc}\n\n{nxt}\n\n▶ Tüm seri (Doğa Adil Değildir oynatma listesi): [PLAYLIST_LINKI]\n\nBÖLÜMLER\n"+"\n".join(ch)+f"\n\nETİKETLER\n{tags}\n\nGÖRSEL KAYNAKLARI (iNaturalist, Creative Commons — atıf zorunlu)\n"+"\n".join(cred)+"\n\nSeslendirme: yapay zekâ sesi (Piper TTS). Videodaki fotoğraflar yukarıdaki lisanslarla kullanılmıştır.\n"
    open(f"../yayin/bolum{ep}_youtube.txt","w",encoding="utf-8").write(out); shutil.copy(f"cikti/bolum{ep}.srt",f"../yayin/bolum{ep}.srt")
    print(ep,"başlık:",(tt[0] if tt else "YOK")[:60],"| açıklama",len(desc),"| etiket",len(tags.split(",")),"| atıf",len(cred))
