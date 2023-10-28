from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import requests
import typer

app = typer.Typer(help="💲 Syrian Pound Exchange Rate Scrapper 💲")

table = Table(title="Syrian Central Bank Dollar Rate")
table.add_column("Date", justify="right")
table.add_column("Rate", justify="right")

console = Console()


def get_central_bank_rate(base: str):
    response = requests.get(base).text

    soup = BeautifulSoup(response, "lxml")

    dates = soup.select("div.about-info .law div[class*=bd] div:first-of-type")
    dates = [date.text.strip() for date in dates if date.text.strip()]

    rates = soup.select("div.about-info .law div[class*=bd] div:nth-of-type(2)")
    rates = [rate.text.strip() for rate in rates if rate.text.strip()]

    data = list(zip(dates, rates))

    for row in data:
        row = [row[0], f"{int(row[1].split('.')[0]):,}"]
        table.add_row(*row)

    console.print(table)


@app.command(name="b")
def get_banks_rate():
    """
    Get Official [red]Banks[/red] Rate
    """
    BASE = "https://www.cb.gov.sy/index.php?page=list&ex=2&dir=exchangerate&lang=1&service=2&act=1206"
    get_central_bank_rate(base=BASE)


@app.command(name="o")
def get_general_rate():
    """
    Get Official [red]General[/red] Rate
    """
    BASE = "https://www.cb.gov.sy/index.php?page=list&ex=2&dir=exchangerate&lang=1&service=4&act=1207"
    get_central_bank_rate(base=BASE)


@app.command(name="m")
def get_black_market_rate():
    """
    Get [red]Market[/red] Rate
    """
    BASE = "https://lirat.org/wp-json/alba-cur/cur/1.json"
    res = requests.get(BASE)

    if res.status_code == 200:
        rates = res.json()

        curr_table = Table(title="💵 Dollar Exchange Rate 💵")
        curr_table.add_column("Title")
        curr_table.add_column("Arabic", justify="right")
        curr_table.add_column("Ask", justify="right", style="red")
        curr_table.add_column("Bid", justify="right", style="green")
        curr_table.add_column("Mid", justify="right", style="bold")

        for rate in rates:
            mid_rate = int((int(rate["ask"]) + int(rate["bid"])) / 2)
            curr_table.add_row(
                rate["name"],
                rate["ar_name"],
                f"{int(rate['ask']):,}",
                f"{int(rate['bid']):,}",
                f"{mid_rate:,}",
            )

        console.print(curr_table)

    else:
        console.print("Connection is [red]LOST[/red]")
