import datetime
import os
import time

import github3
from cpython_stats.logging_utils import set_up_logging
from cpython_stats.models.core_developers import CoreDeveloper
from cpython_stats.models.pull_request import create_pull_request_from_gh_object, PullRequest
from cpython_stats.models_base import init_db
from cpython_stats.utils import retry_and_catch, session_scope

logger = set_up_logging(__name__)


def main():
    gh = github3.login(os.getenv("BOT_MAIL"), os.getenv("BOT_PASSWORD"))
    engine, Base, Session = init_db()

    repo = gh.repository("Python", "cpython")
    with session_scope(Session()) as session:
        while True:
            update_core_devs(gh, session)
            get_latest_pr_from_github(repo, session)
            update_open_prs(repo, session)

            next_date = datetime.datetime.now() + datetime.timedelta(days=1)
            logger.info(f"Schedulling next check: {next_date}")
            time.sleep((next_date - datetime.datetime.now()).seconds)


@retry_and_catch(exceptions=(github3.models.GitHubError,),
                 backoff=8, tries=5, delay=10)
def update_core_devs(gh, session):
    logger.info(f"Retrieving core devs from database")
    core_devs = set(user.username for user in session.query(CoreDeveloper).all())
    logger.info(f"Retrieving latest core devs from github")
    org = gh.organization("Python")
    new_devs = set(coredev.login for coredev in org.iter_members()) - core_devs
    for dev in new_devs:
        new_dev = CoreDeveloper(username=dev)
        session.add(new_dev)


@retry_and_catch(exceptions=(github3.models.GitHubError,),
                 backoff=8, tries=5, delay=10)
def update_open_prs(repo, session):
    logger.info(f"Retrieving open prs from database")
    opened_prs = session.query(PullRequest).filter(PullRequest.closed_at == None).all()
    logger.info(f"{len(opened_prs)} to check against github status")
    for pr in opened_prs:
        logger.info(f"Retrieving latest state for pr {pr.number}")
        pr_object = create_pull_request_from_gh_object(repo.pull_request(pr.number))
        if pr_object.merged:
            logger.info(f"Pr {pr.number} has been merged. Updating.")
            pr.merged = pr_object.merged
            pr.merged_by = pr_object.merged_by
            pr.closed_at = pr_object.closed_at
            pr.commits = pr_object.commits
            pr.comments = pr_object.comments
            session.commit()


@retry_and_catch(exceptions=(github3.models.GitHubError,),
                 backoff=8, tries=5, delay=10)
def get_latest_pr_from_github(repo, session):
    latest_pr = session.query(PullRequest).order_by(PullRequest.number.desc()).first()
    latest_pr_number = latest_pr.number if latest_pr else 1

    latest_available_pr_number = next(repo.iter_pulls()).number

    for id_ in list(range(latest_pr_number + 1, latest_available_pr_number)):
        logger.info(f"Retrieving pull request {id_}")
        pr_object = repo.pull_request(id_)

        logger.info(f"Storing pull request {id_}")
        new_pr = create_pull_request_from_gh_object(pr_object)
        session.add(new_pr)


if __name__ == "__main__":
    # Wait one minute for not blocking deployment
    time.sleep(10)
    main()
