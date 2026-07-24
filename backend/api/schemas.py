import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")
EMPLOYEE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,50}$")


class LoginRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        if not USERNAME_PATTERN.fullmatch(value):
            raise ValueError("Username contains unsupported characters")
        return value


class EmployeeRequest(BaseModel):
    employee: Annotated[str, Field(min_length=3, max_length=50)]

    @field_validator("employee")
    @classmethod
    def validate_employee(cls, value: str) -> str:
        value = value.strip().upper()
        if not EMPLOYEE_PATTERN.fullmatch(value):
            raise ValueError("Employee identifier contains unsupported characters")
        return value


class AssignRequest(EmployeeRequest):
    note: Annotated[str, Field(min_length=1, max_length=1000)]

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Note cannot be empty")
        return value
