import datetime
import socket
from typing import Optional
from xml.etree.ElementTree import ParseError as XMLParseError

from licensing.methods import Helpers, Key
from licensing.models import LicenseKey


class License:
    def __init__(
        self,
        license: LicenseKey,
        license_message: Optional[str] = None,
    ):
        """
        Constructor for License class.
        Args:
            rsa_public_key (str): RSA public key
            activation_token (str): Activation token
            product_id (str): Product ID
            key (str): License key
            key_file_path (str): Path to license file
        """
        self._license = license
        self._license_message = license_message

    @classmethod
    def from_key(
        cls, rsa_public_key: str, activation_token: str, product_id: str, key: str
    ):
        """
        Create a License object from a key
        Args:
            rsa_public_key (str): RSA public key
            activation_token (str): Activation token
            product_id (str): Product ID
            key (str): License key
        Returns:
            License: License object
        """
        try:
            license = Key.activate(
                token=activation_token,
                rsa_pub_key=rsa_public_key,
                product_id=product_id,
                key=key,
                machine_code=Helpers.GetMachineCode(v=2),
                friendly_name=socket.gethostname(),
            )
        # Licensing library throws XMLParseError if the RSA public key is not valid xml
        except XMLParseError:
            license = None
            license_message = "RSA public key is not valid"
            return cls(
                license=license,
                license_message=license_message,
            )
        return cls(
            license=license[0],
            license_message=license[1],
        )

    @classmethod
    def from_file(cls, rsa_public_key: str, key_file_path: str):
        """
        Create a License object from a file
        Args:
            rsa_public_key (str): RSA public key
            key_file_path (str): Path to license file
        Returns:
            License: License object
        """
        key_file = ""
        try:
            with open(str(key_file_path), "r") as license_file:
                key_file = license_file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"License file not found at {key_file_path}")

        license = LicenseKey.load_from_string(
            rsa_pub_key=rsa_public_key,
            string=key_file,
        )
        license_message = "License file is valid"
        if license is None:
            license_message = "License file is not valid"

        return cls(
            license=license,
            license_message=license_message,
        )

    def save_license(self, file_path):
        """
        Save the license to a file
        """
        with open(file_path, "w") as license_file:
            license_file.write(self._license.save_as_string())

    def is_license_valid(self):
        """
        Check if the license is valid
        """
        if self._license is None:
            return False, self._license_message
        if not Helpers.IsOnRightMachine(self._license, v=2):
            return False, "License is not valid for this machine"
        if datetime.datetime.now() > self._license.expires:
            return False, "License expired"
        return True, "License is valid"

    def get_days_until_expiration(self):
        """
        Get the number of days until the license expires
        """

        if self._license is None:
            return 0
        _days_until_expiration = (self._license.expires - datetime.datetime.now()).days
        if _days_until_expiration < 0:
            return 0
        return _days_until_expiration
