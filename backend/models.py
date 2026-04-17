from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ChildBase(BaseModel):
    nik: str
    name: str
    date_of_birth: date
    gender: str  # "L" or "P"


class ChildCreate(ChildBase):
    parent_name: str
    parent_phone: str
    parent_telegram_id: Optional[str] = None
    address: str
    rt_rw: str


class Child(ChildBase):
    id: int
    parent_name: str
    parent_phone: str
    parent_telegram_id: Optional[str]
    address: str
    rt_rw: str
    risk_status: str = "green"  # green, yellow, red
    last_posyandu_date: Optional[date]
    created_at: datetime


class HealthRecordBase(BaseModel):
    child_id: int
    weight_kg: float
    height_cm: float
    bb_tb_status: str
    vitamin_a: bool = False
    immunization_status: str = "complete"
    notes: Optional[str] = ""


class HealthRecordCreate(HealthRecordBase):
    recorded_by: int  # kader_id


class HealthRecord(HealthRecordBase):
    id: int
    date: date
    recorded_by: int


class PosyanduBase(BaseModel):
    name: str
    location: str
    schedule_day: int  # 1-31, day of month


class PosyanduCreate(PosyanduBase):
    pass


class Posyandu(PosyanduBase):
    id: int


class KaderBase(BaseModel):
    name: str
    telegram_id: str
    role: str = "kader"  # kader, bidan, kepala_desa


class KaderCreate(KaderBase):
    pass


class Kader(KaderBase):
    id: int
