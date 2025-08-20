## external imports
# from cryptography import x509 as _X509
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.x509.oid import NameOID
from pathlib import Path

import pytest

## internal imports

## global variables
DATA_PATH = Path(__file__).parent.joinpath("data")


## test cases
# class TestX509Name:
#     def test_load(self):
#         subject = _X509.Name(
#             [
#                 _X509.NameAttribute(NameOID.COMMON_NAME, "example.com"),
#                 _X509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
#                 _X509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
#                 _X509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
#                 _X509.NameAttribute(NameOID.STREET_ADDRESS, "123 Example St"),
#                 _X509.NameAttribute(NameOID.ORGANIZATION_NAME, "Example Inc"),
#                 _X509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "IT"),
#                 _X509.NameAttribute(NameOID.SERIAL_NUMBER, "123456789"),
#                 _X509.NameAttribute(NameOID.EMAIL_ADDRESS, "admin@example.com"),
#                 _X509.NameAttribute(NameOID.POSTAL_ADDRESS, "123 Example St"),
#                 _X509.NameAttribute(NameOID.POSTAL_CODE, "94105"),
#             ]
#         )
#         x509_name = X509Name.load(subject)
#         assert x509_name.commonName == "example.com"
#         assert x509_name.countryName == "US"
#         assert x509_name.localityName == "San Francisco"
#         assert x509_name.stateOrProvinceName == "California"
#         assert x509_name.streetAddress == "123 Example St"
#         assert x509_name.organizationName == "Example Inc"
#         assert x509_name.organizationalUnitName == "IT"
#         assert x509_name.serialNumber == "123456789"
#         assert x509_name.emailAddress == "admin@example.com"
#         assert x509_name.postalAddress == "123 Example St"
#         assert x509_name.postalCode == "94105"
#         assert (
#             x509_name.rfc4514
#             == "CN=example.com,C=US,L=San Francisco,ST=California,STREET=123 Example St,O=Example Inc,OU=IT,SERIALNUMBER=123456789,EMAILADDRESS=admin@example.com,POSTALADDRESS=123 Example St,POSTALCODE=94105"
#         )

#     def test_get_name(self):
#         x509_name = X509Name(
#             commonName="example.com",
#             countryName="US",
#             localityName="San Francisco",
#             stateOrProvinceName="California",
#             streetAddress="123 Example St",
#             organizationName="Example Inc",
#             organizationalUnitName="IT",
#             serialNumber="123456789",
#             emailAddress="admin@example.com",
#             postalAddress="123 Example St",
#             postalCode="94105",
#             rfc4514="CN=example.com,C=US,L=San Francisco,ST=California,STREET=123 Example St,O=Example Inc,OU=IT,SERIALNUMBER=123456789,EMAILADDRESS=admin@example.com,POSTALADDRESS=123 Example St,POSTALCODE=94105",
#         )
#         name = x509_name.get_name()
#         assert (
#             name.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "example.com"
#         )
#         assert name.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value == "US"
#         assert (
#             name.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value
#             == "San Francisco"
#         )
#         assert (
#             name.get_attributes_for_oid(NameOID.STATE_OR_PROVINCE_NAME)[0].value
#             == "California"
#         )
#         assert (
#             name.get_attributes_for_oid(NameOID.STREET_ADDRESS)[0].value
#             == "123 Example St"
#         )
#         assert (
#             name.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
#             == "Example Inc"
#         )
#         assert (
#             name.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
#             == "IT"
#         )
#         assert (
#             name.get_attributes_for_oid(NameOID.SERIAL_NUMBER)[0].value == "123456789"
#         )
#         assert (
#             name.get_attributes_for_oid(NameOID.EMAIL_ADDRESS)[0].value
#             == "admin@example.com"
#         )
#         assert (
#             name.get_attributes_for_oid(NameOID.POSTAL_ADDRESS)[0].value
#             == "123 Example St"
#         )
#         assert name.get_attributes_for_oid(NameOID.POSTAL_CODE)[0].value == "94105"


# class TestCertUtils:
#     def test_certificate_from_pem_file(self):
#         cert_path = "/path/to/certificate.pem"
#         certificate = _cryptography.Certificate.from_pem_file(cert_path)
#         assert isinstance(certificate, _cryptography.Certificate)
#         assert certificate.pem == "..."
#         assert certificate.der == b"..."

#     def test_certificate_from_der_file(self):
#         cert_path = "/path/to/certificate.der"
#         certificate = _cryptography.Certificate.from_der_file(cert_path)
#         assert isinstance(certificate, _cryptography.Certificate)
#         assert certificate.pem == "..."
#         assert certificate.der == b"..."

#     def test_certificate_from_pem(self):
#         cert_data = b"..."
#         certificate = _cryptography.Certificate.from_pem(cert_data)
#         assert isinstance(certificate, _cryptography.Certificate)
#         assert certificate.pem == "..."
#         assert certificate.der == b"..."

#     def test_certificate_from_der(self):
#         cert_data = b"..."
#         certificate = _cryptography.Certificate.from_der(cert_data)
#         assert isinstance(certificate, _cryptography.Certificate)
#         assert certificate.pem == "..."
#         assert certificate.der == b"..."

#     def test_certificate_from_x509(self):
#         x509_cert = ...
#         certificate = _cryptography.Certificate.from_x509(x509_cert)
#         assert isinstance(certificate, _cryptography.Certificate)
#         assert certificate.pem == "..."
#         assert certificate.der == b"..."

