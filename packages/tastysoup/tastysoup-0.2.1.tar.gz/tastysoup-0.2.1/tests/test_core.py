
from tastysoup import TastySoup

def test_title_and_wordcount():
    html = "<html><head><title>Hello</title><meta name='description' content='desc'></head><body><h1>Heading</h1><p>SEO text</p></body></html>"
    soup = TastySoup(html)
    assert soup.get_title() == "Hello"
    assert soup.get_description() == "desc"
    assert soup.get_headings()["h1"] == ["Heading"]
    assert soup.get_word_count() > 0
