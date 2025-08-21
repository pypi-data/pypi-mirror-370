import click
from pydantic import BaseModel

from com_tools.base import ProtocolClient
from com_tools.profiles import ComProfile

from .client import ModbusReadRequest, create_client, ModbusWriteRequest

class ModbusConfig(BaseModel):
    pass

class ModbusComProfile(ComProfile):
    pass


@click.group()
def modbus() -> None:
    pass

# --- Serial Subcommand ---
@modbus.command()
@click.option('--port', required=True, help='Serial port (e.g., COM1 or /dev/ttyUSB0).')
@click.option('--baudrate', default=9600, type=int, help='Baud rate for serial communication.')
@click.option('--parity', default="E", type=str, help='Bus Parity.')
@click.option('--slave-id', default=1, type=int, help='Modbus slave ID.')
@click.argument('command_type', type=click.Choice(['read_coil', 'read_input_register', 'read_holding_register']), required=True)
@click.argument('address', type=int, required=True)
@click.argument('datatype', type=click.Choice(["int16", "int32", "int64", "float32", "float64"]), required=True)
def serial(port, baudrate, slave_id, parity, command_type, address, datatype) -> None:
    """
    Perform Modbus operations over serial.

    COMMAND_TYPE: The type of Modbus command (e.g., read_registers, write_coil).
    ADDRESS: The starting address for the Modbus operation.
    VALUE: The value to write (required for write commands).
    """
    click.echo(f"--- Serial Modbus Operation ---")
    click.echo(f"Port: {port}")
    click.echo(f"Baudrate: {baudrate}")
    click.echo(f"Parity: {parity}")
    click.echo(f"Slave ID: {slave_id}")
    click.echo(f"Command Type: {command_type}")
    click.echo(f"Address: {address}")
    click.echo(f"Datatype: {datatype}")

    if command_type == 'read_coil':
        click.echo(f"Action: Reading Coil from address {address}")
        # Add your pymodbus serial read logic here
        # Example: client = ModbusSerialClient(port=port, baudrate=baudrate, ...)
        # result = client.read_holding_registers(address, count=1, unit=slave_id)
        # click.echo(f"Read result: {result.registers}")
    elif command_type == 'read_input_register':
        click.echo(f"Action: Reading input registers from address {address}")
        # Add your pymodbus serial read logic here
        # Example: client = ModbusSerialClient(port=port, baudrate=baudrate, ...)
        # result = client.read_holding_registers(address, count=1, unit=slave_id)
        # click.echo(f"Read result: {result.registers}")
    elif command_type == 'read_holding_register':
        click.echo(f"Action: Reading holding registers from address {address}")
        client: ProtocolClient = create_client("serial", port=port, baudrate=baudrate, parity=parity)
        request = ModbusReadRequest(
            function="read_holding_register",
            device_id=slave_id,
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
@click.option('--host', default='localhost', help='Modbus TCP server host.')
@click.option('--port', default=502, type=int, help='Modbus TCP server port.')
@click.option('--slave-id', default=1, type=int, help='Modbus slave ID.')
@click.argument('command_type', type=click.Choice(['read_coil', 'read_input_register', 'read_holding_register']), required=True)
@click.argument('address', type=int, required=True)
@click.argument('value', type=int, required=False) # Optional for write commands
def tcp(host, port, slave_id, command_type, address, value) -> None:
    """
    Perform Modbus operations over TCP.

    COMMAND_TYPE: The type of Modbus command (e.g., read_input_registers, write_register).
    ADDRESS: The starting address for the Modbus operation.
    VALUE: The value to write (required for write commands).
    """
    click.echo(f"--- TCP Modbus Operation ---")
    click.echo(f"Host: {host}")
    click.echo(f"Port: {port}")
    click.echo(f"Slave ID: {slave_id}")
    click.echo(f"Command Type: {command_type}")
    click.echo(f"Address: {address}")

    if command_type == 'read_coil':
        click.echo(f"Action: Reading coil from address {address}")
        # Add your pymodbus TCP read logic here
        # Example: client = ModbusTcpClient(host, port=port)
        # result = client.read_input_registers(address, count=1, unit=slave_id)
        # click.echo(f"Read result: {result.registers}")
    elif command_type == 'read_input_register':
        click.echo(f"Action: Reading input registers from address {address}")
        # Add your pymodbus TCP read logic here
        # Example: client = ModbusTcpClient(host, port=port)
        # result = client.read_input_registers(address, count=1, unit=slave_id)
        # click.echo(f"Read result: {result.registers}")
    elif command_type == 'read_holding_register':
        click.echo(f"Action: Reading holding registers from address {address}")
        # Add your pymodbus TCP read logic here
        # Example: client = ModbusTcpClient(host, port=port)
        # result = client.read_input_registers(address, count=1, unit=slave_id)
        # click.echo(f"Read result: {result.registers}")
    else:
        click.echo(click.style(f"Unknown command type: {command_type}", fg='red'))