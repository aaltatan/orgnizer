from rich.table import Table, box
from rich.console import Console
from rich.progress import track
from .calculate import Taxes
from typing import Optional
import xlwings
import typer
import json
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))
app = typer.Typer(help="⭐ Syrian Layers Tax Calculator ⭐", rich_markup_mode="rich")

table = Table(title="📃 Results 📃", border_style="white", box=box.ROUNDED)
console = Console()

table.add_column("#", style="blue", justify="right")
table.add_column("Fixed Salary", style="white", justify="right")
table.add_column("Comps", style="white", justify="right")
table.add_column("Total", style="green", justify="right")
table.add_column("F/T", style="blue", justify="center")
table.add_column("Layers", style="white", justify="right")
table.add_column("Fixed Tax", style="white", justify="right")
table.add_column("Total", style="red", justify="right")
table.add_column("Net", style="green", justify="right")


def create_wb(data, total: int, filename: str):
    wb = xlwings.Book()
    ws: xlwings.main.Sheet = wb.sheets["Sheet1"]

    headers = [
        "Fixed Salary",
        "Companions",
        "Total",
        "Rate",
        "Layers Tax",
        "One Time Tax",
        "Total",
        "Net",
    ]

    ws["A1:H1"].value = headers

    for row in track(data, f"Generating {filename}.xlsx file 💻 ... ", total=total):
        lr = ws.range("A1000000").end("up").row + 1
        ws[f"A{lr}:H{lr}"].value = row

    ws.name = "Data"
    ws.autofit()
    wb.save(f"./{filename}.xlsx")


with open("./settings.json") as f:
    file = json.load(f)


@app.command(name="l")
def layers_tax(
    salary: int,
    ordinance: Optional[str] = file["current_ordinance"],
    min_rate: Optional[float] = 0.25,
):
    """
    Layers Tax from [green]Fixed Salary[/green]
      e.g.:
        python app.py l [green]500,000[/green] -> table content
    """

    tax = Taxes(ordinance=ordinance, min_rate=min_rate)
    layer = tax.layers_tax(salary=salary)

    row = [1, salary, 0, salary, 100.0, layer, 0, layer, salary - layer]
    row = [f"{cell:2,}%" if type(cell) is float else f"{cell:,}" for cell in row]

    table.add_row(*row)
    console.print(table)


@app.command(name="gf")
def gross_fixed_salary(
    salary: int,
    ordinance: Optional[str] = file["current_ordinance"],
    min_rate: Optional[float] = 0.25,
):
    """
    Gross Fixed Salary from [green]Target Salary[/green]
      e.g.:
        python app.py gf [green]500,000[/green] -> table content
    """
    tax = Taxes(ordinance=ordinance, min_rate=min_rate)
    gross_salary = tax.gross_fixed_salary(salary=salary)
    layer = tax.layers_tax(gross_salary)

    row = [
        1,
        gross_salary,
        0,
        gross_salary,
        100.0,
        layer,
        0,
        layer,
        gross_salary - layer,
    ]
    row = [f"{cell:2,}%" if type(cell) is float else f"{cell:,}" for cell in row]

    table.add_row(*row)
    console.print(table)


@app.command(name="bs")
def best_salary(
    salary: int,
    ordinance: Optional[str] = file["current_ordinance"],
    min_rate: Optional[float] = 0.25,
):
    """
    Best salary after looping on salary rate sequence from [green]Target Salary[/green]
      e.g.:
        python app.py bs [green]500,000[/green] -> table content
    """
    tax = Taxes(ordinance=ordinance, min_rate=min_rate)
    best_salary = tax.best_salary(salary=salary)

    row = ["1"] + [
        f"{cell:2,}%" if type(cell) is float else f"{cell:,}" for cell in best_salary
    ]

    table.add_row(*row)
    console.print(table)


@app.command(name="rs")
def rate_sequence(
    salary: int,
    ordinance: Optional[str] = file["current_ordinance"],
    rate: Optional[float] = 0.25,
    excel: Optional[bool] = False,
    filename: Optional[str] = "data",
):
    """
    Generating 400 row of net salary from [green]Target Salary[/green]
      e.g.:
        1. python app.py rs [green]500,000[/green] -> table content
        2. python app.py rs [green]500,000[/green] --rate [red]0.5[/red] -> table content
        3. python app.py rs [green]500,000[/green] --excel -> Generate [green]data.xlsx[/green] file to same directory
    """
    tax = Taxes(ordinance=ordinance, min_rate=rate)
    gross_salary = tax.rate_sequence(salary=salary)

    if excel:
        create_wb(gross_salary, total=400, filename=filename)
    else:
        for idx, row in track(
            enumerate(gross_salary), description="Calculating 🧮 ... ", total=400
        ):
            row = [str(idx + 1)] + [
                f"{cell:2,}%" if type(cell) is float else f"{cell:,}" for cell in row
            ]

            table.add_row(*row)

    if not excel:
        console.print(table)


