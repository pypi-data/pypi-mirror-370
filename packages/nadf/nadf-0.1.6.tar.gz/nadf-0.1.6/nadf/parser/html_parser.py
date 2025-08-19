from typing import List, Tuple
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

from nadf.decorator.check_namuwiki_url import check_namuwiki_url


class HtmlParser:
    @check_namuwiki_url()
    def __init__(self, html: BeautifulSoup, url: str):
        self.soup = html
        self.url = url


    async def extract_name(self):
        slug = unquote(urlparse(self.url).path.rsplit("/", 1)[-1])
        return slug.replace("_", " ").strip()

    async def extract_small_topics(self) -> List[Tuple[str, str, str]]:  # 레벨 추가
        small_topics = self.soup.find_all(['h2', 'h3', 'h4'])
        small_topics_list = []


        for topic in small_topics:
            level = topic.name  # 'h2', 'h3', 'h4'
            span = topic.find('span')
            small_topics_title = span.get_text().replace("[편집]", "")

            if (link := span.find('a')):
                small_topic = (small_topics_title, link.get("href"), level)
                small_topics_list.append(small_topic)
        return small_topics_list

    async def extract_content(self) -> List[str]:
        lines = self.soup.find_all("div", class_="wJRiSuLS")

        result = []
        for line in lines:
            text = line.get_text(separator=" ", strip=True)
            result.append(text)

        return result
