import os, re, json, requests

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
UA = {"User-Agent": "patch-webhook/1.0"}

def first_match(o):
    if isinstance(o, str) and "league-of-legends-patch-" in o and "-notes" in o:
        return o
    if isinstance(o, dict):
        for v in o.values():
            m = first_match(v)
            if m: return m
    if isinstance(o, list):
        for v in o:
            m = first_match(v)
            if m: return m

tags = requests.get("https://www.leagueoflegends.com/en-us/news/tags/patch-notes/", headers=UA, timeout=30).text
nx = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', tags, re.S).group(1)
path = first_match(json.loads(nx))

patch = path if path.startswith("http") else "https://www.leagueoflegends.com" + (path if path.startswith("/") else "/" + path)

page = requests.get(patch, headers=UA, timeout=30).text
imgs = re.findall(r'https://cmsassets\.rgpub\.io/sanity/images/[^"]+\.(png|jpg)', page)

if not imgs:
    raise RuntimeError("No images found on page")

img_url = imgs[1][0] if isinstance(imgs[0], tuple) else imgs[1] if len(imgs) > 1 else imgs[0]

STATE = "state.json"

last = ""
if os.path.exists(STATE):
    last = json.load(open(STATE))["patch"]

if patch != last:
    img = requests.get(img_url, headers=UA, timeout=30).content
    requests.post(WEBHOOK, files={"file": ("patch_highlights.png", img, "image/png")}, timeout=30)
    json.dump({"patch": patch}, open(STATE, "w"))
