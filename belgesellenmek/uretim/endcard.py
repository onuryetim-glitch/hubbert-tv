"""Kapanış ekranı animasyonu: kanal logosu + yorum/beğen/abone ol/zil + sıradaki bölüm kartı. PNG dizisi (RGBA) üretir."""
import os,math,shutil,random
from PIL import Image,ImageDraw,ImageFont
W,H,FPS=1280,720,30
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; EM="/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
GOLD=(255,200,40); RED=(220,38,38)
def font(sz,b=True): return ImageFont.truetype(B if b else R,sz)
_emo={}
def emoji(ch,size):
    k=(ch,size)
    if k not in _emo:
        f=ImageFont.truetype(EM,109); im=Image.new("RGBA",(136,128),(0,0,0,0)); ImageDraw.Draw(im).text((0,0),ch,font=f,embedded_color=True)
        im=im.crop(im.getbbox()); r=size/max(im.size); _emo[k]=im.resize((max(1,int(im.width*r)),max(1,int(im.height*r))),Image.LANCZOS)
    return _emo[k]
def eo(x): x=min(1,max(0,x)); c1=1.70158; c3=c1+1; return 1+c3*pow(x-1,3)+c1*pow(x-1,2)   # ease-out-back
def paste_c(cv,im,cx,cy,scale=1.0,alpha=1.0,rot=0):
    if scale<=0.01 or alpha<=0: return
    if scale!=1.0: im=im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.LANCZOS)
    if rot: im=im.rotate(rot,resample=Image.BICUBIC,expand=True)
    if alpha<1: a=im.split()[3].point(lambda p:int(p*alpha)); im=im.copy(); im.putalpha(a)
    cv.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2)))
def pill(cv,box,fill,r=22):
    d=ImageDraw.Draw(cv); d.rounded_rectangle(box,r,fill=fill)
