import time
import typer
from typing_extensions import Annotated
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..utils.umitools import whitelist_run

app = typer.Typer()

@app.command()
def whitelist(
    bc_pattern: Annotated[str, typer.Option("--bc-pattern", help="Barcode pattern for paired reads.")],
    stdin: Annotated[str, typer.Option("--stdin", "-I", help="file to read stdin from.")],
    set_cell_number: Annotated[int, typer.Option("--set-cell-number", "-S", help="setting cell number.")]=5000,
    plot_prefix: Annotated[str, typer.Option("--plot-prefix", help="prefix of plot files.")]="whitelist",
    stdout: Annotated[str, typer.Option("--stdout", help="file to write stdout to.")]="whitelist.txt",
    tool: Annotated[str, typer.Option("--tool", help="umi_tools.")]="umi_tools",
    tool_command: Annotated[str, typer.Option("--command", help="umi_tools command for whitelist.")]="whitelist",
    parms: Annotated[str, typer.Option("--parms", help="umi_tools parameters for whitelist.")]="--method=reads --ed-above-threshold=correct --extract-method=regex --knee-method=density --random-seed=123",
    ):
    """
    UMI whitelist generation from single-cell Hi-C paired-end reads data.
    """
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        try:
            progress.add_task(description="UMI whitelist generation...", total=None)
            start=time.time()
            whitelist_run(bc_pattern, stdin, set_cell_number, plot_prefix, stdout, tool, tool_command, parms)
            end=time.time()
            time_cost=f"{(end - start) // 3600}h{((end - start) % 3600) // 60}m{(end - start) % 60:.2f}s"
            print(f"UMI whitelist generation Done, time cost: {time_cost}")
            progress.add_task(description=f"UMI whitelist generation Done, time cost: {time_cost}", total=None)
        except Exception as e:
            print(f"Error: {e}")
            progress.add_task(description="UMI whitelist generation Failed", total=None)
            exit(1)
    