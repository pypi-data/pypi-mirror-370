from typing import List

from pydantic import BaseModel
import serial.tools.list_ports


def list_serial_ports() -> List[str]:
    """
    Lists available serial ports on the system.

    Returns:
        list: A list of available COM ports, where each item is a PortInfo object.
              Returns an empty list if no ports are found.
    """
    # Use serial.tools.list_ports.comports() to get a list of all available ports
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        return []
    return list(map(lambda p: p.name, ports))


if __name__ == "__main__":
    list_serial_ports()
