## 🌊 Laine

A CLI tool to deobfuscate & download manga chapters from multiple official Japanese providers.

### 🪐 Features
- Supports multiple official japanese providers.
- Downloads all pages of a chapter.
- Deobfuscates scrambled image blocks.
- Restores any missing transparency on the right side.
- Saves pages as PNG images inside a ZIP archive.

### 🧩 Requirements

- Python `3.7` or higher

Dependencies are automatically installed with `pip`:

- `requests`
- `beautifulsoup4`
- `pillow`
- `tqdm`
- `lxml`
- `InquirerPy`

### 🚀 Installation

```bash
pip install laine
```

> 🔒 Make sure you have Python 3.7+ and pip installed.

### 💎 Providers

| Provider         | Base URL                                   | Auth (Cookies) | Tested |
|------------------|--------------------------------------------|----------------|--------|
| **Comic Days**   | [Visit](https://comic-days.com)            | ✅ Supported   | ✅ Yes |
| **Comic Gardo**  | [Visit](https://comic-gardo.com)           | ✅ Supported   | ✅ Yes |
| **Comic Zenon**  | [Visit](https://comic-zenon.com)           | ✅ Supported   | ✅ Yes |
| **Flat Hero's**  | [Visit](https://viewer.heros-web.com)      | ✅ Supported   | ✅ Yes |


### ✨ Usage

Once installed, run the command:

```bash
laine
```

- You’ll first select a provider using an arrow-key menu.
- Then you’ll enter the chapter ID.
- The result will be a ZIP archive containing clean, deobfuscated PNG images of the manga chapter.

### ❓ Example (Comic-Days Example)

If the chapter URL is:

```md
https://comic-days.com/episode/2550912965469911422
```

You have to use just the ID:

```md
2550912965469911422
```

### 🔑 Auth Setup (Comic-Days Example)

Create `cookie.json` in root directory:

```json
[
    {
        "domain": "comic-days.com",
        "expirationDate": 1786178421.644756,
        "hostOnly": true,
        "httpOnly": true,
        "name": "glsc",
        "path": "/",
        "sameSite": null,
        "secure": true,
        "session": false,
        "storeId": null,
        "value": "COOKIE_VALUE"
    }
]
```

> Use browser devtools to extract fresh cookie values, or use this [extension](https://cookie-editor.com), just hit export and select json.

### 📜 License

This project is available under the [MIT License](LICENSE).

### 📢 Disclaimer

This tool is intended for `educational` and `personal use` only. Please respect the terms of service of Comic-Days and any applicable copyright laws.