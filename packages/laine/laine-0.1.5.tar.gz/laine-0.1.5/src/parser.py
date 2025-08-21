import html, json
from bs4 import BeautifulSoup
from fetcher import fetch_with_retries

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
        src, w, h = page.get("src"), int(page.get("width", 0)), int(page.get("height", 0))
        if src and w and h:
            parsed.append({"src": src, "width": w, "height": h})
    parsed.sort(key=lambda p: p["src"])
    return parsed