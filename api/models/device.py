from __future__ import annotations
from typing import Dict, List
import subprocess

from core.logger import setup_logger

logger = setup_logger()


class Device:
    """
    Represents a connected device.

    Attributes
    ----------
    id : str
        Unique identifier of the device.
    name : str
        Name or alias of the device (default is 'Unknown').
    product : str
        Product name of the deivice (default is 'Unknown').
    model : str
        Model name of the device (default is 'Unknown').
    device : str
        Device name (default is 'Unknown').
    """

    def __init__(
        self,
        id: str,
        name: str = "Unknown",
        product: str = "Unknown",
        model: str = "Unknown",
        device: str = "Unknown",
    ):
        """
        Initializes a Device instance.

        Parameters
        ----------
        id : str
            Unique identifier of the device.
        name : str
            Name or alias of the device (default is 'Unknown').
        product : str
            Product name of the deivice (default is 'Unknown').
        model : str
            Model name of the device (default is 'Unknown').
        device : str
            Device name (default is 'Unknown').
        """
        logger.debug("Define as informacoes dos dispositivos na classe")
        self.id = id
        self.name = name
        self.product = product
        self.model = model
        self.device = device

    @staticmethod
    def list_connected_devices() -> List[Device]:
        """
        Lists all connected devices using ADB (Android Debug Bridge).

        Returns
        -------
        List[Device]
            A list of Device objects representing connected devices.
        """
        logger.debug("Listar os dipositivos.")
        logger.debug("Executa o comando para listar os dispositivos conectados.")
        result = subprocess.run(
            ["adb", "devices", "-l"], capture_output=True, text=True
        )
        devices = []
        for line in result.stdout.splitlines()[1:]:
            if line.strip():
                parts = line.split()
                logger.debug(
                    "Obtem o id do dispositivo e defini o restante dos valores para 'Unknown' para evitar erros."
                )
                id = parts[0]
                product = model = device = "Unknown"

                logger.debug("Extract additional details using regex")
                for part in parts[2:]:
                    if part.startswith("product:"):
                        product = part.split(":", 1)[1]
                    elif part.startswith("model:"):
                        model = part.split(":", 1)[1]
                    elif part.startswith("device:"):
                        device = part.split(":", 1)[1]
                logger.debug(
                    "Adiciona um objeto na lista com as informacoes do dispositivos"
                )
                devices.append(
                    Device(
                        id=id, name=model, product=product, model=model, device=device
                    )
                )
            logger.info(
                f"Dispositivos listados:\n{'\n'.join([f'{i}. {device}' for i, device in enumerate(devices, start=1)])}"
            )
        return devices

    def to_dict(self) -> Dict[str, str]:
        """
        Converts the Device instance to a dictionary.

        Returns
        -------
        Dict[str, str]
            A dictionary with the device's datails.
        """
        logger.debug("Transforma as informacoes em um dicionario.")
        return {
            "id": self.id,
            "name": self.name,
            "product": self.product,
            "model": self.model,
            "device": self.device,
        }
