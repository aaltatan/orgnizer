import httpx
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel
import typer


app = typer.Typer(help="💲 Automata4 15322 Ledger ")


class Row(BaseModel):
    VOUCHER_DATE: str
    BASIC_LOCAL_DEBIT: int
    BASIC_LOCAL_CREDIT: int
    BASIC_TOTAL: int
    VOUCHER_DETAIL_NOTE: str


@app.command("15322")
def get_15322_ledger():
    """
    Get [red]15322[/red] Ledger
    """
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "Referer": "http://edu/RAS/?sc=177",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    data = {
        "loadState": "true",
        "oper": "grid",
        "firstLoad": "Y",
        "rows": "1000",
        "page": "1",
        "sord": "desc",
    }

    cookies = {
        "cal_getYearsTree": "%5B0%2C%5B0%2C0%2C0%2C0%5D%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%5D%7C20222",
        "c_cal_periodGroupCode": "COURSES",
        "act_accountTree": "%5B0%2C0%2C0%2C0%5D%7Cundefined",
        "c_rpt_selectedSemester": "ALL",
        "WPU_lang": "ar",
        "c_act_ledger_accountId": "519.115",
        "c_act_ledger_currencyId": "284",
        "c_act_ledger_lastMatching": "N",
        "PHPSESSID": "6rjf7n78sn4c6kusqo7v310s3g",
    }

    res = httpx.post(
        "http://edu/RAS/app/_fin/act/views/scripts/ledger_grid.php",
        data=data,
        headers=headers,
        cookies=cookies,
    )

    data = res.json()["rows"]
    headers = list(Row(**data[0]).model_dump().keys())

    table = Table(title="حساب السلف", show_lines=True)
    [
        table.add_column(header=header, justify="right", overflow="crop", max_width=50)
        for header in headers
    ]
    console = Console()

    for row in data:
        row = Row(**row).model_dump()
        row = [f"{cell}" if type(cell) != int else f"{cell:,}" for cell in row.values()]
        table.add_row(*row)

    console.print(table)
