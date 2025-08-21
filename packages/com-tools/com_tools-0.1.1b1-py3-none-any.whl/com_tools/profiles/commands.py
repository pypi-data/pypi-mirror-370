from enum import Enum
from typing import List
import click
 
from com_tools.utils.enums import YesOrNo, Colors
from com_tools._protocols import SupportedProtocols
from com_tools.profiles import ComProfile, ProfileRepo, pass_repo_context
from com_tools.loggers import logger


@click.group()
@pass_repo_context
def profile(repo: ProfileRepo) -> None:
    pass


@profile.command("set")
@click.option("--name", prompt="Choose client's name")
@click.option("--protocol", prompt="Choose client's protocol ", type=click.Choice(SupportedProtocols))
@pass_repo_context
def create_profile(repo: ProfileRepo, name: str, protocol: str, color: Colors=None) -> None:
    config = {
        "name": name,
        "protocol": protocol,
        "config": {}

    }
    client = ComProfile.model_validate(config)

    if client in repo:
        erase = click.prompt(click.style(f"The profile {name} already exists. Do you want to replace it ?", fg="yellow"), type=YesOrNo)
        click.echo(f"You choose {erase}")
        if erase == YesOrNo.NO:
            click.echo(f"❌ Client not saved. ❌")
            return
        
    repo.add_profile(client)
    click.echo(click.style(f"✅ '{name}' saved to profile ! ✅", fg="green"))


@profile.command("get")
@click.option("--name", prompt="Enter client's name")
@pass_repo_context
def get_profile(repo: ProfileRepo, name: str) -> ComProfile:
    pass


@profile.command("list")
@pass_repo_context
def list_profile(repo: ProfileRepo) -> List[str]:
    for index, profile in enumerate(repo.list_profiles().keys()):
        click.echo(f"{index+1}. {profile}")

