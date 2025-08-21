#This portion downloads the entire download family of a GSE dataset taking only rhe GSE ID


import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from requests.adapters import HTTPAdapter, Retry

def download_geo_family(gse_id: str, dest_dir: str = "Downloads", max_depth: int = 3, delay: float = 0.5):
    """
    Downloads all available files for a given GEO Series (GSE) ID from NCBI GEO FTP.

    Parameters:
    - gse_id: str — GEO Series ID (e.g., "GSE12345")
    - dest_dir: str — Destination base directory (default: "Downloads")
    - max_depth: int — Maximum recursion depth for subfolders (default: 3)
    - delay: float — Delay (in seconds) between requests (default: 0.5)
    """
    number = int(gse_id.replace("GSE", ""))
    digits = len(gse_id) - 6  # dynamic digit slice to form prefix
    prefix = f"GSE{str(number)[:digits]}nnn"
    base_url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{gse_id}/"
    dest_path = os.path.join(dest_dir, gse_id)
    os.makedirs(dest_path, exist_ok=True)

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    visited_urls = set()

    def download_all_files(url: str, local_path: str, depth: int):
        if depth > max_depth or url in visited_urls or not url.startswith(base_url):
            return
        visited_urls.add(url)

        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Cannot access {url} — {e}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a"):
            href = link.get("href")
            if not href or href in ("../", "./"):
                continue

            full_url = urljoin(url, href)
            local_file_path = os.path.join(local_path, href)

            if href.endswith("/"):
                os.makedirs(local_file_path, exist_ok=True)
                time.sleep(delay)
                download_all_files(full_url, local_file_path, depth + 1)
            else:
                if os.path.exists(local_file_path) and os.path.getsize(local_file_path) > 0:
                    print(f"[SKIP] {href} already exists")
                    continue

                print(f"[DOWNLOADING] {href}")
                try:
                    with session.get(full_url, stream=True, timeout=60) as r:
                        r.raise_for_status()
                        total_size = int(r.headers.get("content-length", 0))
                        with open(local_file_path, "wb") as f, tqdm(
                            total=total_size,
                            unit="B",
                            unit_scale=True,
                            desc=href,
                            leave=False
                        ) as bar:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    bar.update(len(chunk))
                    print(f"[SAVED] {href}")
                except Exception as e:
                    print(f"[ERROR] Failed to download {href} — {e}")

                time.sleep(delay)

    print(f"[START] Downloading files for {gse_id}")
    download_all_files(base_url, dest_path, depth=0)
    print(f"[DONE] Completed downloading for {gse_id}")
    