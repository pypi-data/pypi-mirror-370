import time
import typer
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils.nbib2bib import nbib2bibtex

app = typer.Typer()

@app.command()
def nbib2bib(
    nbib: Annotated[str, typer.Option("--nbib", "-i", help="Input nbib file.")], 
    bib: Annotated[str, typer.Option("--bib", "-o", help="Output bib file.")],
    ):
    """
    nbib file converts to bib file .
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="convert...", total=None)
            start=time.time()
            nbib2bibtex(nbib, bib)
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"convert Done, time cost: {time_cost}")
            progress.add_task(description=f"convert Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="convert Failed", total=None)
            raise SystemExit(1) 
      
        