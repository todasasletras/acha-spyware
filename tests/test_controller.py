import subprocess
from app.controllers.mvt_controller import MVTController

def test_check_adb(mocker):
    """
    Test the MVTController.check_adb method.

    Mocks the subprocess.run call to simulate the execution of the ADB check command.
    Ensures the method correctly processes the output and returns a successful result.

    Parameters
    ----------
    mocker : pytest_mock
        Pytest-mock object for mocking external dependencies.
    """
    # Mock output simulating the subprocess.run stdout for ADB check
    mock_output = "Checking connected devices...\nNo issues found."
    mocker.patch(
        'subprocess.run',
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=mock_output, stderr="")
    )

    # Call the method and check the result
    result = MVTController.check_adb("/output/dir")
    assert result['success'] is True  # Ensure success is True
    assert result['stdout'] == mock_output  # Check if stdout matches the mock output
    assert 'stderr' not in result or result['stderr'] == ""  # stderr should be empty or absent

def test_check_apk(mocker):
    """
    Test the MVTController.check_apk method.

    Mocks the subprocess.run call to simulate the execution of the APK analysis command.
    Ensures the method correctly processes the output and returns a successful result.

    Parameters
    ----------
    mocker : pytest_mock
        Pytest-mock object for mocking external dependencies.
    """
    # Mock output simulating the subprocess.run stdout for APK analysis
    mock_output = "Analyzing APK...\nNo threats detected."
    mocker.patch(
        'subprocess.run',
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=mock_output, stderr="")
    )

    # Call the method and check the result
    result = MVTController.check_apk("/path/to/apk.apk", "/output/dir")
    assert result['success'] is True  # Ensure success is True
    assert result['stdout'] == mock_output  # Check if stdout matches the mock output
    assert 'stderr' not in result or result['stderr'] == ""  # stderr should be empty or absent
