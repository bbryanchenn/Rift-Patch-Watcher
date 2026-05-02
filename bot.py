import os, re, json, requests

PATCH_WEBHOOK = os.environ["PATCH_WEBHOOK"] 
BANNER_WEBHOOK = os.environ["BANNER_WEBHOOK"]

if not PATCH_WEBHOOK or not BANNER_WEBHOOK:
    raise SystemExit("Missing PATCH_WEBHOOK or BANNER_WEBHOOK env var")


UA = {"User-Agent": "patch-webhook/1.0"}
STATE = "state.json"
BASE = "https://www.leagueoflegends.com"


def first_match(obj):
    if isinstance(obj, str) and "league-of-legends-patch-" in obj and "-notes" in obj:
        return obj

    if isinstance(obj, dict):
        for val in obj.values():
            found = first_match(val)
            if found:
                return found

    if isinstance(obj, list):
        for val in obj:
            found = first_match(val)
            if found:
                return found

    return None


def load_state():
    if os.path.exists(STATE):
        with open(STATE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def full_url(url):
    if not url:
        return None

    url = url.replace("&amp;", "&")

    if url.startswith("data:image"):
        return None

    if url.startswith("//"):
        return "https:" + url

    if url.startswith("/"):
        return BASE + url

    if url.startswith("http"):
        return url

    return None


def send_image(webhook, img_url, filename):
    img = requests.get(img_url, headers=UA, timeout=30)
    img.raise_for_status()

    r = requests.post(
        webhook,
        files={"file": (filename, img.content, "image/png")},
        timeout=30
    )

    print("discord status:", r.status_code, r.text)
    r.raise_for_status()


tags_url = BASE + "/en-us/news/tags/patch-notes/"
tags = requests.get(tags_url, headers=UA, timeout=30).text

next_data_match = re.search(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    tags,
    re.S
)

if not next_data_match:
    raise SystemExit("Could not find NEXT_DATA")

path = first_match(json.loads(next_data_match.group(1)))

if not path:
    raise SystemExit("Could not find latest patch path")

patch_url = full_url(path)

if not patch_url:
    raise SystemExit("Could not build patch URL")

page = requests.get(patch_url, headers=UA, timeout=30).text

highlight_match = re.search(
    r'Patch Highlights.*?(https://cmsassets\.rgpub\.io/sanity/images/[^"]+\.(?:png|jpg|jpeg|webp))',
    page,
    re.S
)

if not highlight_match:
    raise SystemExit("Patch Highlights image not found")

img_url = highlight_match.group(1)

banner_match = re.search(
    r'<meta property="og:image" content="([^"]+)"',
    page
)

banner_url = full_url(banner_match.group(1)) if banner_match else None

print(f"Found patch: {patch_url}")
print(f"Found highlights image: {img_url}")
print(f"Found banner image: {banner_url}" if banner_url else "Banner image not found")

state = load_state()
last_patch = state.get("patch", "")

if patch_url != last_patch:
    print("new patch found, sending highlights")

    send_image(PATCH_WEBHOOK, img_url, "patch_highlights.png")

    if banner_url:
        print("sending banner")
        send_image(BANNER_WEBHOOK, banner_url, "patch_banner.png")
        
        requests.post(
            BANNER_WEBHOOK,
            json={"content": f"RIFT_BANNER_COMMIT__Q7xN2vLm9TpR4kZ8"},
            timeout=30
        ).raise_for_status()
        
    else:
        print("no banner found, skipping banner send")

    state["patch"] = patch_url
else:
    print("no new patch, skipping highlights and banner")

save_state(state)
print("state updated")