import os
import re
import time
import hashlib
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import quote_plus
import sys

success, fail = 0, 0
downloaded_hashes = set()
downloaded_urls = set()

def download_image(url, final_path, folder_name):
    global success, fail
    try:
        if url in downloaded_urls:
            return
        downloaded_urls.add(url)

        resp = requests.get(url, timeout=10, stream=True)
        img_data = resp.content

        img = Image.open(BytesIO(img_data))
        img.verify()
        ext = img.format.lower()
        img_hash = hashlib.md5(img_data).hexdigest()
        if img_hash in downloaded_hashes:
            return
        downloaded_hashes.add(img_hash)

        filename = os.path.join(final_path, f"{folder_name}_{success + fail}.{ext}")
        with open(filename, "wb") as f:
            f.write(img_data)
        success += 1
        print(f"✅ Saved {filename}")

    except Exception as e:
        fail += 1
        print(f"⚠️ Failed {url} : {e}")


def scrape_google(query, final_path, folder_name, max_pages=50):
    print(f"\n🌐 Scraping Google Images for '{query}'...\n")
    encoded_query = quote_plus(query)
    for page in range(max_pages):
        url = f"https://www.google.com/search?tbm=isch&ijn={page}&q=t{encoded_query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        links = re.findall(r'"ou":"(.*?)"', html)
        if not links:
            break

        for link in links:
            download_image(link, final_path, folder_name)

        time.sleep(1)


def scrape_bing(query, final_path, folder_name, max_pages=50):
    print(f"\n🌐 Scraping Bing Images for '{query}'...\n")
    encoded_query = quote_plus(query)
    count = 0
    while count < max_pages * 35:
        url = f"https://www.bing.com/images/async?q=t{encoded_query}&first={count}&count=35"
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        links = re.findall(r'murl&quot;:&quot;(.*?)&quot;', html)
        if not links:
            break

        for link in links:
            download_image(link, final_path, folder_name)

        count += 35
        time.sleep(1)


def scrape_yahoo(query, final_path, folder_name, max_pages=50):
    print(f"\n🌐 Scraping Yahoo Images for '{query}'...\n")
    encoded_query = quote_plus(query)
    for page in range(max_pages):
        pos = page * 60
        url = f"https://images.search.yahoo.com/search/images?p=t{encoded_query}&b={pos}"
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        links = re.findall(r'"mediaurl":"(.*?)"', html)
        if not links:
            break

        for link in links:
            download_image(link, final_path, folder_name)

        time.sleep(1)


def main():
    try:
        query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("🔍 Enter keyword: ").strip()
        folder_name = query.replace(" ", "_")
        base_root = "/sdcard/Imagescraper"
        final_path = os.path.join(base_root, folder_name)

        if not os.path.exists(final_path):
            os.makedirs(final_path)
            print(f"📂 Created folder: {final_path}")

        scrape_google(query, final_path, folder_name)
        scrape_bing(query, final_path, folder_name)
        scrape_yahoo(query, final_path, folder_name)

        print(f"\n🎉 Done! {success} images saved in '{final_path}' | {fail} failed.")
        print("Made with ❤️ by MaviMods")

    except KeyboardInterrupt:
        print("\n👋 Exiting gracefully... Bye!")
        sys.exit(0)
