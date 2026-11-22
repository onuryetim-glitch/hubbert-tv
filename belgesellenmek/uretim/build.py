import sys,os,re,json,wave,subprocess,random
from PIL import Image,ImageDraw,ImageFont
from sahneler import parse
ep=sys.argv[1]; W,H,FPS=1280,720,30
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
D=f"klipler/b{ep}"; os.makedirs(D,exist_ok=True); os.makedirs("cikti",exist_ok=True)
man=json.load(open(f"medya/b{ep}/manifest.json"))
META=json.load(open(f"bolum{ep}_meta.json"))
def run(*a):
    r=subprocess.run(a,capture_output=True,text=True)
    if r.returncode: raise RuntimeError(" ".join(a[:6])+"\n"+r.stderr[-600:])
def dur(p):
    if p.endswith(".wav"):
        w=wave.open(p); return w.getnframes()/w.getframerate()
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]))
def font(sz,b=True): return ImageFont.truetype(BOLD if b else REG,sz)
def wrap(d,t,f,mx):
    out,cur=[],""
    for w in t.split():
        if d.textlength((cur+" "+w).strip(),font=f)<=mx: cur=(cur+" "+w).strip()
        else: out.append(cur); cur=w
    return out+[cur]
def card(path,lines,bg=(18,28,24),sub=None,size=64,accent=(255,200,40)):
    im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    for y in range(H): d.line([(0,y),(W,y)],fill=tuple(int(c*(0.55+0.45*y/H)) for c in bg))
    y=H//2-len(lines)*size//2-(30 if sub else 0)
    for l in lines:
        f=font(size); d.text(((W-d.textlength(l,font=f))/2,y),l,font=f,fill=(255,255,255)); y+=int(size*1.25)
    if sub:
        for l in wrap(d,sub,font(34,False),W-200):
            f=font(34,False); d.text(((W-d.textlength(l,font=f))/2,y+10),l,font=f,fill=accent); y+=46
    im.save(path)
def seg_image(img,out,secs,k):
    fr=int(secs*FPS); z0,z1=(1.0,1.18) if k%2==0 else (1.18,1.0)
    expr=f"{z0}+({z1}-{z0})*on/{fr}"
    run("ffmpeg","-y","-loglevel","error","-i",img,"-vf",
        f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,zoompan=z='{expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={fr}:s={W}x{H}:fps={FPS},format=yuv420p",
        "-t",str(secs),"-an","-c:v","libx264","-preset","veryfast","-crf","23",out)
