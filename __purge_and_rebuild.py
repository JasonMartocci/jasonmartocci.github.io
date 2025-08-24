import json, os, sys, subprocess

repo = r"C:\Users\marto\OneDrive\Desktop\eDeveloper Solutions\Jason Martocci\JasonMartocci.github.io"
tool = r"C:\Users\marto\OneDrive\Desktop\eDeveloper Solutions\Jason Martocci\Martocci Mayhem Tools\mayhem_maker.py"

videos_path  = os.path.join(repo, "videos.json")
removed_path = os.path.join(repo, "removed.json")
videos_dir   = os.path.join(repo, "videos")
index_path   = os.path.join(repo, "index.html")

targets = {"let-s-chat-and-chill", "can-you-really-sleep-on-a-bed-of-weed"}

def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

# 1) Load cache and remove target slugs
data = load_json(videos_path, [])
removed_ids, removed_slugs = [], []
kept = []
for v in data:
    sl = (v.get("slug") or "").lower()
    if sl in targets:
        removed_slugs.append(sl)
        vid = (v.get("video_id") or "").strip()
        if vid: removed_ids.append(vid)
        continue
    kept.append(v)

if removed_slugs:
    with open(videos_path, "w", encoding="utf-8") as f:
        json.dump(kept, f, indent=2)
else:
    print("Targets not present in videos.json (maybe already purged).")

# 2) Update removed.json with any found IDs
cur_removed = load_json(removed_path, [])
if not isinstance(cur_removed, list): cur_removed = []
cur_set = set(map(str, cur_removed))
for vid in removed_ids:
    if vid: cur_set.add(vid)
with open(removed_path, "w", encoding="utf-8") as f:
    json.dump(sorted(cur_set), f, indent=2)

# 3) Delete leftover HTML files (slug and id naming)
deleted_files = 0
for sl in targets:
    p = os.path.join(videos_dir, f"{sl}.html")
    if os.path.exists(p):
        os.remove(p); deleted_files += 1
for vid in removed_ids:
    if not vid: continue
    p = os.path.join(videos_dir, f"{vid.lower()}.html")
    if os.path.exists(p):
        os.remove(p); deleted_files += 1

print(f"Purged slugs: {removed_slugs}")
print(f"Removed IDs:  {removed_ids}")
print(f"Deleted HTML: {deleted_files}")

# 4) Rebuild + deploy
cmd = [sys.executable, tool, "--nogui", "--update-index", "--update-videos",
       "--commit-msg", "Purge two pages and rebuild site"]
print("\nRunning:", " ".join(cmd))
subprocess.run(cmd, cwd=os.path.dirname(tool), check=False)

# 5) Verify index.html no longer contains the slugs
try:
    txt = open(index_path, encoding="utf-8").read()
    still = [s for s in targets if s in txt]
    if still:
        print("\nSTILL PRESENT IN index.html:", still)
        print("If you just deployed, try a hard refresh in the browser (Ctrl/Cmd+Shift+R).")
    else:
        print("\nOK: index.html no longer lists the removed slugs.")
except Exception as e:
    print("Verification skipped:", e)
