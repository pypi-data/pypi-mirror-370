from email.policy import default
from typing import List
import click



@click.group()
def demo() -> None:
    pass


@demo.command()
@click.option("--profile", type=str)
def message(profile: str,):
    pass


