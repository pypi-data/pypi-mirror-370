import asyncio
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException
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

        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')

        self._exec = ThreadPoolExecutor(max_workers=1)
        self._loop = asyncio.get_event_loop()

        self._lock = asyncio.Lock()

        def _init_driver():
            driver = uc.Chrome(options=self.options, version_main=139)  # Chrome 139와 정합
            driver.set_page_load_timeout(30)
            return driver

        self._driver_fut = self._loop.run_in_executor(self._exec, _init_driver)

    async def _run(self, fn):

        driver = await self._driver_fut
        return await self._loop.run_in_executor(self._exec, lambda: fn(driver))

    async def _recreate_driver(self):

        def _quit_and_create(old):
            try:
                old.quit()
            except Exception:
                pass
            new = uc.Chrome(options=self.options, version_main=139)
            new.set_page_load_timeout(30)
            return new

        old = await self._driver_fut
        self._driver_fut = self._loop.run_in_executor(self._exec, lambda: _quit_and_create(old))
        return await self._driver_fut

    # override
    async def get(self, url: str):
        async with self._lock:  # 같은 인스턴스 동시 접근 방지
            def _fetch(driver):
                driver.get(url)
                return BeautifulSoup(driver.page_source, "html.parser")

            try:
                return await self._run(_fetch)

            except Exception as e:
                msg = str(e).lower()
                # 창/탭이 먼저 닫힌 전형적 케이스 → 1회 재생성 후 재시도
                if "no such window" in msg or "web view not found" in msg:
                    await self._recreate_driver()
                    return await self._run(lambda d: BeautifulSoup((d.get(url) or d.page_source), "html.parser"))
                # 기타 드라이버 예외도 상황에 따라 재시도 가능
                if isinstance(e, WebDriverException):
                    await self._recreate_driver()
                    return await self._run(lambda d: BeautifulSoup((d.get(url) or d.page_source), "html.parser"))
                raise

    async def close(self):
        """명시적 종료 (권장)"""
        try:
            d = await self._driver_fut
            await self._loop.run_in_executor(self._exec, d.quit)
        finally:
            self._exec.shutdown(wait=False)


if __name__ == '__main__':
    async def main():
        client = SeleniumClient()
        try:
            soup = await client.get("https://namu.wiki/w/%EB%82%98%EB%A3%A8%ED%86%A0")
            print(soup.title.text if soup.title else "(no title)")
        finally:
            await client.close()

    asyncio.run(main())
