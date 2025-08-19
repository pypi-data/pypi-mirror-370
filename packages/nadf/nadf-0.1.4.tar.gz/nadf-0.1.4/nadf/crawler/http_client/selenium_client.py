import asyncio
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from nadf.crawler.http_client.crawler_client import CrawlerClient
import ssl, urllib.request
from nadf.exception.ssl_invalid_exception import SSLInvalidException

try:
    import certifi
    _cafile = certifi.where()
    _ctx = ssl.create_default_context(cafile=_cafile)
    _opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_ctx))
    urllib.request.install_opener(_opener)
except Exception as e:
    print(e)
    raise SSLInvalidException()


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

