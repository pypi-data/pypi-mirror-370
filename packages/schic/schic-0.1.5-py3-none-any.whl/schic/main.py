import typer
from .modules.whitelist import whitelist
from .modules.extract import extract
from .modules.cutadapt import cutadapt_run
from .modules.contacts import contacts
from .modules.report import report

app = typer.Typer(add_completion=False)

@app.callback()
def callback():
    """
    scHiC pipeline for single-cell Hi-C data processing.
    """

app.command(name="whitelist")(whitelist)
app.command(name="extract")(extract)
app.command(name="cutadapt")(cutadapt_run)
app.command(name="contacts")(contacts)
app.command(name="report")(report)



if __name__ == "__main__":
    app()