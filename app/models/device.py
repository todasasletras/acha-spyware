from __future__ import annotations
from typing import Dict, List
import subprocess

class Device:
    """
    Represents a connected device.

    Attributes
    ----------
    id : str
        Unique identifier of the device.
    name : str
        Name or alias of the device (default is 'Unknown').
    """

    def __init__(self, id: str, name: str):
        """
        Initializes a Device instance.

        Parameters
        ----------
        id : str
            Unique identifier of the device.
        name : str
            Name or alias of the device.
        """
        self.id = id
        self.name = name

    @staticmethod
    def list_connected_devices() -> List[Device]:
        """
        Lists all connected devices using ADB (Android Debug Bridge).

        Returns
        -------
        List[Device]
            A list of Device objects representing connected devices.
        """
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = []
        for line in result.stdout.splitlines()[1:]:
            if line.strip():
                parts = line.split()
                devices.append(Device(id=parts[0], name="Unknown"))
        return devices

    def to_dict(self) -> Dict[str, str]:
        """
        Converts the Device instance to a dictionary.

        Returns
        -------
        Dict[str, str]
            A dictionary with the device's id and name.
        """
        return {'id': self.id, 'name': self.name}
