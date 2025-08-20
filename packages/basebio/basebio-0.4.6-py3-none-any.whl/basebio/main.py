import typer
from .modules.cmd import run
from .modules.crud import create, query, update, delete
from .modules.nbib2bib import nbib2bib
from .modules.prepare import prepare

app = typer.Typer(add_completion=False)

@app.callback()
def callback():
    """
    BaseBio is a Python package for bioinformatics.
    """

app.command(name="cmd")(run)
app.command(name="create")(create)
app.command(name="prepare")(prepare)
app.command(name="query")(query)
app.command(name="update")(update)
app.command(name="delete")(delete)
app.command(name="nbib2bib")(nbib2bib)


if __name__ == "__main__":
    app()