import time
import typer
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils.cmdtools import run_command

app = typer.Typer()

@app.command()
def run(
    command: Annotated[str, typer.Option("--cmd", "-c", help="The command to run.")], 
    use_shell: Annotated[bool, typer.Option("--shell", help="Use shell mode.")]=False,
    ):
    """
    Run a command in the terminal.
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="run command...", total=None)
            start=time.time()
            if use_shell:
                run_cmd = command
            else:
                run_cmd = command.split()
            run_command(run_cmd, use_shell=use_shell)
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"run command Done, time cost: {time_cost}")
            progress.add_task(description=f"run command Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="run command Failed", total=None)
            raise SystemExit(1) 
      
        