def text(cv,xy,t,sz,fill,b=True,anchor="la",alpha=1.0):
    layer=Image.new("RGBA",cv.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    f=font(sz,b); d.text((xy[0]+2,xy[1]+2),t,font=f,fill=(0,0,0,int(160*alpha)),anchor=anchor); d.text(xy,t,font=f,fill=fill+(int(255*alpha),),anchor=anchor)
    cv.alpha_composite(layer)
def cursor(cv,x,y,s=1.0,press=False):
    d=ImageDraw.Draw(cv); k=s*(0.9 if press else 1.0)
    pts=[(0,0),(0,34),(9,26),(15,40),(22,37),(16,24),(28,24)]
    pts=[(x+px*k*1.3,y+py*k*1.3) for px,py in pts]; d.polygon(pts,fill=(255,255,255,255),outline=(0,0,0,255))
def anim(ep,text_,L,sp,next_title,next_when,final=False,ayrac="",tfun=None):
    """Dönen: (png_desen, baslangic_sn, sfx_olaylari[(sn,dosya,vol)])"""
    def at(word,default):
        if tfun: return tfun(word,default)
        i=text_.lower().find(word); return default if i<0 else 0.3+(L-0.8)*i/max(1,len(text_))
    tc=at("yorum",L-18); tl=at("beğen",L-15); ts=at("abone",L-12); tn=at("sıradaki",L-7)
    t_start=max(0.0,min(tc,tl,ts)-0.7); t_start=min(t_start,max(0,L-9))
    n=int((L-t_start)*FPS); d=f"{sp}_end"; shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
    logo=Image.open("assets/kanal_logo.png").convert("RGBA").resize((330,330),Image.LANCZOS)
    ev=[(t_start+0.1,"sfx_whoosh_in.wav",0.5),(tc,"sfx_pop.wav",0.7),(tl,"sfx_begen.wav",0.7),(tl+0.35,"sfx_pop.wav",0.45),
        (ts,"sfx_whoosh_in.wav",0.45),(ts+0.95,"sfx_tik.wav",0.9),(ts+1.25,"sfx_zil.wav",0.8),(tn,"sfx_whoosh_in.wav",0.5),(tn+0.35,"sfx_ding.wav",0.7)]
    rnd=random.Random(5); PART=[(rnd.uniform(-1,1),rnd.uniform(-1.6,-0.4),rnd.choice([(255,200,40),(220,38,38),(120,230,140),(90,170,255),(255,255,255)]),rnd.uniform(5,11),rnd.uniform(0,6.28)) for _ in range(90)]
    ev.append((ts+0.98,'sfx_ding.wav',0.4))
    for i in range(n):
        t=t_start+i/FPS; cv=Image.new("RGBA",(W,H),(0,0,0,0)); dd=ImageDraw.Draw(cv)
        dim=min(1,(t-t_start)/0.6)*0.58; cv.alpha_composite(Image.new("RGBA",(W,H),(0,0,0,int(255*dim))))
        # logo
        lt=t-t_start; sc=eo(lt/0.7); paste_c(cv,logo,230,300+4*math.sin(t*2.2),scale=sc)
        # satır A: yorum
        if t>=tc:
            u=t-tc; s_=eo(u/0.4); paste_c(cv,emoji("💬",96),590,150,scale=s_)
            text(cv,(660,118),"YORUM YAP",46,(255,255,255),alpha=min(1,u/0.3))
            text(cv,(660,172),"Seni en çok ne şaşırttı?",28,GOLD,b=False,alpha=min(1,max(0,(u-0.2)/0.3)))
            for k in range(3):
                a=0.35+0.65*max(0,math.sin((u*3.2)-k*0.9)); dd.ellipse((1088+k*26,150,1088+k*26+14,164),fill=(255,200,40,int(255*a)))
        # satır B: beğen
        if t>=tl:
            u=t-tl; pulse=1+0.28*math.exp(-((u-0.3)/0.18)**2)
            paste_c(cv,emoji("👍",96),590,300,scale=eo(u/0.4)*pulse)
            text(cv,(660,268),"BEĞEN",46,(255,255,255),alpha=min(1,u/0.3))
            if u>0.35:
                v=u-0.35; text(cv,(920,262-int(46*min(1,v/0.9))),"+1",40,(120,230,140),alpha=max(0,1-v/1.1))
        # satır C: abone ol + zil
        if t>=ts:
            u=t-ts; slide=1-eo(u/0.45); off=int(260*slide)
            clicked=u>=0.95
            box=(520-off,396,860-off,486); pill(cv,box,(74,74,74,255) if clicked else RED+(255,),r=44)
            text(cv,((box[0]+box[2])//2,(box[1]+box[3])//2),"ABONE OLUNDU" if clicked else "ABONE OL",38 if clicked else 42,(255,255,255),anchor="mm")
            if 0.95<=u<1.3: 
                rr=int(70*(u-0.95)/0.35); dd.ellipse((690-rr,441-rr,690+rr,441+rr),outline=(255,255,255,int(200*(1-(u-0.95)/0.35))),width=4)
            if u<1.0:
                p=min(1,max(0,(u-0.15)/0.8)); cx=1150+(690-1150)*eo(p) if p<1 else 690; cy=600+(450-600)*p
                cursor(cv,cx,cy,press=u>0.88)
            if 0.95<=u<3.0:
                for vx,vy,col,sz,ph in PART:
                    q=u-0.95; px=690+vx*420*q; py=441+vy*380*q+520*q*q; a=int(255*max(0,1-q/2.0))
                    if a>0: dd.rectangle((px,py,px+sz,py+sz*0.6),fill=col+(a,))
            if u>=1.9:
                text(cv,(930,502),"ZİLİ AÇ",26,GOLD,anchor="mm",alpha=min(1,(u-1.9)/0.4)); text(cv,(930,532),"tüm bildirimler",20,(255,255,255),b=False,anchor="mm",alpha=min(1,(u-1.9)/0.4))
            if u>=1.15:
                v=u-1.15; rot=26*math.exp(-1.1*v)*math.sin(v*13)
                bell=emoji("🔔",92); paste_c(cv,bell,930,441,scale=eo(v/0.35),rot=rot)
                if v<2.6:
                    for k in (1,2): 
                        a=int(200*max(0,math.sin(v*9+k))*(1-v/2.6)); 
                        if a>0: dd.arc((930-62-k*14,441-62-k*14,930+62+k*14,441+62+k*14),200,250,fill=(255,200,40,a),width=4); dd.arc((930-62-k*14,441-62-k*14,930+62+k*14,441+62+k*14),290,340,fill=(255,200,40,a),width=4)
        # alt kart: sıradaki bölüm (iki satır: başlık + teaser)
        if t>=tn:
            u=t-tn; y=int(572+170*(1-eo(u/0.5))); pill(cv,(60,y,1220,y+132),(18,16,14,222),r=26)
            dd.rounded_rectangle((60,y,1220,y+132),26,outline=(201,150,62,255),width=3)
            if final:
                text(cv,(100,y+12),"SERİ FİNALİ",22,GOLD); text(cv,(100,y+40),"İzlediğin için teşekkürler!",38,(255,255,255)); text(cv,(100,y+86),"2. Sezon yakında",32,GOLD)
            else:
                text(cv,(100,y+12),"SIRADAKİ BÖLÜM",22,GOLD); text(cv,(100,y+40),next_title[:46],38,(255,255,255)); text(cv,(100,y+86),next_when[:max(0,int((u-0.45)*26))][:60]+("▌" if int(u*3)%2==0 and (u-0.45)*26<len(next_when) else ""),32,GOLD)
        cv.save(f"{d}/f_{i:04d}.png")
    return f"{d}/f_%04d.png",t_start,ev
