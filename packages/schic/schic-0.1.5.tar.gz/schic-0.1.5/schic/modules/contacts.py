import time
import typer
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils.pairtools import pairtools

app = typer.Typer()

@app.command()
def contacts(
    read1: Annotated[str, typer.Option("--read1", help="read1 file.")],
    read2: Annotated[str, typer.Option("--read2", help="read2 file.")],
    reference: Annotated[str, typer.Option("--reference", "-r", help="reference file.")],
    genome_size: Annotated[str, typer.Option("--genome-size", "-g", help="genome size.")],
    prefix: Annotated[str, typer.Option("--prefix", help="outfile prefix.")],
    threads: Annotated[int, typer.Option("--threads", help="threads number.")]=8,
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
            pairtools(read1, read2, reference, genome_size, prefix, threads)
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"Build contact matrix Done, time cost: {time_cost}")
            progress.add_task(description=f"Build contact matrix Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="Build contact matrix Failed", total=None)
            exit(1)
    