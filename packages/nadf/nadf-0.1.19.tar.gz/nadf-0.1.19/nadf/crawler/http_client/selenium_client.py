import asyncio
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common.exceptions import (
    WebDriverException,
    NoSuchWindowException,
    InvalidSessionIdException,
)
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
        self._exec = ThreadPoolExecutor(max_workers=1)
        self._loop = asyncio.get_event_loop()
        self._lock = asyncio.Lock()

        def _new_driver():
            opts = uc.ChromeOptions()
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument("--headless=new")          # 권장
            opts.add_argument("--disable-dev-shm-usage")
            driver = uc.Chrome(options=opts, version_main=139)
            driver.set_page_load_timeout(30)
            return driver

        self._new_driver = _new_driver
        self._driver_fut = self._loop.run_in_executor(self._exec, self._new_driver)

    async def _run(self, fn):
        driver = await self._driver_fut
        return await self._loop.run_in_executor(self._exec, lambda: fn(driver))

    async def _recreate_driver(self):
        def _quit_and_create(old):
            try:
                old.quit()
            except Exception:
                pass
            return self._new_driver()

        old = await self._driver_fut
        self._driver_fut = self._loop.run_in_executor(self._exec, lambda: _quit_and_create(old))
        return await self._driver_fut

    async def _ensure_alive(self):
        def _check(drv):
            try:
                _ = drv.current_window_handle
                return True
            except Exception:
                return False

        drv = await self._driver_fut
        alive = await self._loop.run_in_executor(self._exec, lambda: _check(drv))
        if not alive:
            await self._recreate_driver()

    # override
    async def get(self, url: str):
        async with self._lock:
            await self._ensure_alive()

            def _fetch(driver):
                driver.get(url)
                return BeautifulSoup(driver.page_source, "html.parser")

            try:
                return await self._run(_fetch)

            except (NoSuchWindowException, InvalidSessionIdException) as e:
                await self._recreate_driver()
                return await self._run(lambda d: (d.get(url), BeautifulSoup(d.page_source, "html.parser"))[1])

            except WebDriverException as e:
                await self._recreate_driver()
                return await self._run(lambda d: (d.get(url), BeautifulSoup(d.page_source, "html.parser"))[1])

    async def close(self):
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
