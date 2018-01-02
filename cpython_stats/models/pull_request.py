import dateutil.parser
from cpython_stats.models_base import Base
from sqlalchemy import Column, String, Integer, DateTime, Boolean


class PullRequest(Base):
    __tablename__ = 'pull_requests'
    number = Column(Integer, primary_key=True)
    base = Column(String)
    author = Column(String)
    comments = Column(Integer)
    created_at = Column(DateTime)
    closed_at = Column(DateTime, nullable=True)
    commits = Column(Integer)
    merged = Column(Boolean)
    merged_by = Column(String)


def create_pull_request_from_gh_object(pr_object):
    pr = pr_object._json_data
    return PullRequest(
        number=pr["number"],
        base=pr["base"]["label"],
        author=pr["user"]["login"],
        comments=pr["comments"],
        created_at=dateutil.parser.parse(pr["created_at"]),
        closed_at=dateutil.parser.parse(pr["closed_at"]) if pr["closed_at"] is not None else None,
        commits=pr["commits"],
        merged=pr["merged"],
        merged_by=pr["merged_by"]["login"] if pr["merged_by"] is not None else None
    )
