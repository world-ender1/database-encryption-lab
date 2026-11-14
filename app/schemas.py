from pydantic import BaseModel, ConfigDict, Field

STUDENT_ID_PATTERN = r"^[A-Za-z0-9]{1,16}$"


class StudentUpdate(BaseModel):
    """PUT replaces all editable fields; the student ID cannot be changed."""
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=150)
    major: str = Field(min_length=1, max_length=100)
    national_id: str = Field(min_length=1, max_length=32)
    phone: str = Field(min_length=1, max_length=32)
    address: str = Field(min_length=1, max_length=255)


class StudentPayload(StudentUpdate):
    student_id: str = Field(pattern=STUDENT_ID_PATTERN)


class StudentOut(StudentPayload):
    """Authorized API response containing decrypted values."""
