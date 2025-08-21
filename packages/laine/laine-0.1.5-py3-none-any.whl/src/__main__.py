from InquirerPy import inquirer
from cookies import load_cookies_from_file
from processor import download_chapter
from providers import PROVIDERS

def main():
    print("✦ Multi-Site Manga Chapter Downloader ✦")

    choice = inquirer.select(
        message="Select Provider:",
        choices=list(PROVIDERS.keys())
    ).execute()

    provider = PROVIDERS[choice]
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