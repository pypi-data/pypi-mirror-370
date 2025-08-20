from datetime import datetime

from pydantic import BaseModel

from .custom_types import Status

class CreateSubmission(BaseModel):
    source_code: str
    language_id: int
    stdin: str | None = None
    expected_output: str | None = None
    cpu_time_limit: float | None = None
    memory_limit: int | None = None # In kilobytes
    date: datetime = datetime.now()

class Submission(CreateSubmission):
    token: str

class SubmissionResult(BaseModel):
    source_code: str
    language_id: int
    result: Status
    stdout: str
    time: float | None = None
    memory: int | None = None # In kilobytes
    date: datetime = datetime.now()
