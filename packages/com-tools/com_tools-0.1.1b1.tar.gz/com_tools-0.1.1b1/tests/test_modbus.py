import logging
import pytest

from com_tools.modbus.profiles import ModbusClient, ModbusReadRequest, create_client

@pytest.fixture
def client() -> ModbusClient:
    return create_client(
        "serial",
        baudrate=19200,
        stopbits=1,
        port="COM3",
        parity="E",
        framer="rtu"

    )

def test_read_registers(client: ModbusClient) -> None:
    request = ModbusReadRequest(
        function="read_holding_register",
        device_id=1,
        address=3203,
        datatype="int64"
    )
    with client as c:
        response = c.request(request)

    logging.info(f"Modbus id {request.device_id}: {request.function} ({request.address}) => {response.content}")

def test_read_registers_2(client: ModbusClient) -> None:
    request = ModbusReadRequest(
        function="read_holding_register",
        device_id=1,
        address=3027,
        datatype="float32"
    )
    with client as c:
        response = c.request(request)

    logging.info(f"Modbus id {request.device_id}: {request.function} ({request.address}) => {response.content}")