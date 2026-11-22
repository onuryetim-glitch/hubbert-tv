"""Seslendirme kontrolü: Whisper ile her sahneyi yazıya çevirir, senaryoyla karşılaştırır; eksik/yanlış kelimeleri listeler."""
import sys,re,os,subprocess,difflib,numpy as np
from faster_whisper import WhisperModel
from sahneler import parse
m=WhisperModel("small",device="cpu",compute_type="int8")
def norm(t):
    t=t.replace("İ","i").replace("I","ı").lower()
    return re.findall(r"[a-zçğıöşü0-9]+",t)
def pcm(p):
    r=subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True,check=True).stdout
    return np.frombuffer(r,dtype=np.float32)
ep=sys.argv[1]; only=set(map(int,sys.argv[2].split(","))) if len(sys.argv)>2 else None
tot=bad=0
for s in parse(ep):
    if only and s["n"] not in only: continue
    f=f"ses_tm/b{ep}/s{s['n']}.wav"
    if not os.path.exists(f): continue
    seg,_=m.transcribe(pcm(f),language="tr",beam_size=5)
    h=norm(" ".join(x.text for x in seg)); r=norm(s["text"])
    sm=difflib.SequenceMatcher(None,r,h,autojunk=False); 
    for op,a,b,c,d in sm.get_opcodes():
        if op!="equal":
            tot+=1
            ra=" ".join(r[a:b]); hb=" ".join(h[c:d])
            # sayıları/ufak yazım farklarını yok say
            if difflib.SequenceMatcher(None,ra,hb).ratio()<0.75: bad+=1; print(f"s{s['n']}: '{ra}' -> '{hb}'")
    print(f"sahne {s['n']} oran {sm.ratio():.3f}",flush=True)
print("şüpheli:",bad)
