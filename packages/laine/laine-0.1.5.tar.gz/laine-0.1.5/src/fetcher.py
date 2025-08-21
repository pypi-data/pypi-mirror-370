import time, requests

def fetch_with_retries(url, cookies=None, referer=None):
    max_retries = 5
    for i in range(max_retries):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": referer
            }
            req_cookies = {c.name: c.value for c in cookies} if cookies else {}
            resp = requests.get(url, headers=headers, cookies=req_cookies, timeout=15)
            resp.raise_for_status()
            return resp
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(2 * (2 ** i))
            else:
                raise e