import sys,os,re,subprocess,wave
from sahneler import parse
ep=sys.argv[1]; os.makedirs(f"ses/b{ep}",exist_ok=True)
for s in parse(ep):
    out=f"ses/b{ep}/s{s['n']}.wav"
    if os.path.exists(out): continue
    txt=re.sub(r"\s+"," ",s["text"]).replace("…","...")
    subprocess.run(["python3","-m","piper","-m","ses/tr.onnx","-f",out,"--sentence-silence","0.22","--length-scale","0.86"],input=txt.encode(),check=True,capture_output=True)
    w=wave.open(out); print("sahne",s["n"],round(w.getnframes()/w.getframerate(),1),"sn",flush=True)
