from sqlalchemy import TIMESTAMP, Column, String

from database import Base


class IpAddress(Base):
    __tablename__ = "ip_addresses"

    id = Column(String, primary_key=True, nullable=False, index=True)
    ip_address = Column(String, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False)
