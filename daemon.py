#!/usr/bin/env python3
"""Attention daemon — polls PLATO rooms, computes salience, reports most salient gap."""
import json, urllib.request, time, math, os

PLATO = "http://localhost:8847"
AESOP = "http://localhost:4041"
CYCLE = 60
ROOM = "/home/ubuntu/.openclaw/workspace/research/NEXT-EVOLUTION.md"

def fetch(path):
    try: return json.loads(urllib.request.urlopen(f"{PLATO}{path}", timeout=5).read())
    except: return {}

def salience(room_name, tile_count, prev_count):
    novelty = min(1.0, tile_count / 100)
    change = abs(tile_count - prev_count) / max(prev_count, 1)
    curiosity = 1.0 / (1.0 + tile_count)  # Less-known rooms are more curious
    return 0.3 * novelty + 0.4 * change + 0.3 * curiosity

prev = {}
while True:
    status = fetch("/status")
    rooms = status.get("rooms", {})
    scored = []
    for name, data in rooms.items():
        tc = data.get("tile_count", 0)
        s = salience(name, tc, prev.get(name, tc))
        scored.append((s, name, tc))
        prev[name] = tc
    
    scored.sort(key=lambda x: -x[0])
    top = scored[:5]
    
    print(f"\n=== Attention Cycle — {time.strftime('%H:%M:%S')} ===")
    for s, name, tc in top:
        bar = "█" * int(s * 20) + "░" * (20 - int(s * 20))
        print(f"  {bar} {s:.2f}  {name:25s} {tc:4d} tiles")
    print(f"  Total rooms: {len(rooms)}")
    
    time.sleep(CYCLE)
