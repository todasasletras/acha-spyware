import subprocess
from app.models.device import Device

def test_list_connected_devices(mocker):
    """
    Test the Device.list_connected_devices method.

    Mocks the subprocess.run call to simulate the `adb devices -l` command.
    Ensures the method parses the output correctly and returns a list of Device objects.

    Parameters
    ----------
    mocker : pytest_mock
        Pytest-mock object for mocking external dependencies.
    """
    # Mock output simulating `adb devices -l` command output
    mock_output = """\
List of devices attached
emulator-5554             device usb:1-3 product:hawaiip_g model:ios device:hawaiip transport_id:1
"""
    # Mock the subprocess.run call to return the mocked output
    mocker.patch(
        'subprocess.run',
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=mock_output)
    )

    # Call the method and verify the result
    devices = Device.list_connected_devices()
    assert len(devices) == 1  # Ensure one device is detected
    assert devices[0].id == "emulator-5554"  # Verify device ID
    assert devices[0].name == "ios"  # Verify device name (model)
    assert devices[0].product == "hawaiip_g"  # Verify product
    assert devices[0].device == "hawaiip"  # Verify device type
    assert devices[0].model == "ios"  # Verify model

def test_device_to_dict():
    """
    Test the Device.to_dict method.

    Verifies that the method correctly converts a Device object into a dictionary
    with the appropriate attributes and default values for missing fields.
    """
    # Create a Device object with some attributes set
    device = Device(id="emulator-5554", name="Test Device")

    # Convert the device to a dictionary and verify the result
    device_dict = device.to_dict()
    assert device_dict == {
        "id": "emulator-5554",  # Verify device ID
        "name": "Test Device",  # Verify device name
        "device": "Unknown",  # Default value for device type
        "model": "Unknown",  # Default value for model
        "product": "Unknown"  # Default value for product
    }
