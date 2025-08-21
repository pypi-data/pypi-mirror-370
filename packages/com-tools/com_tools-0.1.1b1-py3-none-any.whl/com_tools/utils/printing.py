from typing import Any
import click
from com_tools.utils.enums import Colors


def print_result(result: Any):
    s_result =f"Résultat : {result}"
    l_result = len(s_result)
    h_line = "" + "-"*(l_result + 10) + ""
    click.echo(click.style(h_line, fg=Colors.GREEN.value))
    click.echo(click.style("|" + " "*4 +  s_result + " "*4 + "|", fg=Colors.GREEN.value))
    click.echo(click.style(h_line, fg=Colors.GREEN.value))


def print_error(result: Any):
    s_result =f"Erreur : {result}"
    l_result = len(s_result)
    h_line = "" + "-"*(l_result + 10) + ""
    click.echo(click.style(h_line, fg=Colors.RED.value))
    click.echo(click.style("|" + " "*4 +  s_result + " "*4 + "|", fg=Colors.RED.value))
    click.echo(click.style(h_line, fg=Colors.RED.value))