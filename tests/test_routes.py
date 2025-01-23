import subprocess
import pytest
from app import create_app

@pytest.fixture
def client():
    """
    Pytest fixture to create a test client for the Flask application.

    Sets the app in TESTING mode and provides a client instance to use in tests.
    """
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_check_adb_route(client, mocker):
    """
    Test the /check-adb route.

    Mocks the subprocess.run call to simulate the MVTController.check_adb behavior.
    Ensures the endpoint correctly returns the expected JSON response.

    Parameters
    ----------
    client : FlaskClient
        Test client provided by the pytest fixture.
    mocker : pytest_mock
        Pytest-mock object for mocking external dependencies.
    """
    # Mock output simulating subprocess.run stdout for ADB check
    mock_output = "Checking connected devices...\nNo issue found."
    mocker.patch(
        'subprocess.run',
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=mock_output, stderr="")
    )

    response = client.post('/check-adb', json={"output_dir": "output_dir"})
    assert response.status_code == 200  # Asserts successful HTTP response
    data = response.get_json()
    assert data['success'] is True  # Confirms success key in response
    assert data['stdout'] == mock_output  # Checks stdout matches mock output

def test_check_apk_route(client, mocker):
    """
    Test the /check-apk route.

    Mocks the subprocess.run call to simulate the MVTController.check_apk behavior.
    Ensures the endpoint correctly handles the provided file path and output directory,
    and returns the expected JSON response.

    Parameters
    ----------
    client : FlaskClient
        Test client provided by the pytest fixture.
    mocker : pytest_mock
        Pytest-mock object for mocking external dependencies.
    """
    # Mock output simulating subprocess.run stdout for APK analysis
    mock_output = "Analyzing APK...\nNo threats detected."
    mocker.patch(
        'subprocess.run',
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=mock_output, stderr="")
    )

    response = client.post('/check-apk', json={"file_path": "/path/to/apk.apk", "output_dir": "/output/dir"})
    assert response.status_code == 200  # Asserts successful HTTP response
    data = response.get_json()
    assert data['success'] is True  # Confirms success key in response
    assert data['stdout'] == mock_output  # Checks stdout matches mock output
