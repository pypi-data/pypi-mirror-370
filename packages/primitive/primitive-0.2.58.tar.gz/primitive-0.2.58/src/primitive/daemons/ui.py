from rich.console import Console
from rich.table import Table
from typing import List

from ..utils.daemons import Daemon


def render_daemon_list(daemons: List[Daemon]) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold #FFA800")
    table.add_column("Name")
    table.add_column("Label")
    table.add_column("Installed")
    table.add_column("Active")
    table.add_column("File Path")
    table.add_column("Log Path")

    for daemon in daemons:
        child_table = Table(show_header=False, header_style="bold #FFA800")
        child_table.add_column("Name")
        child_table.add_column("Label")
        child_table.add_column("Installed")
        child_table.add_column("Active")
        child_table.add_column("File Path")
        child_table.add_column("Log Path")

        table.add_row(
            daemon.name,
            daemon.label,
            "[bold green]Yes[/bold green]"
            if daemon.is_installed()
            else "[bold red]No[/bold red]",
            "[bold green]Yes[/bold green]"
            if daemon.is_active()
            else "[bold red]No[/bold red]",
            str(daemon.file_path),
            str(daemon.logs),
        )

    console.print(table)
