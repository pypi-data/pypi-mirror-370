import time
import typer
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils.db import ProgramMonitor

app = typer.Typer()

@app.command()
def query(
    url: Annotated[str, typer.Option("--url", help="PostgreSQL URL.")], 
    max_retries: Annotated[int, typer.Option("--max-retries", "-m", help="Max retries.")]=3,
    retry_interval: Annotated[int, typer.Option("--retry-interval", "-i", help="Retry interval in seconds.")]=5,
    program_id: Annotated[int, typer.Option("--program-id", "-p", help="Program ID.")]=None
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
            progress.add_task(description="query db...", total=None)
            start=time.time()
            
            monitor = ProgramMonitor(
                url,
                max_retries=max_retries,
                retry_interval=retry_interval
            )
            # 创建示例程序
            # program_id = monitor.create_program(
            #     user_id=1001,
            #     program_name="Nightly Backup",
            #     stages=["Init", "Compress", "Upload", "Cleanup"]
            # )
            
            # # 更新阶段状态
            # monitor.update_stage_status(program_id, 1, 'in_progress')
            # monitor.update_stage_status(program_id, 1, 'completed')
            
            # 查询进度
            progress = monitor.get_progress(program_id)
            print(f"Current Progress: {progress}")
            
            # 删除程序（示例）
            # monitor.delete_program(program_id)
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"query db Done, time cost: {time_cost}")
            progress.add_task(description=f"query db Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="query db Failed", total=None)
            raise SystemExit(1) 

@app.command()
def create(
    url: Annotated[str, typer.Option("--url", help="PostgreSQL URL.")], 
    max_retries: Annotated[int, typer.Option("--max-retries", "-m", help="Max retries.")]=3,
    retry_interval: Annotated[int, typer.Option("--retry-interval", "-i", help="Retry interval in seconds.")]=5,
    user_id: Annotated[int, typer.Option("--user-id", "-u", help="User ID.")]=None,
    program_name: Annotated[str, typer.Option("--program-name", "-n", help="Program name.")]=None,
    stages: Annotated[str, typer.Option("--stages", "-s", help="Program stages.")]=None
    ):
    """
    Create a program in the database.
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="create program...", total=None)
            start=time.time()
            monitor = ProgramMonitor(
                url,
                max_retries=max_retries,
                retry_interval=retry_interval
            )
            program_id = monitor.create_program(
                user_id=user_id,
                program_name=program_name,
                stages=stages.split()
            )
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"create program Done, program_id: {program_id}, time cost: {time_cost}")
            progress.add_task(description=f"create program Done, program_id: {program_id}, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="create program Failed", total=None)
            raise SystemExit(1) 

@app.command()
def update(
    url: Annotated[str, typer.Option("--url", help="PostgreSQL URL.")], 
    max_retries: Annotated[int, typer.Option("--max-retries", "-m", help="Max retries.")]=3,
    retry_interval: Annotated[int, typer.Option("--retry-interval", "-i", help="Retry interval in seconds.")]=5,
    program_id: Annotated[int, typer.Option("--program-id", "-p", help="Program ID.")]=None,
    stage_order: Annotated[int, typer.Option("--stage-order", "-o", help="Stage order.")]=None,
    new_status: Annotated[str, typer.Option("--new-status", "-s", help="New status.")]=None
    ):
    """
    Update a program stage status in the database.
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="update stage status...", total=None)
            start=time.time()
            monitor = ProgramMonitor(
                url,
                max_retries=max_retries,
                retry_interval=retry_interval
            )
            monitor.update_stage_status(
                program_id=program_id,
                stage_order=stage_order,
                new_status=new_status
            )
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"update stage status Done, time cost: {time_cost}")
            progress.add_task(description=f"update stage status Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="update stage status Failed", total=None)
            raise SystemExit(1) 

@app.command()
def delete(
    url: Annotated[str, typer.Option("--url", help="PostgreSQL URL.")], 
    max_retries: Annotated[int, typer.Option("--max-retries", "-m", help="Max retries.")]=3,
    retry_interval: Annotated[int, typer.Option("--retry-interval", "-i", help="Retry interval in seconds.")]=5,
    program_id: Annotated[int, typer.Option("--program-id", "-p", help="Program ID.")]=None
    ):
    """
    Delete a program in the database.
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="delete program...", total=None)
            start=time.time()
            monitor = ProgramMonitor(
                url,
                max_retries=max_retries,
                retry_interval=retry_interval
            )
            monitor.delete_program(program_id)
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"delete program Done, time cost: {time_cost}")
            progress.add_task(description=f"delete program Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="delete program Failed", total=None)
            raise SystemExit(1) 