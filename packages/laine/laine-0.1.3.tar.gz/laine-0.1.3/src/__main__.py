import os
import io
import time
import zipfile
import tempfile
import requests
import json
import html
from PIL import Image
from bs4 import BeautifulSoup
from tqdm import tqdm
from InquirerPy import inquirer


class Cookie:
    def __init__(self, domain, expirationDate, hostOnly, httpOnly, name, path,
                 sameSite, secure, session, storeId, value):
        self.domain = domain
        self.expirationDate = expirationDate
        self.hostOnly = hostOnly
        self.httpOnly = httpOnly
        self.name = name
        self.path = path
        self.sameSite = sameSite
        self.secure = secure
        self.session = session
        self.storeId = storeId
        self.value = value

    def to_dict(self):
        return {
            "domain": self.domain,
            "expirationDate": self.expirationDate,
            "hostOnly": self.hostOnly,
            "httpOnly": self.httpOnly,
            "name": self.name,
            "path": self.path,
            "sameSite": self.sameSite,
            "secure": self.secure,
            "session": self.session,
            "storeId": self.storeId,
            "value": self.value,
        }


def load_cookies_from_file(filename="cookie.json"):
    cookies = []
    print("✦ Loading Cookies...")
    if not os.path.exists(filename):
        print(f"✗ Cookie file '{filename}' not found. Skipping...")
        return cookies
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            for item in data:
                cookies.append(
                    Cookie(
                        domain=item.get("domain"),
                        expirationDate=item.get("expirationDate"),
                        hostOnly=item.get("hostOnly"),
                        httpOnly=item.get("httpOnly"),
                        name=item.get("name"),
                        path=item.get("path"),
                        sameSite=item.get("sameSite"),
                        secure=item.get("secure"),
                        session=item.get("session"),
                        storeId=item.get("storeId"),
                        value=item.get("value"),
                    )
                )
        print("✓ Cookies has been loaded successfully.")
    except json.JSONDecodeError as e:
        print(f"✗ Error: an error occurred while decoding cookie file: {e}. Skipping...")
    except Exception as e:
        print(f"✗ Error: An error occurred while loading cookies: {e}. Skipping...")
    return cookies


def fetch_with_retries(url, cookies=None, referer=None):
    max_retries = 5
    for i in range(max_retries):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": referer
            }
            req_cookies = {}
            if cookies:
                for cookie in cookies:
                    req_cookies[cookie.name] = cookie.value
            resp = requests.get(
                url, headers=headers, cookies=req_cookies, timeout=15
            )
            resp.raise_for_status()
            return resp
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(2 * (2 ** i))
            else:
                raise e


def extract_chapter_json(page_url, cookies=None, referer=None):
    resp = fetch_with_retries(page_url, cookies=cookies, referer=referer)
    soup = BeautifulSoup(resp.text, "lxml")
    json_data = soup.find(id="episode-json")
    if not json_data or not json_data.has_attr("data-value"):
        raise ValueError("Data couldn't be found!")
    unescaped = html.unescape(json_data["data-value"])
    return json.loads(unescaped)


def parse_pages(json_blob):
    pages = json_blob["readableProduct"]["pageStructure"]["pages"]
    parsed = []
    for page in pages:
        src = page.get("src")
        width = int(page.get("width", 0))
        height = int(page.get("height", 0))
        if src and width and height:
            parsed.append({
                "src": src,
                "width": width,
                "height": height
            })
    parsed.sort(key=lambda p: p["src"])
    return parsed


def detect_transparent_strip(img):
    width, height = img.size
    max_transparent_width = 0
    for x in reversed(range(width)):
        transparent = True
        for y in range(height):
            _, _, _, a = img.getpixel((x, y))
            if a != 0:
                transparent = False
                break
        if transparent:
            max_transparent_width += 1
        else:
            break
    return max_transparent_width


def deobfuscate(img, width, height):
    spacing_w = (width // 32) * 8
    spacing_h = (height // 32) * 8
    dst = Image.new("RGBA", (width, height))
    for x in range(0, width, spacing_w):
        for y_offset in range(0, height, spacing_h):
            initial_y_start = (x // spacing_w) * spacing_h + spacing_h
            for y in range(initial_y_start, height, spacing_h):
                if y + spacing_h > height:
                    continue
                old_rect = (x, y, x + spacing_w, y + spacing_h)
                new_x = (y // spacing_h) * spacing_w
                new_y = (x // spacing_w) * spacing_h
                new_rect = (new_x, new_y, new_x + spacing_w, new_y + spacing_h)
                dst.paste(img.crop(new_rect), old_rect[:2])
                dst.paste(img.crop(old_rect), new_rect[:2])
    for i in range(4):
        mx, my = i * spacing_w, i * spacing_h
        mid_rect = (mx, my, mx + spacing_w, my + spacing_h)
        dst.paste(img.crop(mid_rect), mid_rect[:2])
    return dst


def restore_right_strip(deob_img, orig_img, width, height, strip_width):
    if strip_width <= 0:
        return
    box = (width - strip_width, 0, width, height)
    strip = orig_img.crop(box)
    deob_img.paste(strip, (width - strip_width, 0))


def process_page(page, index, output_dir, cookies=None, referer=None):
    img_resp = fetch_with_retries(page["src"], cookies=cookies, referer=referer)
    orig_img = Image.open(io.BytesIO(img_resp.content)).convert("RGBA")
    deob = deobfuscate(orig_img, page["width"], page["height"])
    strip_width = detect_transparent_strip(deob)
    restore_right_strip(deob, orig_img, page["width"], page["height"], strip_width)
    file_path = os.path.join(output_dir, f"{index:03d}.png")
    deob.save(file_path)


def download_chapter(chapter_id, output_path, cookies=None, base_url=None, referer=None):
    chapter_url = f"{base_url}{chapter_id}"
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"✦ Fetching...")
        json_blob = extract_chapter_json(chapter_url, cookies=cookies, referer=referer)
        pages = parse_pages(json_blob)
        print(f"✦ Processing {len(pages)} Pages...")
        for i, page in enumerate(tqdm(pages, desc="✦ Processing", bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}"), 1):
            process_page(page, i, temp_dir, cookies=cookies, referer=referer)
        zip_filename = os.path.abspath(output_path or f"{chapter_id}.zip")
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for img_file in sorted(os.listdir(temp_dir)):
                if img_file.endswith(".png"):
                    zipf.write(os.path.join(temp_dir, img_file), arcname=img_file)
        print(f"✓ Deobfuscated & Downloaded")


def main():
    print("「 ✦ Multi-Site Manga Chapter Downloader ✦ 」")
    providers = {
        "Comic Days": {
            "base_url": "https://comic-days.com/episode/",
            "referer": "https://comic-days.com"
        },
        "Comic Gardo": {
            "base_url": "https://comic-gardo.com/episode/",
            "referer": "https://comic-gardo.com"
        },
        "Comic Zenon": {
            "base_url": "https://comic-zenon.com/episode/",
            "referer": "https://comic-zenon.com"
        },
        "Flat Hero's": {
            "base_url": "https://viewer.heros-web.com/episode/",
            "referer": "https://viewer.heros-web.com"
        }
    }
    choice = inquirer.select(
        message="Select Provider:",
        choices=list(providers.keys())
    ).execute()
    provider = providers[choice]
    cookies = load_cookies_from_file()
    chapter_id = input("➤ Chapter ID: ").strip()
    try:
        download_chapter(
            chapter_id,
            f"{chapter_id}.zip",
            cookies=cookies,
            base_url=provider["base_url"],
            referer=provider["referer"]
        )
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()