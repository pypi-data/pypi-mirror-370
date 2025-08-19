import asyncio
from time import sleep
import typer
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
    typer.echo("나무위키에서 데이터를 받아오는 중입니다 .........")
    typer.echo(f"탐색 대상 : {url}")

    crawler = Crawler()
    name, data = await crawler.get_namuwiki_list(url)
    typer.echo("데이터 받기 성공!")
    sleep(1)

    typer.echo("PDF로 변환을 시작합니다 .........")
    typer.echo(f"저장 위치 : {path}")

    pdf = PDF(doc_title=f"{name} 분석 보고서")
    await pdf.create_pdf_from_namuwiki_list(data, path)


@app.command()
def love():
    typer.echo(f"I love you")

if __name__ == "__main__":
   app()
