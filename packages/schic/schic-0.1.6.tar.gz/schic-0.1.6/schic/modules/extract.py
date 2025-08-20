import time
import typer
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils.umitools import extract_run

app = typer.Typer()

@app.command()
def extract(
    bc_pattern: Annotated[str, typer.Option("--bc-pattern", help="Barcode pattern for paired reads.")],
    stdin: Annotated[str, typer.Option("--stdin", "-I", help="file to read stdin from.")],
    stdout: Annotated[str, typer.Option("--stdout", "-S", help="file where output.")],
    read2_in: Annotated[str, typer.Option("--read2-in", "-R2", help="file to read read2 from.")],
    read2_out: Annotated[str, typer.Option("--read2-out", "-R2O", help="file where read2 output.")],
    whitelist: Annotated[str, typer.Option("--whitelist", help="file containing whitelist barcodes.")],
    tool: Annotated[str, typer.Option("--tool", help="umi_tools.")]="umi_tools",
    tool_command: Annotated[str, typer.Option("--command", help="umi_tools command for extract.")]="extract",
    parms: Annotated[str, typer.Option("--parms", help="umi_tools parameters for extract.")]="--extract-method=regex --filter-cell-barcode",
    ):
    """
    Extract UMI and cell barcode from single-cell Hi-C paired-end reads data.
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="extract UMI...", total=None)
            start=time.time()
            extract_run(bc_pattern, stdin, stdout,read2_in, read2_out, whitelist, tool, tool_command, parms)
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"extract UMI Done, time cost: {time_cost}")
            progress.add_task(description=f"extract UMI Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="extract UMI Failed", total=None)
            exit(1)
    