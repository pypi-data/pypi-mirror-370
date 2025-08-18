import datetime
import re
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Security
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import session

import models
from database import db_dependency
from util.auth import get_token_header

router = APIRouter(prefix="/ip", dependencies=[Security(get_token_header)])

ipv4_pattern = re.compile(
    r"^([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26"
    r"|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
    r"(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]"
    r"|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
)


@router.post("/")
async def add_ip(
    identifier: str, db: db_dependency, request: Request, ip: Optional[str] = None
):
    if identifier.strip() == "":
        raise HTTPException(
            status_code=422, detail="Missing identifier query parameter"
        )
    if ip is None:
        if "cf-connecting-ip" in request.headers:
            ip = request.headers.get("cf-connecting-ip")
        else:
            ip = request.client.host
    if not ipv4_pattern.match(ip):
        raise HTTPException(status_code=422, detail="Invalid IP address format")

    return insert_or_update_ip(identifier, ip, db)


@router.get("/")
async def get_all_ips(db: db_dependency):
    return db.query(models.IpAddress).all()


@router.get("/{identifier}")
async def get_ip(identifier: str, db: db_dependency):
    try:
        return db.get_one(models.IpAddress, identifier)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Identifier not found")


def insert_or_update_ip(identifier: str, ip: str, db: session):
    updated_at = datetime.datetime.now()

    try:
        db_ip = db.get_one(models.IpAddress, identifier)
        db_ip.ip_address = ip
        db_ip.id = identifier
        db_ip.updated_at = updated_at
        db.merge(db_ip)
    except NoResultFound:
        db_ip = models.IpAddress(id=identifier, ip_address=ip, updated_at=updated_at)
        db.add(db_ip)

    db.commit()
    db.refresh(db_ip)

    return db_ip