@app.command(name="rbs")
def all_sequence(
    min_salary: int,
    max_salary: int,
    step: int,
    ordinance: Optional[str] = file["current_ordinance"],
    rate: Optional[float] = 0.25,
    excel: Optional[bool] = False,
    filename: Optional[str] = "data",
):
    """
    Generating sequence of best salaries based on min and max salary and each step between them
      e.g.:
        python app.py rbs [green][MIN]500,000[/green] [blue][MAX]1000000[/blue] [cyan][STEP]25000[/cyan] -> table content
    """
    tax = Taxes(ordinance=ordinance, min_rate=rate)
    kwargs = {"min_sal": min_salary, "max_sal": max_salary, "step": step}
    all_seq = tax.all_sequence(**kwargs)
    total = (max_salary - min_salary) / step
    total += 1

    if excel:
        create_wb(all_seq, total=total, filename=filename)
    else:
        for idx, row in track(
            enumerate(all_seq), description="Calculating 🧮 ... ", total=total
        ):
            row = [str(idx + 1)] + [
                f"{cell:2,}%" if type(cell) is float else f"{cell:,}" for cell in row
            ]

            table.add_row(*row)

    if not excel:
        console.print(table)


@app.command(name="gs")
def gross_salary(
    salary: int,
    ordinance: Optional[str] = file["current_ordinance"],
    rate: Optional[float] = 0.25,
):
    """
    Gross Salary from [green]Target Salary[/green]
      e.g.:
        1. python app.py gf [green]500,000[/green] -> table content
        2. python app.py gf [green]500,000[/green] --rate [red]0.5[/red] -> table content
    """
    tax = Taxes(ordinance=ordinance, min_rate=rate)
    gross_salary = tax.gross_salary(target_salary=salary, rate=1 - rate)

    row = ["1"] + [
        f"{cell:2,}%" if type(cell) is float else f"{cell:,}" for cell in gross_salary
    ]

    table.add_row(*row)
    console.print(table)


@app.command(name="cs")
def compare_salaries_with_rate(
    salary: int,
    seq: Optional[bool] = False,
    rate_1: float = 0.25,
    rate_2: float = 0.75,
    ordinance: Optional[str] = file["current_ordinance"],
    rate: Optional[float] = 0.25,
):
    """
    Compare two salaries by different rates
    """
    tax = Taxes(ordinance=ordinance, min_rate=rate)

    compare_table = Table(title="📃 Results 📃", border_style="white", box=box.ROUNDED)

    compare_table.add_column("#", style="white", justify="right")
    compare_table.add_column("Salary", style="white", justify="right")
    compare_table.add_column(
        f"Rate of Comps {rate_1:2,}%", style="blue bold", justify="right"
    )
    compare_table.add_column(
        f"Rate of Comps {rate_2:2,}%", style="green bold", justify="right"
    )
    compare_table.add_column("Diff", style="white bold", justify="right")
    compare_table.add_column("Yearly Diff", style="white bold", justify="right")

    if not seq:
        salary_one = tax.gross_salary(target_salary=salary, rate=rate_1)[2]
        salary_two = tax.gross_salary(target_salary=salary, rate=rate_2)[2]

        row = [
            "1",
            f"{salary:,}",
            f"{salary_one:,}",
            f"{salary_two:,}",
            f"{(salary_one -salary_two):,}",
            f"{(salary_one -salary_two) * 12:,}",
        ]

        compare_table.add_row(*row)

    else:
        min_salary = typer.prompt(text="Enter the minimum salary", type=int)
        max_salary = typer.prompt(text="Enter the maximum salary", type=int)
        step = typer.prompt(text="Enter the step", type=int)

        total = (max_salary - min_salary) / step
        total += 1

        for idx, salary in track(
            enumerate(range(min_salary, max_salary + step, step)),
            description="Calculating 🧮 ... ",
            total=total,
        ):
            salary_one = tax.gross_salary(target_salary=salary, rate=rate_1)[2]
            salary_two = tax.gross_salary(target_salary=salary, rate=rate_2)[2]

            row = [
                str(idx + 1),
                f"{salary:,}",
                f"{salary_one:,}",
                f"{salary_two:,}",
                f"{(salary_one -salary_two):,}",
                f"{(salary_one -salary_two) * 12:,}",
            ]

            compare_table.add_row(*row)

    console.print(compare_table)
