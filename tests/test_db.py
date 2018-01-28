import contextlib
import os

import betamax
import github3
import pytest
from cpython_stats.models.pull_request import create_pull_request_from_gh_object
from cpython_stats.models import init_db
from cpython_stats.utils import session_scope


@pytest.fixture(scope="function")
def database():
    os.environ["DATABASE_URL"] = 'sqlite://'
    engine, Base, Session = init_db()
    with contextlib.closing(engine.connect()) as con:
        yield con, Session
        with con:
            for table in reversed(Base.metadata.sorted_tables):
                con.execute(table.delete())

def test_retrieve(database):
    gh = github3.login("user", "name")
    conn, Session = database
    recorder = betamax.Betamax(gh._session)
    with recorder.use_cassette("simple_pr_request"):
        repo = gh.repository("Python", "cpython")
        pr_object = repo.pull_request(1)
        with session_scope(Session()) as session:
            new_pr = create_pull_request_from_gh_object(pr_object)
            session.add(new_pr)
        prs, = *conn.execute("SELECT * from pull_requests"),
        assert prs.number == 1
