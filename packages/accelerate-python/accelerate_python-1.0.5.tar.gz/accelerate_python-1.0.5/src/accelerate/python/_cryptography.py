"""This module provides wrapper classes for certificate operations"""

## external imports
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Self

from cryptography import x509 as _X509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.types import PRIVATE_KEY_TYPES
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.extensions import ExtensionNotFound
from cryptography.x509.oid import ExtensionOID, NameOID

## internal imports
from ._dataclasses import DataClass
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker
from ._utils import Base64

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)


## constants
CERT_TYPE_PKCS12 = 1
CERT_TYPE_DER = 2
CERT_TYPE_PEM = 3


## class definitions
@dataclass(frozen=True)
@_LOGGER.audit_class()
class X509Name(DataClass):
    commonName: str
    countryName: str
    localityName: str
    stateOrProvinceName: str
    streetAddress: str
    organizationName: str
    organizationalUnitName: str
    serialNumber: str
    emailAddress: str
    postalAddress: str
    postalCode: str
    rfc4514: str

    @classmethod
    def load(cls, subject: _X509.Name) -> Self:
        args = {
            "commonName": "",
            "countryName": "",
            "localityName": "",
            "stateOrProvinceName": "",
            "streetAddress": "",
            "organizationName": "",
            "organizationalUnitName": "",
            "serialNumber": "",
            "emailAddress": "",
            "postalAddress": "",
            "postalCode": "",
            "rfc4514": subject.rfc4514_string(),
        }
        args.update(
            {name.oid._name: name.value for name in subject if name.oid._name in args}
        )
        return cls(**args)

    def get_name(self) -> _X509.Name:
        return _X509.Name(
            [
                _X509.NameAttribute(NameOID.COMMON_NAME, str(self.commonName)),
                _X509.NameAttribute(NameOID.COUNTRY_NAME, str(self.countryName)),
                _X509.NameAttribute(NameOID.LOCALITY_NAME, str(self.localityName)),
                _X509.NameAttribute(
                    NameOID.STATE_OR_PROVINCE_NAME, str(self.stateOrProvinceName)
                ),
                _X509.NameAttribute(NameOID.STREET_ADDRESS, str(self.streetAddress)),
                _X509.NameAttribute(
                    NameOID.ORGANIZATION_NAME, str(self.organizationName)
                ),
                _X509.NameAttribute(
                    NameOID.ORGANIZATIONAL_UNIT_NAME, str(self.organizationalUnitName)
                ),
                _X509.NameAttribute(NameOID.SERIAL_NUMBER, str(self.serialNumber)),
                _X509.NameAttribute(NameOID.EMAIL_ADDRESS, str(self.emailAddress)),
                _X509.NameAttribute(NameOID.POSTAL_ADDRESS, str(self.postalAddress)),
                _X509.NameAttribute(NameOID.POSTAL_CODE, str(self.postalCode)),
            ]
        )


@dataclass(frozen=True)
@_LOGGER.audit_class()
class Certificate(DataClass):
    # x509: _X509.Certificate
    subject: X509Name
    issuer: X509Name
    expiryISO: str
    thumbprint: str
    pem: str
    der: str
    subjectAlternateNames: list[str] = field(default_factory=list)

    @classmethod
    def from_pem_file(cls, *path: str | Path) -> Self:
        return cls.from_pem(Path(*path).read_bytes())

    @classmethod
    def from_der_file(cls, *path: str | Path) -> Self:
        return cls.from_der(Path(*path).read_bytes())

    @classmethod
    def from_pem(cls, cert_data: bytes) -> Self:
        return cls.from_x509(_X509.load_pem_x509_certificate(cert_data))

    @classmethod
    def from_der(cls, cert_data: bytes) -> Self:
        return cls.from_x509(_X509.load_der_x509_certificate(cert_data))

    @classmethod
    def from_x509(cls, x509: _X509.Certificate) -> Self:
        san_list = []
        try:
            san = x509.extensions.get_extension_for_oid(
                ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            ).value
            san_list = [dns.value for dns in san]  # type: ignore[reportGeneralTypeIssues]
        except ExtensionNotFound:
            _LOGGER.debug("No subjectAltName in cert")
            pass

        args = {
            # "x509": x509,
            "subject": X509Name.load(x509.subject),
            "issuer": X509Name.load(x509.issuer),
            "subjectAlternateNames": san_list,
            "expiryISO": x509.not_valid_after.isoformat() + "+00:00",
            "thumbprint": x509.fingerprint(hashes.SHA1()).hex().upper(),
            "pem": x509.public_bytes(serialization.Encoding.PEM).decode(),
            "der": Base64.encode(x509.public_bytes(serialization.Encoding.DER)),
            # "public_key": x509.public_key(), #OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, aX509).decode("utf-8"),
        }
        return cls(**args)


