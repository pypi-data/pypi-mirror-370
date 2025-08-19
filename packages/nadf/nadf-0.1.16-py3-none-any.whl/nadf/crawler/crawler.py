from collections import deque
from typing import Set

from bs4 import BeautifulSoup

from nadf.crawler.http_client.selenium_client import SeleniumClient
from nadf.decorator.check_namuwiki_url import check_namuwiki_url
from nadf.parser.html_parser import HtmlParser


class Crawler:
    def __init__(self):
        self.base_url = "https://namu.wiki"

    @check_namuwiki_url()
    async def get_namuwiki_list(self, name : str, skip_titles : Set[str] = {"게임", "미디어 믹스", "둘러보기"}):
        # 메인 페이지 HTML
        url = f"{self.base_url}/{name}"
        main_html = await self._crawling_namuwiki(url=url)
        main_parser = HtmlParser(main_html, url=url)
        small_topics = await main_parser.extract_small_topics()
        # print(small_topics)
        namuwiki_list = []
        content_list = await main_parser.extract_content()
        # print(content_list[0])

        content_list_dq = deque(content_list)
        for title, uri, level in small_topics:
            # print(f"title : {title}")
            if title.strip() in skip_titles:
                continue

            if uri.startswith("/w") and level == 'h2':
                content_list_dq.popleft()
                full_url = self.base_url + uri
                html = await self._crawling_namuwiki(full_url)
                parser = HtmlParser(html, full_url)
                data = await self._extract_page_data(parser)
                data = [x for x in data if x[0].strip() not in skip_titles]
                namuwiki_list.extend(data)

            else:
                content = content_list_dq.popleft()
                namuwiki_list.append((title, content, level))
        return namuwiki_list

    @check_namuwiki_url()
    async def _crawling_namuwiki(self, url: str) -> BeautifulSoup:
        http_client = SeleniumClient()
        soup = await http_client.get(url)  # soup은 BeautifulSoup 객체라고 가정

        # res = await clean_html(soup.prettify())
        return soup


    async def _extract_page_data(self, parser: HtmlParser) -> list[tuple[str, str, str]]:
        small_topics = await parser.extract_small_topics()

        # print(small_topics)
        content = await parser.extract_content()
        # print(len(small_topics), len(content))
        # if len(small_topics) != len(content):
        #     print(parser.url)
        return [(title, body, level) for (title, _, level), body in zip(small_topics, content)]

