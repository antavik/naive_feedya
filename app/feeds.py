from dataclasses import dataclass

from settings import ENGLISH_LANGUAGE


@dataclass(frozen=True)
class Feed:
    title: str
    url: str
    language: str
    classify: bool = True
    skip_summary: bool = False


FEEDS = (
    Feed('The Verge', 'https://www.theverge.com/rss/index.xml', ENGLISH_LANGUAGE, skip_summary=True),
    Feed('TNW', 'https://thenextweb.com/feed/', ENGLISH_LANGUAGE, skip_summary=True),
    Feed('ARS Technica', 'http://feeds.arstechnica.com/arstechnica/index', ENGLISH_LANGUAGE),
    Feed('Wired', 'https://www.wired.com/feed/rss', ENGLISH_LANGUAGE),
    # Feed('The Atlantic', 'https://www.theatlantic.com/feed/all/.rss', ENGLISH_LANGUAGE),
    Feed('Hacker News', 'https://news.ycombinator.com/rss', ENGLISH_LANGUAGE),
    Feed('Engadged', 'https://www.engadget.com/rss.xml', ENGLISH_LANGUAGE),
    Feed('MIT Tech Review', 'https://www.technologyreview.com/topnews.rss', ENGLISH_LANGUAGE),
    Feed('The Register', 'https://www.theregister.com/headlines.atom', ENGLISH_LANGUAGE),
    Feed('CNet', 'https://www.cnet.com/rss/all/', ENGLISH_LANGUAGE),
    Feed('Venture Beat', 'https://venturebeat.com/feed/', ENGLISH_LANGUAGE),
    # Feed('python PEP', 'https://www.python.org/dev/peps/peps.rss', ENGLISH_LANGUAGE),  # TODO: Don't process
)


FEEDS_REGISTRY = {
    f.title: f for f in FEEDS
}
