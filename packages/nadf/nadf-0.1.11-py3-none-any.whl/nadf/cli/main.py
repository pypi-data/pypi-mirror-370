import asyncio
from time import sleep
import typer

from nadf.cli.dots import RainbowDots
from nadf.crawler import Crawler
from nadf.pdf import PDF

app = typer.Typer()

@app.command()
def invoke(
    path: str = typer.Option(..., "-p", help="폴더 경로"),
    url: str = typer.Option(..., "-u", help="namuwiki URL")
):
    asyncio.run(_invoke(path, url))


async def _invoke(path : str, url : str):


    typer.echo(f"탐색 대상 : {url}")
    spinner = RainbowDots("나무위키에서 데이터를 받아오는 중입니다", interval=0.1, max_dots=12)
    spinner.start()
    name, namuwiki_list = await crawl(url)
    spinner.stop("\033[32m데이터 받기 성공!!\033[0m")

    sleep(1)

    typer.echo(f"저장 위치 : {path}")
    spinner = RainbowDots("PDF로 변환을 시작합니다", interval=0.1, max_dots=12)
    spinner.start()
    await create_pdf(name, namuwiki_list, path)
    spinner.stop()


async def crawl(url):
    crawler = Crawler()
    name, namuwiki_list = await crawler.get_namuwiki_list(url)
    return name, namuwiki_list


async def create_pdf(name, namuwiki_list, path):
    pdf = PDF(doc_title=f"{name} 분석 보고서")
    await pdf.create_pdf_from_namuwiki_list(namuwiki_list, path)


@app.command()
def love():
    typer.echo(f"I love you")

if __name__ == "__main__":
   app()
