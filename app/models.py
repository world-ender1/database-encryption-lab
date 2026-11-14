"""Frozen H3 schema: scripts from TV3 depend on these column names."""
from sqlalchemy import LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    student_id: Mapped[str] = mapped_column(String(16), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    major: Mapped[str] = mapped_column(String(100))
    national_id_ct: Mapped[bytes] = mapped_column(LargeBinary)
    national_id_nonce: Mapped[bytes] = mapped_column(LargeBinary)
    phone_ct: Mapped[bytes] = mapped_column(LargeBinary)
    phone_nonce: Mapped[bytes] = mapped_column(LargeBinary)
    address_ct: Mapped[bytes] = mapped_column(LargeBinary)
    address_nonce: Mapped[bytes] = mapped_column(LargeBinary)
    key_version: Mapped[str] = mapped_column(String(20))
