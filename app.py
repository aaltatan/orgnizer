import os
import typer
from tax import app as tax_app
from exchange import app as exchange_app
from automata import app as automata_app


os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = typer.Typer(rich_markup_mode="rich")

app.add_typer(tax_app.app, name="tax")
app.add_typer(exchange_app.app, name="ex")
app.add_typer(automata_app.app, name="auto")

if __name__ == "__main__":
    app()
