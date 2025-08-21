from __future__ import annotations
from typing import Literal, Optional

from pydantic import BaseModel, field_validator
import click

import pymodbus.client as PyModbusClient
from pymodbus import FramerType, ModbusException    
from pymodbus.client.mixin import ModbusClientMixin

from com_tools.base import RequestResponse, RequestResult


ModbusFunctions = Literal["read_coil", "read_input_register", "read_holding_register", "write_coil", "write_register"]


class ModbusReadRequest(BaseModel):
    function: ModbusFunctions
    device_id: int
    address: int
    datatype: str | ModbusClientMixin.DATATYPE
    size: Optional[int] = -1
    word_order: Literal["little", "big"] = "big"

    @field_validator("datatype")
    def transform_in_valid_datatype(cls, v: str) -> None:
        return v if isinstance(v, ModbusClientMixin.DATATYPE) else ModbusClientMixin.DATATYPE._member_map_[v.upper()]
    
    def model_post_init(self, __context) -> None:
        if (register_size := self.datatype.value[1]):
            self.size =  register_size

class ModbusWriteRequest(BaseModel):
    function: ModbusFunctions
    device_id: int
    address: int
    datatype: str | ModbusClientMixin.DATATYPE
    size: Optional[int] = -1
    word_order: Literal["little", "big"] = "big"

    @field_validator("datatype")
    def transform_in_valid_datatype(cls, v: str) -> None:
        return v if isinstance(v, ModbusClientMixin.DATATYPE) else ModbusClientMixin.DATATYPE._member_map_[v.upper()]
    
    def model_post_init(self, __context) -> None:
        if (register_size := self.datatype.value[1]):
            self.size =  register_size


class ModbusClient:

    def __init__(self, client: PyModbusClient.ModbusBaseSyncClient):
        self._client = client

    def __enter__(self) -> None:
        self._client.connect()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._client.close()
    
    def request(self, request: ModbusReadRequest | ModbusWriteRequest) -> RequestResponse:
        if isinstance(request, ModbusReadRequest):
            return self.execute_read_request(request)
        elif isinstance(request, ModbusWriteRequest):
            return self.execute_read_request(request)
    def connect(self) -> None:
        self._client.connect()

    def execute_read_request(self, request: ModbusReadRequest) -> RequestResponse:
        if request.function == "read_holding_register":
            try:
                click.echo(f"Requestion {request} with {self._client}")
                response = self._client.read_holding_registers(
                    address=request.address,
                    count=request.size,
                    device_id=request.device_id
                )
                if response.isError():
                    return RequestResponse(
                        status=RequestResult.FAILED,
                        content=f"Modbsu request failed with {response.exception_code()}"
                    )
                try:
                    decoded = self._client.convert_from_registers(
                        registers=response.registers,
                        data_type=request.datatype,
                        word_order=request.word_order
                    )
                    return RequestResponse(
                        status=RequestResult.SUCCESS,
                        content=decoded
                    )
                except Exception as err:
                    return RequestResponse(
                    status=RequestResult.FAILED,
                    content=err
                ) 
            except Exception as err:
                return RequestResponse(
                    status=RequestResult.FAILED,
                    content=err
                )

    @classmethod
    def create_serial_client(
        cls,
        port: str,
        framer: Literal["rtu", "ascii"],
        baudrate: Literal[300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200],
        bytesize: Literal[7, 8],
        parity: Literal['N','E','O'],
        stopbits: int,
        timeout: float
    ) -> PyModbusClient.ModbusSerialClient:
        return cls(client=PyModbusClient.ModbusSerialClient(
            port=port,
            framer=FramerType.RTU if framer == "rtu" else FramerType.ASCII,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout
        ))

    @classmethod
    def create_tcp_client(
        cls,
        host: str,
        port: int,
        timeout: float
    ) -> PyModbusClient.ModbusTcpClient:
        return cls(client=PyModbusClient.ModbusTcpClient(
            host=host,
            framer=FramerType.SOCKET,
            port=port,
            timeout=timeout
        ))


def create_client(type: Literal["serial", "tcp"], **kwargs) -> ModbusClient:
    if type == "tcp":
        return ModbusClient.create_tcp_client(
                host=kwargs.get("host", "127.0.0.1"),
                port=kwargs.get("port", 502),
                timeout=kwargs.get("timeout", 1.5)
            )
    elif type == "serial":
        return ModbusClient.create_serial_client(
            port=kwargs.get("port",),
            framer=FramerType.RTU if kwargs.get("framer","rtu") == "rtu" else FramerType.ASCII,
            timeout=kwargs.get("timeout", 1.5),
            baudrate=kwargs.get("baudrate", 9600),
            bytesize=kwargs.get("bytesize", 8),
            parity=kwargs.get("parity", "E"),
            stopbits=kwargs.get("stopbits", 1),
        )
    else:
        print(f"Unknown client {type} selected")
        return

