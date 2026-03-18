import os, re, json, requests

# WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
WEBHOOK = "https://discord.com/api/webhooks/1478633006846443531/dj64vSn2kuPrEwWjMQezKRtlEJXqWLiCV-mFw1tfnmpBET55DIBNvxa7q4W3zpAOoI1p"
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

m = re.search(
    r'Patch Highlights.*?(https://cmsassets\.rgpub\.io/sanity/images/[^"]+\.(?:png|jpg|jpeg|webp))',
    page,
    re.S
)

if not m:
    print("Patch Highlights image not found")
    exit()

img_url = m.group(1)
print(f"Found patch {patch} with highlights image {img_url}")

STATE = "state.json"
last = ""
if os.path.exists(STATE):
    last = json.load(open(STATE)).get("patch", "")

if patch != last:
    print("sending to webhook")
    img = requests.get(img_url, headers=UA, timeout=30)
    img.raise_for_status()

    r = requests.post(WEBHOOK, files={"file": ("patch_highlights.png", img.content, "image/jpeg")}, timeout=30)
    print("discord status:", r.status_code, r.text)
    r.raise_for_status()

    json.dump({"patch": patch}, open(STATE, "w"))
    print("state updated")
else:
    print("no new patch, skipping send")
