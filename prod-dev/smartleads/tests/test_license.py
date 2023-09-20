# System imports
import datetime
from unittest.mock import MagicMock

# Third party imports
import pytest
from freezegun import freeze_time
from licensing.models import LicenseKey

# Local imports
from SmartLeads.license import License

"""
Tests for the Segment License interface helper
"""


@pytest.fixture
def mock_activate(mocker):
    return mocker.patch("licensing.methods.Key.activate")


@pytest.fixture
def mock_get_machine_code(mocker):
    return mocker.patch("licensing.methods.Helpers.IsOnRightMachine")


@pytest.fixture
def mock_load_license_from_string(mocker):
    return mocker.patch("licensing.models.LicenseKey.load_from_string")


@pytest.fixture
def mock_open(mocker):
    return mocker.patch("builtins.open")


@pytest.fixture
def create_license_from_key(mock_activate, mock_get_machine_code):
    mock_license = MagicMock(
        spec=LicenseKey,
    )
    mock_activate.return_value = (mock_license, "license_message")
    mock_get_machine_code.return_value = True
    license = License.from_key(
        rsa_public_key="mocked_rsa_public_key",
        activation_token="mocked_activation_token",
        product_id="mocked_product_id",
        key="mocked_key",
    )
    return license


@pytest.fixture
def create_license(mock_activate, mock_get_machine_code):
    mock_license = MagicMock(
        spec=LicenseKey,
    )
    mock_license.expires = datetime.datetime(2100, 12, 31, 00, 00, 00)
    mock_activate.return_value = (mock_license, "license_message")
    mock_get_machine_code.return_value = True

    license = License.from_key(
        rsa_public_key="mocked_rsa_public_key",
        activation_token="mocked_activation_token",
        product_id="mocked_product_id",
        key="mocked_key",
    )
    return license


@pytest.fixture
def create_license_from_file(mock_load_license_from_string, mock_open):
    license = MagicMock(
        spec=LicenseKey,
    )
    mock_load_license_from_string.return_value = license
    mock_open.return_value = mock_open(read_data="mocked_key_file")
    return License.from_file(
        rsa_public_key="mocked_rsa_public_key",
        key_file_path="mocked_key_file_path",
    )


def test_license(create_license_from_key):
    """
    Test that the license is set correctly
    """
    # Setup
    license = create_license_from_key
    # Assert
    assert isinstance(license._license, LicenseKey)


def test_license_license_message(create_license_from_key):
    """
    Test that the license message is set correctly
    """
    # Setup
    license = create_license_from_key
    # Assert
    assert license._license_message == "license_message"


def test_license_from_license_file(create_license_from_file):
    """
    Test that the license is set correctly from a license file
    """
    # Setup
    license = create_license_from_file
    # Assert
    assert isinstance(license._license, LicenseKey)


def test_license_save_license_to_file(create_license_from_key, mock_open):
    """
    Test that the license is saved to a file correctly
    """
    # Setup
    mock_open.return_value = mock_open(write_data="mocked_key_file")

    # Excute
    create_license_from_key.save_license("mocked_file_path")

    # Assert
    mock_open.assert_called()


def test_is_valid_license(create_license, mock_get_machine_code):
    """
    Test that the license is valid
    """
    # Setup
    mock_get_machine_code.return_value = True

    # Excute
    is_license_valid = create_license.is_license_valid()

    # Assert
    assert is_license_valid


def test_should_be_expired(create_license, mock_get_machine_code):
    """
    Test that the license is expired
    """
    # Setup
    mock_get_machine_code.return_value = True
    create_license._license.expires = datetime.datetime(2019, 12, 31, 00, 00, 00)

    # Excute
    is_license_valid = create_license.is_license_valid()

    # Assert
    assert is_license_valid == (False, "License expired")


def test_should_be_invalid_machine(create_license, mock_get_machine_code):
    """
    Test that the license is invalid for this machine
    """
    # Setup
    # Mock the machine code check to return False
    mock_get_machine_code.return_value = False

    # Excute
    is_license_valid = create_license.is_license_valid()

    # Assert
    assert is_license_valid == (
        False,
        "License is not valid for this machine",
    )


@freeze_time("2020-01-01")
def test_should_return_30_days(create_license, mock_get_machine_code):
    """
    Test that the license is valid for 30 days
    """
    # Setup
    mock_get_machine_code.return_value = True
    create_license._license.expires = datetime.datetime(2020, 1, 31, 00, 00, 00)

    # Excute
    days_until_expiration = create_license.get_days_until_expiration()

    # Assert
    assert days_until_expiration == 30


@freeze_time("2020-01-01")
def test_should_return_0_days_if_license_is_expired(
    create_license, mock_get_machine_code
):
    """
    Test that 0 days are returned if the license is None
    """
    # Setup
    mock_get_machine_code.return_value = True
    create_license._license.expires = datetime.datetime(2000, 1, 31, 00, 00, 00)
    # Excute
    days_until_expiration = create_license.get_days_until_expiration()
    # Assert
    assert days_until_expiration == 0


def test_should_return_false_if_rsa_key_xml_invalid():
    """
    Test that False is returned if rsa key xml is invalid
    """
    # Setup
    license = License.from_key(
        rsa_public_key="mocked_rsa_public_key",
        key="mocked_key",
        activation_token="mocked_activation_token",
        product_id="mocked_product_id",
    )

    # Excute
    is_license_valid = license.is_license_valid()

    # Assert
    assert is_license_valid == (False, "RSA public key is not valid")


def test_should_return_false_and_message_if_invalid():
    """
    Test that False and a message is returned if the license is invalid
    """
    # Setup
    license = License.from_key(
        rsa_public_key="<RSAKeyValue><Modulus>mock_modulus</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>",
        key="mocked_key",
        activation_token="mocked_activation_token",
        product_id="mocked_product_id",
    )

    # Excute
    is_license_valid = license.is_license_valid()

    # Assert
    assert is_license_valid[0] is False
    assert isinstance(is_license_valid[1], str)


def test_should_return_file_error_if_key_file_does_not_exist():
    """
    Test that a FileError is returned if the key file does not exist
    """
    # Setup
    with pytest.raises(FileNotFoundError) as exception_info:
        # Excute
        _ = License.from_file(
            rsa_public_key="mocked_rsa_public_key",
            key_file_path="mocked_key_file_path",
        )
    # Assert
    assert str(exception_info.value) == "License file not found at mocked_key_file_path"
