import click
import com_tools
from .modbus.commands import modbus
from .demo.commands import demo
from .profiles import ProfileRepo, pass_repo_context
from .profiles.commands import profile


# Define the main group for the CLI

@click.group()
@pass_repo_context
def comtools(repo: ProfileRepo) -> None:
    """Communique avec plusieurs protocols supporté.
    """
    

def main() -> None:
    comtools()


comtools.add_command(modbus)
comtools.add_command(demo)
comtools.add_command(profile)