def seg_video(src,out,secs,k,rep=0):
    d=dur(src); ss=min(0.5+rep*(secs+0.5),max(0,d-secs-0.1)) if d>secs+1.5 else 0
    run("ffmpeg","-y","-loglevel","error","-stream_loop","-1","-ss",str(ss),"-i",src,"-t",str(secs),"-vf",
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","23",out)
def tabledraw(path,rows,n):
    im=Image.new("RGB",(W,H),(14,22,20)); d=ImageDraw.Draw(im)
    d.text((60,36),"PUAN TABLOSU",font=font(54),fill=(255,200,40))
    d.text((60,100),"Hayatta kalma puanı (10 üzerinden)",font=font(26,False),fill=(190,200,195))
    y=170; step=min(72,(690-170)//max(1,len(rows)))
    for i,(name,pt) in enumerate(rows):
        if i>=n: break
        d.text((60,y),name,font=font(34),fill=(255,255,255))
        d.rounded_rectangle((520,y+6,520+60*10,y+40),8,outline=(90,110,100),width=2)
        d.rounded_rectangle((520,y+6,520+60*pt,y+40),8,fill=(255,200,40) if pt>=8 else (120,200,140))
        d.text((1160,y),f"{pt}",font=font(34),fill=(255,255,255)); y+=step
    im.save(path)
scenes=parse(ep); parts=[]; srt=[]; t0=0.0; random.seed(7)
def hms(t): h=int(t//3600);m=int(t%3600//60);s=t%60; return f"{h:02}:{m:02}:{s:06.3f}".replace(".",",")
for s in scenes:
    n=s["n"]; a=f"ses/b{ep}/s{n}.wav"; L=dur(a)+0.6
    sp=f"{D}/s{n}"
    if os.path.exists(f"{sp}.mp4") and str(n) not in os.environ.get("FORCE","").split(","):
        parts.append(f"{sp}.mp4")
        sents=[x.strip() for x in re.split(r"(?<=[.!?…])\s+",s["text"]) if x.strip()]; tc=sum(len(x) for x in sents); tt=t0+0.1; span=L-0.8
        for x in sents:
            d_=span*len(x)/tc; srt.append((tt,tt+d_,x)); tt+=d_
        t0+=L; print("sahne",n,"önbellekten",flush=True); continue
    segs=[]; media=[m for m in man if m["scene"]==n]
    vids=[m for m in media if m["kind"]=="video"]; imgs=[m for m in media if m["kind"]=="image"]
    order=[]
    vi=ii=0
    while len(order)<60 and (vids or imgs):
        for _ in range(3 if vids else 0):
            order.append(dict(vids[vi%len(vids)],_k=vi)); vi+=1
        if imgs: order.append(imgs[ii%len(imgs)]); ii+=1
        if not vids and len(order)>=len(imgs)*4: break
    sp=f"{D}/s{n}"
    if n==META["scoreboard_scene"]:
        rows=META["scores"]; k=len(rows); per=L/(k+1)
        for i in range(k+1):
            p=f"{sp}_t{i}.png"; tabledraw(p,rows,i); run("ffmpeg","-y","-loglevel","error","-loop","1","-i",p,"-t",f"{per:.3f}","-vf","fps=30,format=yuv420p","-c:v","libx264","-preset","veryfast",f"{sp}_t{i}.mp4"); segs.append(f"{sp}_t{i}.mp4")
    elif not order:
        p=f"{sp}_c.png"; card(p,[s["title"]]); seg_image(p,f"{sp}_c.mp4",L,0); segs=[f"{sp}_c.mp4"]
    else:
        tot,i=0.0,0
        while tot<L-0.05:
            m=order[i%len(order)]; secs=min(7.0 if m["kind"]=="video" else 6.0,L-tot)
            if L-tot-secs<2.0: secs=L-tot
            o=f"{sp}_{i}.mp4"
            (seg_video(m["file"],o,secs,i,m.get("_k",0)//max(1,len(vids))) if m["kind"]=="video" else seg_image(m["file"],o,secs,i)); segs.append(o); tot+=secs; i+=1
    lst=f"{sp}_list.txt"; open(lst,"w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in segs))
    raw=f"{sp}_raw.mp4"; run("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-c","copy",raw)
    ttl=META["titles"].get(str(n),s["title"]); tf=f"{sp}_title.txt"; open(tf,"w",encoding="utf-8").write(ttl)
    ov=f"drawbox=x=0:y=ih-150:w=iw:h=80:color=black@0.55:t=fill:enable='between(t,0.5,4.5)',drawtext=fontfile={BOLD}:textfile={tf}:fontsize=40:fontcolor=white:x=60:y=h-130:enable='between(t,0.5,4.5)'" if n not in META["no_title"] else "null"
    if n==META.get("cta_scene"):
        c=META["cta"]; fs=[]
        for j,(txt,sz,col,y) in enumerate(c):
            fn=f"{sp}_cta{j}.txt"; open(fn,"w",encoding="utf-8").write(txt); fs.append(f"drawtext=fontfile={BOLD}:textfile={fn}:fontsize={sz}:fontcolor={col}:x=(w-text_w)/2:y={y}:enable='gte(t,3)'")
        ov="drawbox=x=140:y=170:w=1000:h=380:color=black@0.62:t=fill:enable='gte(t,3)',"+",".join(fs)
    ov=ov+f",drawtext=fontfile={BOLD}:text='DOĞA ADİL DEĞİLDİR  •  {int(ep)}/10':fontsize=22:fontcolor=white@0.75:x=w-text_w-28:y=22:shadowcolor=black@0.6:shadowx=1:shadowy=1" if ov!="null" else f"drawtext=fontfile={BOLD}:text='DOĞA ADİL DEĞİLDİR  •  {int(ep)}/10':fontsize=22:fontcolor=white@0.75:x=w-text_w-28:y=22:shadowcolor=black@0.6:shadowx=1:shadowy=1"
    out=f"{sp}.mp4"; run("ffmpeg","-y","-loglevel","error","-i",raw,"-i",a,"-vf",ov,"-af","apad=pad_dur=1,aresample=44100","-t",f"{L:.3f}","-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","160k","-ar","44100",out)
    parts.append(out)
    # altyazı: cümleleri karakter oranıyla dağıt
    sents=[x.strip() for x in re.split(r"(?<=[.!?…])\s+",s["text"]) if x.strip()]; tc=sum(len(x) for x in sents); tt=t0+0.1; span=L-0.8
    for x in sents:
        d_=span*len(x)/tc; srt.append((tt,tt+d_,x)); tt+=d_
    t0+=L; print("sahne",n,round(L,1),"sn",len(segs),"klip",flush=True)
open(f"cikti/bolum{ep}.srt","w",encoding="utf-8").write("".join(f"{i+1}\n{hms(a)} --> {hms(b)}\n{x}\n\n" for i,(a,b,x) in enumerate(srt)))
lst=f"{D}/final_list.txt"; open(lst,"w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in parts))
# fon müziği (geçici, sentezlenmiş) + birleştirme
total=sum(dur(p) for p in parts)
run("ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-f","lavfi","-i",f"sine=f=110:d={total},sine=f=165:d={total}"[:0] or f"aevalsrc=0.5*sin(2*PI*110*t)+0.35*sin(2*PI*165*t)+0.25*sin(2*PI*220.5*t):s=44100:d={total}",
    "-filter_complex","[1:a]lowpass=f=400,tremolo=f=0.18:d=0.4,volume=0.045[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]","-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k",f"cikti/bolum{ep}.mp4")
print("TAMAM",round(total/60,2),"dk")
