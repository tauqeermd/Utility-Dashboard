from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base = declarative_base()
engine = create_engine("sqlite:///./machines.db")
SessionLocal = sessionmaker(bind=engine)

class MachineStatus(Base):
    __tablename__ = "machines"
    machine_id = Column(String, primary_key=True, index=True)
    os = Column(String)
    os_version = Column(String)
    disk_encryption = Column(Boolean)
    os_update = Column(Boolean)
    antivirus = Column(Boolean)
    sleep_setting_ok = Column(Boolean)
    last_report = Column(DateTime)

Base.metadata.create_all(bind=engine)

class Report(BaseModel):
    machine_id: str
    os: str
    os_version: str
    disk_encryption: bool
    os_update: bool
    antivirus: bool
    sleep_setting_ok: bool
    timestamp: int

@app.post("/api/report")
async def report_status(report: Report):
    db = SessionLocal()
    obj = db.query(MachineStatus).filter_by(machine_id=report.machine_id).first()
    now = datetime.datetime.fromtimestamp(report.timestamp)
    if obj:
        obj.os = report.os
        obj.os_version = report.os_version
        obj.disk_encryption = report.disk_encryption
        obj.os_update = report.os_update
        obj.antivirus = report.antivirus
        obj.sleep_setting_ok = report.sleep_setting_ok
        obj.last_report = now
    else:
        obj = MachineStatus(
            machine_id=report.machine_id,
            os=report.os,
            os_version=report.os_version,
            disk_encryption=report.disk_encryption,
            os_update=report.os_update,
            antivirus=report.antivirus,
            sleep_setting_ok=report.sleep_setting_ok,
            last_report=now
        )
        db.add(obj)
    db.commit()
    db.close()
    return {"status": "ok"}

@app.get("/api/machines")
async def list_machines(os: str = None, issue: str = None):
    db = SessionLocal()
    query = db.query(MachineStatus)
    if os:
        query = query.filter(MachineStatus.os == os)
    results = []
    for m in query.all():
        issues = []
        if not m.disk_encryption:
            issues.append("disk_encryption")
        if not m.os_update:
            issues.append("os_update")
        if not m.antivirus:
            issues.append("antivirus")
        if not m.sleep_setting_ok:
            issues.append("sleep_setting")
        if issue and issue not in issues:
            continue
        results.append({
            "machine_id": m.machine_id,
            "os": m.os,
            "os_version": m.os_version,
            "disk_encryption": m.disk_encryption,
            "os_update": m.os_update,
            "antivirus": m.antivirus,
            "sleep_setting_ok": m.sleep_setting_ok,
            "last_report": m.last_report.isoformat(),
            "issues": issues
        })
    db.close()
    return results