# news/preview_utils.py (또는 utils.py)

import requests
from bs4 import BeautifulSoup

def fetch_url_preview(url):
    """
    주어진 URL에서 Open Graph 메타데이터(og:title, og:description, og:image)를 추출해 반환.
    만약 가져올 수 없으면 None 또는 기본값을 반환.
    """
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        og_title = soup.find("meta", property="og:title")
        og_desc = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")

        return {
            "title": og_title["content"] if og_title else "",
            "description": og_desc["content"] if og_desc else "",
            "image": og_image["content"] if og_image else ""
        }
    except Exception as e:
        print("Error fetching URL preview:", e)
        return None
