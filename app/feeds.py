from dataclasses import dataclass
from typing import Optional

from settings import ENGLISH_LANGUAGE


@dataclass(frozen=True)
class Feed:
    title: str
    url: str
    language: str
    classify: bool = True
    skip_summary: bool = False
    base_url: Optional[str] = None


FEEDS = (
    Feed('The Verge', 'https://www.theverge.com/rss/index.xml', ENGLISH_LANGUAGE, skip_summary=True, base_url='https://www.theverge.com'),  # noqa
    Feed('Wired', 'https://www.wired.com/feed/rss', ENGLISH_LANGUAGE, base_url='https://www.wired.com'),  # noqa
    Feed('Hacker News', 'https://news.ycombinator.com/rss', ENGLISH_LANGUAGE, base_url='https://news.ycombinator.com'),  # noqa
    Feed('Lobsters', 'https://lobste.rs/rss', ENGLISH_LANGUAGE, base_url='https://lobste.rs'),  # noqa
    Feed('ARS Technica', 'http://feeds.arstechnica.com/arstechnica/index', ENGLISH_LANGUAGE, base_url='https://arstechnica.com'),  # noqa
    Feed('TNW', 'https://thenextweb.com/feed/', ENGLISH_LANGUAGE, skip_summary=True, base_url='https://thenextweb.com'),  # noqa
    Feed('Spectrum IEEE', 'https://spectrum.ieee.org/rss/fulltext', ENGLISH_LANGUAGE, base_url='https://spectrum.ieee.org'),  # noqa
    Feed('Business insider Tech', 'https://www.businessinsider.com/sai/rss', ENGLISH_LANGUAGE, skip_summary=True, base_url='https://www.businessinsider.com'),  # noqa
    Feed('Engadged', 'https://www.engadget.com/rss.xml', ENGLISH_LANGUAGE, base_url='https://www.engadget.com'),  # noqa
    Feed('Slashdot', 'http://rss.slashdot.org/Slashdot/slashdotMain', ENGLISH_LANGUAGE, base_url='https://slashdot.org'),  # noqa
    Feed('MIT Tech Review', 'https://www.technologyreview.com/topnews.rss', ENGLISH_LANGUAGE, base_url='https://www.technologyreview.com'),  # noqa
    Feed('The Register', 'https://www.theregister.com/headlines.atom', ENGLISH_LANGUAGE, skip_summary=True, base_url='https://www.theregister.com'),  # noqa
    Feed('CNet', 'https://www.cnet.com/rss/all/', ENGLISH_LANGUAGE, base_url='https://www.cnet.com'),  # noqa
    Feed('Venture Beat', 'https://venturebeat.com/feed/', ENGLISH_LANGUAGE, base_url='https://venturebeat.com'),  # noqa
    Feed('ArXive CS', 'https://export.arxiv.org/rss/cs', ENGLISH_LANGUAGE, base_url='https://arxiv.org/list/cs/recent'),  # noqa
    Feed('ArXive Economics', 'https://export.arxiv.org/rss/econ', ENGLISH_LANGUAGE, base_url='https://arxiv.org/list/econ/recent'),  # noqa
    Feed('ArXive Statistics', 'https://export.arxiv.org/rss/stat', ENGLISH_LANGUAGE, base_url='https://arxiv.org/list/stat/recent'),  # noqa
    Feed('ArXive Mathematics', 'https://export.arxiv.org/rss/math', ENGLISH_LANGUAGE, base_url='https://arxiv.org/list/math/recent'),  # noqa
    # Feed('python PEP', 'https://www.python.org/dev/peps/peps.rss', ENGLISH_LANGUAGE),  # noqa
    # Feed('The Atlantic', 'https://www.theatlantic.com/feed/all/.rss', ENGLISH_LANGUAGE),  # noqa
)


REGISTRY = {
    f.title: f for f in FEEDS
}
