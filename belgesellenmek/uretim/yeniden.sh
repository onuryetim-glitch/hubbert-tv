#!/bin/bash
cd "$(dirname "$0")"
w() { for e in "$@"; do python3 -u build.py $e > build$e.log 2>&1 && echo "B$e hazır" >> yeniden.log || echo "B$e HATA" >> yeniden.log; done; }
w 01 03 05 07 09 &
w 02 04 06 08 10 &
wait; python3 aciklama.py 1 10 >> yeniden.log 2>&1; echo "HEPSİ BİTTİ" >> yeniden.log
