import time,os
from supertonic import TTS
t=time.time(); tts=TTS(auto_download=True); print("model yüklendi",round(time.time()-t,1),"sn",flush=True)
txt="Şu görüntüye bakın. Bir yaprak. Çok sıradan, çok kuru, çok yaprak gibi. Bir saniye… yaprak yürüdü. Kanalımıza hoş geldiniz. Doğa adil değildir, ama komiktir."
os.makedirs("ses_numune",exist_ok=True)
for v in ("M1","M2","M3","M4","M5","F1","F2","F3","F4","F5"):
    t=time.time(); style=tts.get_voice_style(voice_name=v)
    wav,dur=tts.synthesize(txt,voice_style=style,lang="tr"); tts.save_audio(wav,f"ses_numune/{v}.wav")
    print(v,round(float(dur),1),"sn ses,",round(time.time()-t,1),"sn sürdü",flush=True)
