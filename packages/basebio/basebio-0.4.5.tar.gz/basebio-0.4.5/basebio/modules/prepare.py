import time
import typer
from typing import Optional
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils.prepare import Prepare

app = typer.Typer()

@app.command()
def prepare(
    input: Annotated[str, typer.Option("--input", "-i", help="input dir path")],
    output: Annotated[str, typer.Option("--output", "-o", help="output dir path")],
    ref: Annotated[str, typer.Option("--ref", "-r", help="ref dir path")],
    species: Annotated[str, typer.Option("--species", "-s", help="Species name. [human|mouse|rat|other]")],
    prefix: Annotated[str, typer.Option("--prefix", "-p", help="Prefix for output file.")],
    control_names: Annotated[Optional[str], typer.Option("--control_names", "-c", help="Control sample rawname or rename separated by comma, such as 'raw1,raw2' or 'rename1,rename2'.")] = None,
    pipeline: Annotated[Optional[str], typer.Option("--pipeline", help="pipeline name.")] = None,
    renames: Annotated[Optional[str], typer.Option("--renames", help="rawname and rename of sample dir separated by comma, such as 'raw1:rename1,raw2:rename2,raw3:rename3,raw4:rename4'.")] = None,
    customer: Annotated[Optional[str], typer.Option("--customer", help="customer name of project.")] = None,
    detail: Annotated[Optional[str], typer.Option("--detail", help="Detail information of project.")] = None,
    support: Annotated[Optional[str], typer.Option("--support", help="Support information of project.")] = None,
    ):
    """
    Generate config file and init project structure.
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="Generate config file and init project structure...", total=None)
            start=time.time()
            
            prepare = Prepare(input_dir=input, output_dir=output, ref_dir=ref, species=species, prefix=prefix, control_names=control_names, pipeline=pipeline, renames=renames, customer=customer, detail=detail, support=support)
            prepare.init_structure()

            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"Generate config file and init project structure Done, time cost: {time_cost}")
            progress.add_task(description=f"Generate config file and init project structure Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="Generate config file and init project structure Failed", total=None)
            exit(1)