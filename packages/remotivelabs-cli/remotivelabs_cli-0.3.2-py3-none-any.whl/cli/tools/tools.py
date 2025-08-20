from cli.typer import typer_utils

from .can.can import app as can_app

HELP_TEXT = """
CLI tools unrelated to cloud or broker
"""

app = typer_utils.create_typer(help=HELP_TEXT)
app.add_typer(can_app, name="can", help="CAN tools")
