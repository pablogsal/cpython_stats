from cpython_stats.models import Base
from sqlalchemy import Column, String


class CoreDeveloper(Base):
    __tablename__ = 'core_developers'
    username = Column(String, primary_key=True)
