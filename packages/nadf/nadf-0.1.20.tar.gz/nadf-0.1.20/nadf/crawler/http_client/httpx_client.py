import asyncio

from bs4 import BeautifulSoup
from httpx import AsyncClient

from nadf.crawler.http_client.crawler_client import CrawlerClient

HEADERS = {
    "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        ),
        "Referer": "https://namu.wiki/",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

#
# COOKIES = {
#     "__cf_bm": "8W433mvwz.8ujsBRMKl_pRQG2ObJCfZ7vaVjPnJAsMY-1755503191-1.0.1.1-cbGwhSFBgnCpCm8E6DakSRaArsfsJmqnHhjy.DrKUM_XBPXruRtAbr.P257bTfeCnTNzb7jaREw0X_h5LCtM3x3WEgNZ4q4MlU50G32Te6w",
#     "__cfuid": "cUVzzQ%2BB2gPxAv%2B59gtVhQ%3D%3D",
#     "cf_clearance": "PY_89gvisMRFCsfLUgAlAfhBFMfJqJztfBwnVyeYar4-1755503764-1.2.1.1-NjlnBEyBpr_JKYNQoVZPOAZ8EVExuGO2WCFJDjS09wK1T_fyQxESVU3knCo4ZcR7cc6auFp6osm4kD8J2fEAeGcyQ0gdXcXTriOQjsg6iETK7PpW.9iH404Kj2WoiZbcxvxKDYSCw14Fn5xg10kqcxzU8mjxr346l76x62ZouDPdSjoWVeWlFylP3K4BdvgeRAOzM5XTv8i2L4GwDnDVeCvJHov7KnqGF4uYd8m_IoM",
#     "kotori": "RF6e7tcF89J5bOfAEZqJcDR-vB5kO192",
#     "kotori.sig": "n8k_01Zj67TzcQXkVPAYTu5wqFg",
# }


class HttpxClient(CrawlerClient):
    def __init__(self):
        self.client = AsyncClient(headers=HEADERS)

    # override
    async def get(self, url : str, timeout : int = 30):
       res  = await self.client.get(url, timeout=timeout)
       print(res)
       res.raise_for_status()
       soup = BeautifulSoup(res.content, "html.parser")
       return soup

    def __del__(self):
        self.client.aclose()

if __name__ == "__main__":
    client = HttpxClient()
    print(asyncio.run(client.get("https://namu.wiki/w/%EB%82%98%EB%A3%A8%ED%86%A0")))

