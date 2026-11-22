"""Geliştirilmiş Piper seslendirme: cümle bazlı tonlama + duraklama + stüdyo mastering. Çıktı: ses2/bNN/sN.wav"""
import sys,os,re,wave,subprocess,numpy as np
from piper import PiperVoice, SynthesisConfig
from sahneler import parse
VOICE=PiperVoice.load("ses/tr.onnx"); SR=VOICE.config.sample_rate
def synth(text,ls,ns,nw):
    cfg=SynthesisConfig(length_scale=ls,noise_scale=ns,noise_w_scale=nw)
    chunks=[]
    for ch in VOICE.synthesize(text,syn_config=cfg): chunks.append(ch.audio_int16_array)
    return np.concatenate(chunks) if chunks else np.zeros(0,dtype=np.int16)
def sil(sec): return np.zeros(int(SR*sec),dtype=np.int16)
def prosody(sent):
    n=len(sent)
    if sent.endswith("?"): return 0.90,0.78,0.95,0.40
    if sent.endswith("!"): return 0.86,0.80,0.95,0.32
    ls=0.93 if n<38 else (0.82 if n>120 else 0.87)
    return ls,0.78,0.95,(0.28 if sent.endswith(".") else 0.38)
def master(src,dst):
    af=("highpass=f=75,equalizer=f=170:t=q:w=1:g=2.2,equalizer=f=3000:t=q:w=1.2:g=2.0,equalizer=f=6800:t=q:w=2:g=-3.5,"
        "acompressor=threshold=0.1:ratio=3:attack=8:release=140:makeup=2.5,"
        "aecho=0.88:0.42:55|105:0.12|0.07,"
        "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=44100")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-af",af,"-ac","1",dst],check=True)
if __name__=="__main__":
    ep=sys.argv[1]; only=set(map(int,sys.argv[2].split(","))) if len(sys.argv)>2 else None
    out=f"ses2/b{ep}"; os.makedirs(out,exist_ok=True)
    for s in parse(ep):
        if only and s["n"] not in only: continue
        text=re.sub(r"\s+"," ",s["text"]).replace("…","...")
        sents=[x.strip() for x in re.split(r"(?<=[.!?])\s+",text) if x.strip()]
        parts=[sil(0.15)]
        for x in sents:
            ls,ns,nw,pause=prosody(x)
            parts+= [synth(x,ls,ns,nw),sil(pause)]
        raw=f"{out}/s{s['n']}_ham.wav"
        w=wave.open(raw,"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.concatenate(parts).tobytes()); w.close()
        master(raw,f"{out}/s{s['n']}.wav"); os.remove(raw)
        print("sahne",s["n"],flush=True)
