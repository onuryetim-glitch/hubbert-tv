"""Supertonic 3 (M5) ile bölüm seslendirmesi: cümle cümle + duraklama + loudnorm. Çıktı: ses_tm/bNN/sN.wav"""
import sys,os,re,subprocess,wave,numpy as np
from supertonic import TTS
from sahneler import parse
import sync
VOICE=os.environ.get("SES","M5"); SPEED=float(os.environ.get("HIZ","1.05")); STEPS=int(os.environ.get("ADIM","10"))
tts=TTS(auto_download=True); style=tts.get_voice_style(voice_name=VOICE)
def pause(x): return 0.38 if x.endswith("?") else (0.30 if x.endswith("!") else 0.24)
_wh=None
def _norm(t):
    t=t.replace("İ","i").replace("I","ı").lower(); return re.findall(r"[a-zçğıöşü0-9]+",t)
def _skor(sent,a,sr):
    """Cümleyi Whisper ile geri okur; son kelime kesildi mi / kelimeler eksik mi bakar. 0..1"""
    global _wh
    if _wh is None:
        from faster_whisper import WhisperModel; _wh=WhisperModel("small",device="cpu",compute_type="int8")
    x=np.interp(np.arange(0,len(a)*16000/sr)*sr/16000,np.arange(len(a)),a).astype(np.float32)
    seg,_=_wh.transcribe(x,language="tr",beam_size=5)
    h=_norm(" ".join(g.text for g in seg)); r=_norm(sent)
    import difflib
    son=r[-1] if r else ""
    if not son or len(r)<=2 or any(c.isdigit() for c in son) or not h: return 1.0
    sl=difflib.SequenceMatcher(None,son,h[-1]).ratio()
    tum=difflib.SequenceMatcher(None,r,h,autojunk=False).ratio()
    return min(sl,tum+0.1)
def one(sent):
    sr=getattr(tts,"sample_rate",44100); best=None
    for hiz,adim in ((SPEED,STEPS),(SPEED,20),(SPEED-0.07,20),(SPEED-0.12,20),(SPEED-0.2,20)):
        w,d=tts.synthesize(sent,voice_style=style,lang="tr",speed=hiz,total_steps=adim,silence_duration=0.25)
        a=np.asarray(w).reshape(-1).astype(np.float32)
        sk=_skor(sent,a,sr) if os.environ.get("DOGRULA","1")=="1" else 1.0
        if best is None or sk>best[0]: best=(sk,a)
        if sk>=0.8: break
    if best[0]<0.8: print("  ZAYIF:",round(best[0],2),sent[:60],flush=True)
    return best[1]
def scene(text):
    sents=sync.split_sents(re.sub(r"\s+"," ",text).replace("…","..."))
    sr=getattr(tts,"sample_rate",44100); parts=[np.zeros(int(sr*0.15),dtype=np.float32)]
    for x in sents:
        parts+= [one(x),np.zeros(int(sr*pause(x)),dtype=np.float32)]
    return np.concatenate(parts),sr
if __name__=="__main__":
    ep=sys.argv[1]; only=set(map(int,sys.argv[2].split(","))) if len(sys.argv)>2 else None
    out=f"ses_tm/b{ep}"; os.makedirs(out,exist_ok=True)
    for s in parse(ep):
        if only and s["n"] not in only: continue
        a,sr=scene(s["text"]); raw=f"{out}/s{s['n']}_ham.wav"
        w=wave.open(raw,"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(a,-1,1)*32767).astype(np.int16).tobytes()); w.close()
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",raw,"-af","highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=9,aresample=44100","-ac","1",f"{out}/s{s['n']}.wav"],check=True); os.remove(raw)
        print("sahne",s["n"],round(len(a)/sr,1),"sn",flush=True)
