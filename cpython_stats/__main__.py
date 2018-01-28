import datetime
import itertools
import os
import logging

import numpy as np
import pandas as pd
from cpython_stats.models.core_developers import CoreDeveloper
from cpython_stats.models.pull_request import PullRequest
from cpython_stats.models import init_db
from cpython_stats.utils import session_scope, cache_response
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)

ENGINE, BASE, SESSION = init_db()


@app.route("/")
def hello():
    coredev, non_coredev = get_merge_stats()
    return render_template('prs.html',
                           coredev=coredev,
                           non_coredev=non_coredev)


@app.route("/get_prs")
def get_prs():
    events = get_open_pr_history()
    return jsonify([{"date": event[0], "n": event[1]} for event in events.itertuples()])


@app.route("/get_merge_times")
def get_merge_times():
    events = get_merge_over_time()
    logging.warning("merge ready")
    return jsonify([{"date": event[0], "n": event[1]} for event in events.itertuples()])


@cache_response(datetime.timedelta(days=1))
def get_merge_stats():
    pull_requests = get_pull_requests()
    core_devs = get_core_developers()

    core_prs = pd.merge(pull_requests, core_devs, how="inner", left_on="author", right_on="username")
    non_core_prs = pull_requests[~pull_requests.isin(core_prs)]

    core_devs_merge_time = (core_prs["closed_at"] - core_prs["created_at"]) / np.timedelta64(1, 'D')
    non_core_devs_merge_time = (non_core_prs["closed_at"] - non_core_prs["created_at"]) / np.timedelta64(1, 'D')
    return core_devs_merge_time, non_core_devs_merge_time


@cache_response(datetime.timedelta(days=1))
def get_core_developers():
    with session_scope(SESSION()) as session:
        core_devs = pd.read_sql(session.query(CoreDeveloper).statement, session.bind)
    return core_devs


@cache_response(datetime.timedelta(days=1))
def get_open_pr_history():
    pr_dt = get_pull_requests()
    pr_dt = pr_dt.set_index("created_at")
    closed_events = list(zip(pr_dt[pr_dt["closed_at"].notnull()]["closed_at"].values, itertools.repeat(-1)))
    created_events = list(zip(pr_dt.index.values, itertools.repeat(+1)))
    events = np.concatenate([created_events, closed_events])
    events = np.array(sorted(events, key=lambda x: x[0]))
    events = pd.DataFrame(events).set_index(0)
    events = events.cumsum()
    return events[::10]


@cache_response(datetime.timedelta(days=1))
def get_merge_over_time():
    pr_dt = get_pull_requests()
    pr_dt["merge_time"] = (pr_dt["closed_at"] - pr_dt["created_at"]) / np.timedelta64(1, 'D')
    pr_dt = pr_dt.set_index("created_at").sort_index()
    merges = pr_dt[~pr_dt["merge_time"].isnull()]["merge_time"]
    return pd.DataFrame(index=merges.index, data=(merges.cumsum() / (np.arange(len(merges)) + 1)).values).iloc[100::10]


@cache_response(datetime.timedelta(days=1))
def get_pull_requests():
    with session_scope(SESSION()) as session:
        latest_prs = pd.read_sql(session.query(PullRequest).statement, session.bind)
    return latest_prs


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
