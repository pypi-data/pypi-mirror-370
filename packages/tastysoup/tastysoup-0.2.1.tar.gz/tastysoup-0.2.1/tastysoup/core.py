
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

WORD_RE = re.compile(r"[A-Za-z0-9']+")

class TastySoup:
    """SEO-focused wrapper around BeautifulSoup with extra helpers."""

    def __init__(self, url_or_html: str, timeout: int = 15):
        self.timeout = timeout
        if url_or_html.startswith(("http://", "https://")):
            resp = requests.get(url_or_html, timeout=self.timeout, headers={
                "User-Agent": "tastysoup/0.2 (+https://pypi.org/project/tastysoup/)"
            })
            resp.raise_for_status()
            self.html = resp.text
            self.base_url = url_or_html
        else:
            self.html = url_or_html
            self.base_url = None
        self.soup = BeautifulSoup(self.html, "lxml")

    def get_title(self):
        tag = self.soup.find("title")
        return tag.get_text(strip=True) if tag else None

    def get_description(self):
        tag = self.soup.find("meta", attrs={"name": "description"})
        return tag["content"].strip() if tag and tag.has_attr("content") else None

    def get_headings(self):
        return {
            f"h{i}": [h.get_text(strip=True) for h in self.soup.find_all(f"h{i}")]
            for i in range(1, 7)
        }

    def get_links(self, internal=True):
        links = [a["href"] for a in self.soup.find_all("a", href=True)]
        if not self.base_url:
            return links
        domain = urlparse(self.base_url).netloc
        if internal:
            return [l for l in links if urlparse(l).netloc in ("", domain)]
        else:
            return [l for l in links if urlparse(l).netloc not in ("", domain)]

    def get_images(self, without_alt=False):
        imgs = self.soup.find_all("img")
        if without_alt:
            return [img.get("src") for img in imgs if not img.get("alt")]
        return [{"src": img.get("src"), "alt": img.get("alt", "")} for img in imgs]

    def get_word_count(self):
        text = self.soup.get_text(" ", strip=True)
        return len(WORD_RE.findall(text))

    def get_keyword_density(self, keyword: str):
        text = self.soup.get_text(" ", strip=True).lower()
        words = WORD_RE.findall(text)
        if not words:
            return 0.0
        count = words.count(keyword.lower())
        return round((count / len(words)) * 100, 2)

    def get_schema(self):
        scripts = self.soup.find_all("script", type="application/ld+json")
        schemas = []
        for script in scripts:
            try:
                import json
                schemas.append(json.loads(script.string))
            except Exception:
                pass
        return schemas

    @classmethod
    def audit_report(cls, urls: list[str]):
        """Run audit for multiple URLs and return as list of dicts."""
        results = []
        for url in urls:
            try:
                soup = cls(url)
                results.append({
                    "url": url,
                    "title": soup.get_title(),
                    "description": soup.get_description(),
                    "word_count": soup.get_word_count(),
                    "h1": soup.get_headings().get("h1", []),
                    "internal_links": len(soup.get_links(internal=True)),
                    "external_links": len(soup.get_links(internal=False)),
                    "images_missing_alt": len(soup.get_images(without_alt=True)),
                })
            except Exception as e:
                results.append({"url": url, "error": str(e)})
        return results
