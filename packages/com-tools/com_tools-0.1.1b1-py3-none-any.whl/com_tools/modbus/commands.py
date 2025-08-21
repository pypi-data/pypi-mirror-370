from importlib.metadata import requires
import time
import click
from pydantic import BaseModel
from InquirerPy import inquirer


from com_tools.base import ProtocolClient
from com_tools.profiles import ComProfile
from com_tools.utils.listings import list_serial_ports
from com_tools.utils.enums import Colors
from com_tools.utils.printing import print_error, print_result
from .profiles import ModbusReadRequest, create_client, ModbusWriteRequest

class ModbusConfig(BaseModel):
    pass

class ModbusComProfile(ComProfile):
    pass


@click.group()
def modbus() -> None:
    """
    Execute une requête Modbus.
    Vous pouvez utiliser serial ou tcp commme type de communication. 
    Ensuite, référencez les paramètres de la communication en utilisant des --<mon-paramètre>\n
    ⏩ Exemple:\n
    com-tools modbus serial --port COM1 --baudrate 9600 read_coil 1 3200\n
    Effectuera une requête de type "read_coil" sur le device_id 1 à l'adresse 3200 en utilisant un transport seriel sur le port COM1 et  un baudrate de 9600. 
    Notez que les autres paramètres seront ceux par défaut (voir --help après serial ou tcp).
    """
    pass

# --- Serial Subcommand ---
@modbus.command()
@click.option('--port', default=None, help='Port sériel', show_default=True)
@click.option('--baudrate', default=9600, type=int, help='Baudrate.', show_default=True)
@click.option('--parity', default="E", type=str, help='Parité du bus.', show_default=True)
@click.argument('command_type', type=click.Choice(['read_coil', 'read_input_register', 'read_holding_register']), required=True)
@click.argument("device_id", default=1, type=int)
@click.argument('address', type=int, required=True)
@click.argument('datatype', type=click.Choice(["int16", "int32", "int64", "float32", "float64"]), required=True)
def serial(port, baudrate, device_id, parity, command_type, address, datatype) -> None:

    if port is None:
        click.echo(click.style(f"⚠ Attention, vous n'avez pas spécifié de port.", fg=Colors.YELLOW.value))
        _available_serial_port = list_serial_ports()
        if len(_available_serial_port) == 0:
            click.echo(click.style(f"Aucun port seriel disponnible 😥", fg=Colors.RED.value))
        port = inquirer.select(
            message="Choisissez un port:",
            choices=_available_serial_port,
            default=_available_serial_port[0]
        ).execute()

    click.echo(
        f"""------- Recapitulatif Setup ------------------------------
        Port: {port}
        Baudrate: {baudrate}
        Parity: {parity}
        Slave ID: {device_id}
        Command Type: {command_type}
        Address: {address}
        Datatype: {datatype}
        {command_type} on {device_id=} to {address=} and decoding as {datatype}
---------------------------------------------------------------------"""
    )
    if command_type == 'read_coil':
        click.echo(f"Action: Reading holding registers from address {address}")
        client: ProtocolClient = create_client("serial", port=port, baudrate=baudrate, parity=parity)
        request = ModbusReadRequest(
            function="read_coil",
            device_id=device_id,
            address=address,
            datatype=datatype
        )
        with client as clt:
            response = clt.request(request)
            if response.status.value:
                click.echo(f"Modbus id {request.device_id}: {request.function} ({request.address}) => {response.content}")
            else:
                click.echo(click.style(f"Error reading modbus => {response.content}", fg="red"))
    elif command_type == 'read_input_register':
        click.echo(f"Action: Reading holding registers from address {address}")
        client: ProtocolClient = create_client("serial", port=port, baudrate=baudrate, parity=parity)
        request = ModbusReadRequest(
            function="read_input_register",
            device_id=device_id,
            address=address,
            datatype=datatype
        )
        with client as clt:
            response = clt.request(request)
            if response.status.value:
                click.echo(f"Modbus id {request.device_id}: {request.function} ({request.address}) => {response.content}")
            else:
                click.echo(click.style(f"Error reading modbus => {response.content}", fg="red"))

    elif command_type == 'read_holding_register':
        click.echo(f"Action: Reading holding registers from address {address}")
        client: ProtocolClient = create_client("serial", port=port, baudrate=baudrate, parity=parity)
        request = ModbusReadRequest(
            function="read_holding_register",
            device_id=device_id,
            address=address,
            datatype=datatype
        )
        with client as clt:
            response = clt.request(request)
            if response.status.value:
                click.echo(f"Modbus id {request.device_id}: {request.function} ({request.address}) => {response.content}")
            else:
                click.echo(click.style(f"Error reading modbus => {response.content}", fg="red"))
    else:
        click.echo(click.style(f"Unknown command type: {command_type}", fg='red'))


# --- TCP Subcommand ---
@modbus.command()
@click.option('--host', help='Host IP address', type=str)
@click.option('--port', default=502, type=int, help='Port.', show_default=True)
@click.option('--timeout', default=1.5, type=float, help='Timeout.', show_default=True)
@click.argument('command_type', type=click.Choice(['read_coil', 'read_input_register', 'read_holding_register']), required=True)
@click.argument("device_id", default=1, type=int)
@click.argument('address', type=int, required=True)
@click.argument('datatype', type=click.Choice(["bits", "int16", "int32", "int64", "float32", "float64"]), default="bits")
def tcp(host, port, timeout, command_type, device_id, address, datatype) -> None:
    click.echo(
        f"""------- Recapitulatif Setup ------------------------------
        Host: {host}
        Port: {port}
        Timeout: {timeout}
        Slave ID: {device_id}
        Command Type: {command_type}
        Address: {address}
        Datatype: {datatype}
        {command_type} on {device_id=} to {address=} and decoding as {datatype}
---------------------------------------------------------------------"""
    )
    client: ProtocolClient = create_client("tcp", host=host, port=port)
    if command_type == 'read_coil':
        click.echo(f"Reading holding registers from address {address}")
        request = ModbusReadRequest(
            function="read_coil",
            device_id=device_id,
            address=address,
            datatype=datatype
        )
        with client as clt:
            response = clt.request(request)
            if response.status.value:
                print_result(f"Modbus id {request.device_id}: {request.function} ({request.address}) => {response.content}")
            else:
                print_error(f"{response.content}")
    elif command_type == 'read_input_register':
        click.echo(f"Reading holding registers from address {address}")
        request = ModbusReadRequest(
            function="read_input_register",
            device_id=device_id,
            address=address,
            datatype=datatype
        )
        with client as clt:
            response = clt.request(request)
            if response.status.value:
                print_result(f"Modbus id {request.device_id}: {request.function} ({request.address}) => {response.content}")
            else:
                print_error(f"{response.content}")

    elif command_type == 'read_holding_register':
        click.echo(f"Reading holding registers from address {address}")
        request = ModbusReadRequest(
            function="read_holding_register",
            device_id=device_id,
            address=address,
            datatype=datatype
        )
    else:
        print_error(f"Unknown command type: {command_type}")
        raise ValueError(f"Unknown command type: {command_type}")
     
    with client as clt:
        response = clt.request(request)
        if response.status.value:
            print_result(f"Modbus id {request.device_id}: {request.function} ({request.address}) => {response.content}")
        else:
            print_error(f"Error reading modbus => {response.content}")