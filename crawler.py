from html.parser import HTMLParser
import queue
import requests
import time
from typing import List, Callable
import urllib.parse
import re

USER_AGENT = "crawler (+utagawakiki@gmail.com)"

IgnoreIf = Callable[[str], bool]


class AnchorExtractor(HTMLParser):
    def __init__(self, baseurl: str, ignore_if: IgnoreIf=(lambda url: True), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._baseurl = baseurl
        self._ignore_if = ignore_if
        self._anchors: List[str] = []

    def anchors(self) -> List[str]:
        return self._anchors

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return

        unordered_attrs = dict(attrs)
        if "href" not in unordered_attrs:
            return

        href = unordered_attrs["href"]
        if href is None:
            return

        if not href.startswith(self._baseurl):
            href = urllib.parse.urljoin(self._baseurl, href)
        
        if self._ignore_if(href):
            return

        self._anchors.append(href)


class Crawler:
    def __init__(self, origin: str):
        parsed_origin = urllib.parse.urlparse(origin)
        self._origin_scheme = parsed_origin.scheme
        self._origin_hostname = parsed_origin.hostname
        self._baseurl = f"{self._origin_scheme}://{self._origin_hostname}/"
        self._crawled = set()
        self._queue = queue.Queue()
        self._queue.put(origin)

    def crawl(self):
        while not self._queue.empty():
            url = self._queue.get()
            self._crawl_url(url)

    def crawled(self):
        return list(self._crawled)

    def _is_same_scheme_hostname(self, url: str) -> bool:
        parsed_url = urllib.parse.urlparse(url)
        return (
            parsed_url.scheme == self._origin_scheme
            and parsed_url.hostname == self._origin_hostname
        )

    def _crawl_url(self, url: str):
        if url in self._crawled:
            return

        if not self._is_same_scheme_hostname(url):
            return

        print(url)
        time.sleep(0.4)

        self._crawled.add(url)
        resp = requests.get(
            url, allow_redirects=True, headers={"User-Agent": USER_AGENT}
        )
        if resp.status_code != 200:
            return

        next_urls = self._extract_anchor_urls(resp.text)
        for url in next_urls:
            if url in self._crawled:
                continue

            self._queue.put(url)

    def _extract_anchor_urls(self, body: str) -> List[str]:
        extractor = AnchorExtractor(self._baseurl, ignore_if=lambda url: '~' in url)
        extractor.feed(body)
        return extractor.anchors()
