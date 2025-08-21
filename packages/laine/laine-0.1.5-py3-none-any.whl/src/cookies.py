import os, json

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
        return self.__dict__


def load_cookies_from_file(filename="cookie.json"):
    cookies = []
    print("✦ Loading Cookies...")
    if not os.path.exists(filename):
        print(f"✗ Unable to locate '{filename}' file. Skipping authentication...")
        return cookies
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            for item in data:
                cookies.append(Cookie(**item))
        print("✓ Cookie file located and processed.")
    except Exception as e:
        print(f"✗ Error: {e}. Skipping...")
    return cookies