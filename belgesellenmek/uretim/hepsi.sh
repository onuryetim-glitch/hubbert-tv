#!/bin/bash
cd "$(dirname "$0")"
EPS="02 03 04 05 06 07 08 09 10"
( for e in $EPS; do python3 tts_piper.py $e > tts$e.log 2>&1; echo "TTS $e bitti" >> hat.log; done ) &
( for e in $EPS; do python3 -u inat.py $e > inat$e.log 2>&1; echo "FOTO $e bitti" >> hat.log; done ) &
build() { for e in "$@"; do
  while [ ! -f medya/b$e/manifest.json ] || [ $(ls ses/b$e/*.wav 2>/dev/null | wc -l) -lt $(python3 -c "from sahneler import parse;print(len(parse('$e')))") ] || ! grep -q "TTS $e bitti" hat.log; do sleep 10; done
  python3 -u build.py $e > build$e.log 2>&1 && echo "BÖLÜM $e HAZIR" >> hat.log || echo "BÖLÜM $e HATA" >> hat.log
done; }
build 02 04 06 08 10 &
build 03 05 07 09 &
wait
echo "HEPSİ BİTTİ" >> hat.log
