#!/usr/bin/env python3
"""Download BA labour-market flow files (ANBA Jahreszahlen, Zeitreihen PDF) into
/home/user/buffers/data/raw/ba_flows/. Re-runnable: skips files that exist.
Usage: python3 fetch_ba_flows.py [--force]
"""
import os, sys, time, subprocess

RAW = "/home/user/buffers/data/raw/ba_flows"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
B = "https://statistik.arbeitsagentur.de/Statistikdaten/Detail"

FILES = {}
for y in range(2017, 2026):
    FILES[f"anba-arbeitsmarkt-d-0-{y}12.xlsx"] = (
        f"{B}/{y}12/anba/anba-arbeitsmarkt/anba-arbeitsmarkt-d-0-{y}12-xlsx.xlsx?__blob=publicationFile&v=1")
FILES["analyse-arbeitsmarkt-zeitreihen-d-0-202512.pdf"] = (
    f"{B}/202512/analyse/analyse-arbeitsmarkt-zeitreihen/analyse-arbeitsmarkt-zeitreihen-d-0-202512-pdf.pdf?__blob=publicationFile&v=1")
EXTRA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ba_flows_extra_urls.txt")
if os.path.exists(EXTRA):  # optional lines: "<filename> <url>"
    for line in open(EXTRA):
        p = line.split()
        if len(p) == 2:
            FILES[p[0]] = p[1]


def fetch(name, url, force=False):
    out = os.path.join(RAW, name)
    if os.path.exists(out) and os.path.getsize(out) > 10000 and not force:
        return "exists"
    for attempt in range(6):
        r = subprocess.run(["curl", "-sSL", "-A", UA, "--max-time", "180", "-o", out + ".part",
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        code = r.stdout.strip()
        if code == "200":
            head = open(out + ".part", "rb").read(8)
            if head.startswith(b"PK") or head.startswith(b"%PDF") or head.startswith(b"\xd0\xcf"):
                os.replace(out + ".part", out)
                return "ok"
            code = "not-a-data-file"
        if code == "404":
            break
        time.sleep(20 * (attempt + 1))  # 429 rate limit back-off
    if os.path.exists(out + ".part"):
        os.remove(out + ".part")
    return f"failed ({code})"


if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True)
    force = "--force" in sys.argv
    for n, u in FILES.items():
        print(n, fetch(n, u, force), flush=True)
        time.sleep(5)
