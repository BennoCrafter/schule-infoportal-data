from datetime import date

from pydantic import BaseModel


class Substitution(BaseModel):
    class_name: str
    period: str
    absent_teacher: str
    substitution_teacher: str
    subject_abbreviation: str
    room: str
    info: str
    date: date


class News(BaseModel):
    message: str
    date: date
