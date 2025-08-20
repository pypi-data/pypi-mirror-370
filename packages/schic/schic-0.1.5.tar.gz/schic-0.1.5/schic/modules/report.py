import time
import typer
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from basebio import cutadapt as cutadapt_run

app = typer.Typer()

@app.command()
def report(
    read1: Annotated[str, typer.Option("--read1", help="read1 file.")],
    read2: Annotated[str, typer.Option("--read2", help="read2 file.")],
    read1_out: Annotated[str, typer.Option("--read1-out", help="output file for read1.")],
    read2_out: Annotated[str, typer.Option("--read2-out", help="output file for read2.")],
    tool: Annotated[str, typer.Option("--tool", help="cutadapt.")]="cutadapt",
    parms: Annotated[str, typer.Option("--parms", help="cutadapt parameters for whitelist.")]="-m 10 -a CTGTCTCTTATACACATCT -A CTGTCTCTTATACACATCT -G GACCGCTTGGCCTCCGACTTAGATGTGTATAAGAGACAG",
    ):
    """
    Build contact matrix from single-cell Hi-C paired-end reads data.
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="Build contact matrix...", total=None)
            start=time.time()
            cutadapt_run(read1, read2, read1_out, read2_out, tool, parms)
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"Build contact matrix Done, time cost: {time_cost}")
            progress.add_task(description=f"Build contact matrix Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="Build contact matrix Failed", total=None)
            exit(1)
    