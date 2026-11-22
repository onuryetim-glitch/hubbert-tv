import time,commons
t0=time.time()
while time.time()-t0<3300:
    h=commons.S.get("https://upload.wikimedia.org/wikipedia/commons/b/bd/Mimic_Octopus2.jpg",stream=True,timeout=30)
    ra=int(h.headers.get("retry-after","0") or 0)
    print(round((time.time()-t0)/60),"dk:",h.status_code,ra,flush=True)
    if h.status_code==200: print("ACIK",flush=True); break
    time.sleep(max(ra,300)+10)
