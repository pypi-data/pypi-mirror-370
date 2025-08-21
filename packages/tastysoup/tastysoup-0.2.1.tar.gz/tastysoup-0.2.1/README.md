
# 🍲 TastySoup

A tasty SEO-focused wrapper around BeautifulSoup for extracting metadata, headings, links, images, and schema.

## Features
- Extract meta title & description
- Extract H1–H6 headings
- Extract internal/external links
- Extract images (check missing alt attributes)
- Word count + keyword density
- Extract JSON-LD schema
- Bulk audit report for multiple URLs

## Installation
```bash
pip install tastysoup
```

## Usage
```python
from tastysoup import TastySoup

soup = TastySoup("https://example.com")
print(soup.get_title())
print(soup.get_description())
print(soup.get_headings())
print(soup.get_links())
print(soup.get_images(without_alt=True))
print(soup.get_word_count())
print(soup.get_keyword_density("example"))
print(soup.get_schema())
```
