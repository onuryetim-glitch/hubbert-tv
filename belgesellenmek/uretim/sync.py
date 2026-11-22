"""Cümle-senkron montaj yardımcıları: gerçek cümle zamanları (duraklamalardan), konu etiketleri, bilgi kartları."""
import re,subprocess,os
from PIL import Image,ImageDraw,ImageFont,ImageFilter
W,H=1280,720
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def split_sents(text): return [x.strip() for x in re.split(r"(?<=[.!?])\s+",text) if x.strip()]
def sentence_spans(text,wav,audio):
    sents=split_sents(text); N=len(sents); tot=max(1,sum(len(x) for x in sents))
    ideal=[]; c=0
    for x in sents[:-1]: c+=len(x); ideal.append(audio*c/tot)
    err=subprocess.run(["ffmpeg","-i",wav,"-af","silencedetect=noise=-32dB:d=0.12","-f","null","-"],capture_output=True,text=True).stderr
    st=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",err)]; en=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",err)]
    sil=[((a+b)/2,b-a) for a,b in zip(st,en) if a>0.3 and b<audio-0.25]
    bounds=[]; prev=0.2
    for T in ideal:
        cand=[(abs(m-T)-4*min(d,0.6),m) for m,d in sil if m>prev+0.4]
        best=min(cand) if cand else None
        if best and abs(best[1]-T)<=max(3.0,0.12*audio): bounds.append(best[1]); prev=best[1]
        else: bounds.append(max(T,prev+0.4)); prev=bounds[-1]
    spans=[]; p=0.0
    for b in bounds+[audio]: spans.append((p,b)); p=b
    return sents,spans
def anchor_t(text,anchor,sents,spans):
    i=text.find(anchor)
    return None if i<0 else time_at(text,i,sents,spans)
def time_at(text,i,sents,spans):
    pos=0
    for k,x in enumerate(sents):
        j=text.find(x,pos)
        if j<0: break
        if i<j+len(x): return spans[k][0]+(0.12 if i<=j+2 else 0.12+(spans[k][1]-spans[k][0])*(i-j)/max(1,len(x)))
        pos=j+len(x)
    return spans[-1][0]
def font(sz,b=True): return ImageFont.truetype(BOLD if b else REG,sz)
def card(path,title,lines=(),tag="BİLGİ",logo=False):
    im=Image.new("RGB",(W,H),(16,26,22)); d=ImageDraw.Draw(im)
    for y in range(H): d.line([(0,y),(W,y)],fill=(int(16+14*y/H),int(26+16*y/H),int(22+12*y/H)))
    # ince desen
    for k in range(0,W,64): d.line([(k,0),(k-200,H)],fill=(24,38,32),width=1)
    d.rectangle((90,170,98,560),fill=(255,200,40))
    d.text((130,170),tag,font=font(30),fill=(255,200,40))
    f=font(66); y=232
    words=title.split(); line=""; out=[]
    for w in words:
        if d.textlength((line+" "+w).strip(),font=f)<=1000: line=(line+" "+w).strip()
        else: out.append(line); line=w
    out.append(line)
    for l in out[:3]: d.text((130,y),l,font=f,fill=(255,255,255)); y+=82
    y+=14
    for l in lines[:4]: d.text((130,y),l,font=font(38,False),fill=(255,200,40)); y+=54
    if logo and os.path.exists("assets/kanal_logo.png"):
        lg=Image.open("assets/kanal_logo.png").convert("RGBA").resize((300,300),Image.LANCZOS); im.paste(lg,(W-400,H//2-150),lg)
    im.save(path)
