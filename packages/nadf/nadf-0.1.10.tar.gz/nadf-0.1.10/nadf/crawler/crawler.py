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
    async def crawling_namuwiki(self, url: str) -> BeautifulSoup:
        http_client = SeleniumClient()
        soup = await http_client.get(url)  # soup은 BeautifulSoup 객체라고 가정

        # res = await clean_html(soup.prettify())
        return soup

    @check_namuwiki_url()
    async def get_namuwiki_list(self, url : str, skip_titles : Set[str] = {"게임", "미디어 믹스", "둘러보기"}):
        # 메인 페이지 HTML
        main_html = await self.crawling_namuwiki(url=url)
        main_parser = HtmlParser(main_html, url=url)
        # 이름 추출
        name = await main_parser.extract_name()
        # print(name)
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
                html = await self.crawling_namuwiki(full_url)
                parser = HtmlParser(html, full_url)
                data = await self.extract_page_data(parser)
                data = [x for x in data if x[0].strip() not in skip_titles]
                namuwiki_list.extend(data)

            else:
                content = content_list_dq.popleft()
                namuwiki_list.append((title, content, level))
        return name, namuwiki_list


    async def extract_page_data(self, parser: HtmlParser) -> list[tuple[str, str, str]]:
        small_topics = await parser.extract_small_topics()

        # print(small_topics)
        content = await parser.extract_content()
        # print(len(small_topics), len(content))
        # if len(small_topics) != len(content):
        #     print(parser.url)
        return [(title, body, level) for (title, _, level), body in zip(small_topics, content)]


if __name__ == "__main__":
    url = "https://namu.wiki/w/%EC%9A%B0%EC%A6%88%EB%A7%88%ED%82%A4%20%EB%82%98%EB%A3%A8%ED%86%A0#s-2.1"
    url2 = "https://namu.wiki/w/%EA%B3%A0%ED%86%A0%20%ED%9E%88%ED%86%A0%EB%A6%AC/%EC%9D%B8%EB%AC%BC%20%EA%B4%80%EA%B3%84"
    print("end")