@dataclass(frozen=True)
@_LOGGER.audit_class()
class PrivateKey(DataClass):
    # rsa_key: rsa.RSAPrivateKey
    pem: str

    @classmethod
    def from_rsa(cls, private_key: PRIVATE_KEY_TYPES) -> Self:
        pem = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode()
        return cls(pem=pem)


@dataclass(frozen=True)
@_LOGGER.audit_class()
class PKCS12(DataClass):
    certificate: Certificate
    privateKey: PrivateKey
    additionalCertificates: list[X509Name]

    @classmethod
    def from_file(cls, *path: str | Path, password: str = "") -> Self:
        return cls.load(Path(*path).read_bytes(), password)

    @classmethod
    def load(cls, cert_data: bytes, password: str = "") -> Self:
        rsa_key, x509, additional_certificates = pkcs12.load_key_and_certificates(
            cert_data, password.encode("utf-8")
        )
        assert rsa_key and x509, "Invalid PKCS12 data"

        return cls(
            Certificate.from_x509(x509),
            PrivateKey.from_rsa(rsa_key),
            [X509Name.load(_cert.subject) for _cert in additional_certificates],
        )

    def create_certificate(
        self,
        name: str,
        public_key_pem: str,
        private_key_pem: str,
        password: str | None = None,
        key_password: str | None = None,
    ):
        return pkcs12.serialize_key_and_certificates(
            name=name.encode(),
            key=serialization.load_pem_private_key(
                private_key_pem.encode(),
                key_password.encode() if key_password else None,
            ),  # type: ignore[reportArgumentType]
            cert=_X509.load_pem_x509_certificate(public_key_pem.encode()),
            cas=None,
            encryption_algorithm=serialization.BestAvailableEncryption(
                password.encode()
            )
            if password
            else serialization.NoEncryption(),
        )

    @classmethod
    def create_self_signed_certificate(
        cls, certificate: Certificate, aSubjectAlternateNames=[], aIssuer={}
    ):
        """
        This method generates self signed certificate
        """
        # Generate private key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        san_list = [_X509.DNSName(dns) for dns in certificate.subjectAlternateNames]
        san_list.insert(0, _X509.DNSName(certificate.subject.commonName))

        # path_len=0 means this cert can only sign itself, not other certs.
        basic_contraints = _X509.BasicConstraints(ca=True, path_length=0)
        now = datetime.now()
        _certificate = (
            _X509.CertificateBuilder()
            .subject_name(certificate.subject.get_name())
            .issuer_name(certificate.issuer.get_name())
            .public_key(private_key.public_key())
            .serial_number(1000)
            .not_valid_before(now)
            .not_valid_after(now + timedelta(days=730))
            .add_extension(basic_contraints, False)
            .add_extension(_X509.SubjectAlternativeName(san_list), False)
            .sign(private_key, hashes.SHA256())
        )

        p12_cert = cls(
            Certificate.from_x509(_certificate), PrivateKey.from_rsa(private_key), []
        )
        _LOGGER.notice("PKCS12: {}", p12_cert.as_dict())

        return p12_cert


## export symbols
__all__ = ["X509Name", "Certificate", "PrivateKey", "PKCS12"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
