"""Map H2 payloads to H3 storage using only TV1's H1 interface."""
from app.crypto_service import CryptoService, EncryptedValue
from app.models import Student
from app.schemas import StudentOut, StudentUpdate

SENSITIVE_FIELDS = ("national_id", "phone", "address")


def apply_sensitive(row: Student, data: StudentUpdate, crypto: CryptoService) -> None:
    # Complete encryption before modifying the row, including on PUT.
    encrypted = {field: crypto.encrypt(getattr(data, field), row.student_id, field)
                 for field in SENSITIVE_FIELDS}
    for field, value in encrypted.items():
        setattr(row, f"{field}_ct", value.ciphertext)
        setattr(row, f"{field}_nonce", value.nonce)
    row.key_version = crypto.key_version


def to_out(row: Student, crypto: CryptoService) -> StudentOut:
    values = {
        field: crypto.decrypt(
            EncryptedValue(getattr(row, f"{field}_ct"), getattr(row, f"{field}_nonce"), row.key_version),
            row.student_id, field,
        )
        for field in SENSITIVE_FIELDS
    }
    return StudentOut(student_id=row.student_id, full_name=row.full_name, major=row.major, **values)
