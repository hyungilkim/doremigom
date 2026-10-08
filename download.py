import os
import re
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "doremigom_2025.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    books = json.load(f)

story_dir = os.path.join(BASE_DIR, "downloads", "구연동화")
musical_dir = os.path.join(BASE_DIR, "downloads", "뮤지컬동화")
os.makedirs(story_dir, exist_ok=True)
os.makedirs(musical_dir, exist_ok=True)

def sanitize(name):
    return re.sub(r'[\\/:*?"<>|]', '', name).strip()

tasks = []
for b in books:
    num = b["num"]
    safe_name = sanitize(b["name"])
    
    # Musical
    if b["m_mp3"]:
        fname = f"{num:02d}_뮤지컬동화_{safe_name}.mp3"
        tasks.append((b["m_mp3"], os.path.join(musical_dir, fname), fname))
        
    # Story
    if b["s_mp3"]:
        fname = f"{num:02d}_구연동화_{safe_name}.mp3"
        tasks.append((b["s_mp3"], os.path.join(story_dir, fname), fname))

def download_one(task):
    url, path, fname = task
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        return fname, True, "Already exists"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            with open(path, "wb") as fp:
                fp.write(data)
        return fname, True, f"Downloaded ({len(data):,} bytes)"
    except Exception as e:
        return fname, False, str(e)

print(f"총 {len(tasks)}개 음원 다운로드를 시작합니다...")
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(download_one, tasks))

success_count = sum(1 for r in results if r[1])
print(f"\n[완료] 총 {len(tasks)}개 중 {success_count}개 다운로드 성공!")
print(f"저장 위치: {os.path.join(BASE_DIR, 'downloads')}")