#     def test_pkcs12_from_file(self):
#         cert_path = "/path/to/certificate.p12"
#         password = "password"
#         pkcs12 = _cryptography.PKCS12.from_file(cert_path, password)
#         assert isinstance(pkcs12, _cryptography.PKCS12)
#         assert isinstance(pkcs12.certificate, _cryptography.Certificate)
#         assert isinstance(pkcs12.privateKey, _cryptography.PrivateKey)
#         assert isinstance(pkcs12.additionalCertificates, list)

#     def test_create_self_signed_certificate(self):
#         certificate = _cryptography.Certificate(...)
#         p12_cert = _cryptography.create_self_signed_certificate(certificate)
#         assert isinstance(p12_cert, _cryptography.PKCS12)
#         assert isinstance(p12_cert.certificate, _cryptography.Certificate)
#         assert isinstance(p12_cert.privateKey, _cryptography.PrivateKey)
#         assert isinstance(p12_cert.additionalCertificates, list)

#     def test_create_p12_certificate(self):
#         name = "certificate"
#         public_key_pem = "..."
#         private_key_pem = "..."
#         password = "password"
#         key_password = "key_password"
#         p12_data = _cryptography.create_p12_certificate(
#             name, public_key_pem, private_key_pem, password, key_password
#         )
#         assert isinstance(p12_data, bytes)
#         # Additional assertions for the generated PKCS12 data


# class TestPKCS12:
#     def test_certificate_from_pem_file(tmp_path):
#         cert_path = tmp_path / "certificate.pem"
#         cert_data = b"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
#         cert_path.write_bytes(cert_data)
#         certificate = Certificate.from_pem_file(str(cert_path))
#         assert isinstance(certificate, Certificate)
#         assert certificate.pem == cert_data.decode()

#     def test_certificate_from_der_file(tmp_path):
#         cert_path = tmp_path / "certificate.der"
#         cert_data = b"..."
#         cert_path.write_bytes(cert_data)
#         certificate = Certificate.from_der_file(str(cert_path))
#         assert isinstance(certificate, Certificate)
#         assert certificate.der == cert_data

#     def test_certificate_from_pem():
#         cert_data = b"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
#         certificate = Certificate.from_pem(cert_data)
#         assert isinstance(certificate, Certificate)
#         assert certificate.pem == cert_data.decode()

#     def test_certificate_from_der():
#         cert_data = b"..."
#         certificate = Certificate.from_der(cert_data)
#         assert isinstance(certificate, Certificate)
#         assert certificate.der == cert_data

#     def test_certificate_from_x509():
#         subject = _X509.Name([
#             _X509.NameAttribute(NameOID.COMMON_NAME, "example.com"),
#         ])
#         issuer = subject
#         private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
#         certificate = (
#             _X509.CertificateBuilder()
#             .subject_name(subject)
#             .issuer_name(issuer)
#             .public_key(private_key.public_key())
#             .serial_number(1000)
#             .not_valid_before(_X509.datetime.datetime.utcnow())
#             .not_valid_after(_X509.datetime.datetime.utcnow() + _X509.datetime.timedelta(days=10))
#             .sign(private_key, hashes.SHA256())
#         )
#         cert = Certificate.from_x509(certificate)
#         assert isinstance(cert, Certificate)
#         assert cert.subject.commonName == "example.com"

#     def test_pkcs12_from_file(tmp_path):
#         cert_path = tmp_path / "certificate.p12"
#         cert_data = b"..."
#         cert_path.write_bytes(cert_data)
#         pkcs12 = PKCS12.from_file(str(cert_path), "password")
#         assert isinstance(pkcs12, PKCS12)
#         assert isinstance(pkcs12.certificate, Certificate)
#         assert isinstance(pkcs12.privateKey, PrivateKey)
#         assert isinstance(pkcs12.additionalCertificates, list)

#     def test_create_self_signed_certificate():
#         subject = X509Name(
#             commonName="example.com",
#             countryName="US",
#             localityName="San Francisco",
#             stateOrProvinceName="California",
#             streetAddress="123 Example St",
#             organizationName="Example Inc",
#             organizationalUnitName="IT",
#             serialNumber="123456789",
#             emailAddress="admin@example.com",
#             postalAddress="123 Example St",
#             postalCode="94105",
#             rfc4514="CN=example.com,C=US,L=San Francisco,ST=California,STREET=123 Example St,O=Example Inc,OU=IT,SERIALNUMBER=123456789,EMAILADDRESS=admin@example.com,POSTALADDRESS=123 Example St,POSTALCODE=94105"
#         )
#         certificate = Certificate(
#             subject=subject,
#             issuer=subject,
#             subjectAlternateNames=["example.com"],
#             expiryISO="2023-10-10T00:00:00+00:00",
#             thumbprint="...",
#             pem="...",
#             der=b"..."
#         )
#         p12_cert = PKCS12.create_self_signed_certificate(certificate)
#         assert isinstance(p12_cert, PKCS12)
#         assert isinstance(p12_cert.certificate, Certificate)
#         assert isinstance(p12_cert.privateKey, PrivateKey)
#         assert isinstance(p12_cert.additionalCertificates, list)

#     def test_create_p12_certificate():
#         name = "certificate"
#         public_key_pem = "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
#         private_key_pem = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
#         password = "password"
#         key_password = "key_password"
#         p12_data = PKCS12.create_certificate(name, public_key_pem, private_key_pem, password, key_password)
#         assert isinstance(p12_data, bytes)

if __name__ == "__main__":
    pytest.main([__file__])
