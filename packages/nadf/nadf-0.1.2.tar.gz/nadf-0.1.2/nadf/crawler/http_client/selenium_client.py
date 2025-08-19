import asyncio

from bs4 import BeautifulSoup
import undetected_chromedriver as uc

from nadf.crawler.http_client.crawler_client import CrawlerClient


class SeleniumClient(CrawlerClient):
    def __init__(self):
        self.options = uc.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--headless=new')
        self.driver = uc.Chrome(options=self.options)

    # override
    async def get(self, url: str):
        def _fetch():
            self.driver.get(url)
            html = self.driver.page_source
            return BeautifulSoup(html, "html.parser")

        soup = await asyncio.to_thread(_fetch)
        return soup


if __name__ == '__main__':
    client = SeleniumClient()
    print(asyncio.run(client.get("https://namu.wiki/w/%EB%82%98%EB%A3%A8%ED%86%A0")))

