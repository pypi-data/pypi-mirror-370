import os, io, zipfile, tempfile
from tqdm import tqdm
from PIL import Image
from fetcher import fetch_with_retries
from parser import extract_chapter_json, parse_pages
from deobfuscator import deobfuscate, detect_transparent_strip, restore_right_strip

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
        for i, page in enumerate(tqdm(pages, desc="✦ Process", bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}"), 1):
            process_page(page, i, temp_dir, cookies=cookies, referer=referer)
        zip_filename = os.path.abspath(output_path or f"{chapter_id}.zip")
        with zipfile.ZipFile(zip_filename, "w") as zipf:
            for img_file in sorted(os.listdir(temp_dir)):
                if img_file.endswith(".png"):
                    zipf.write(os.path.join(temp_dir, img_file), arcname=img_file)
        print(f"✓ Deobfuscated & Downloaded")