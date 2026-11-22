"""Supertonic 3 (M5) ile bölüm seslendirmesi: cümle cümle + duraklama + loudnorm. Çıktı: ses_tm/bNN/sN.wav"""
import sys,os,re,subprocess,wave,numpy as np
from supertonic import TTS
from sahneler import parse
import sync
VOICE=os.environ.get("SES","M5"); SPEED=float(os.environ.get("HIZ","1.05")); STEPS=int(os.environ.get("ADIM","10"))
tts=TTS(auto_download=True); style=tts.get_voice_style(voice_name=VOICE)
def pause(x): return 0.38 if x.endswith("?") else (0.30 if x.endswith("!") else 0.24)
def one(sent):
    w,d=tts.synthesize(sent,voice_style=style,lang="tr",speed=SPEED,total_steps=STEPS,silence_duration=0.25)
    return np.asarray(w).reshape(-1).astype(np.float32)
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
