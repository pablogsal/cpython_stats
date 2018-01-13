#!/bin/bash

set -e

git config --global user.email "travis@travis-ci.org" 
git config --global user.name "Travis CI"
git config --global push.default matching

git remote add dokku dokku@pablogsal.science:cpython_stats

git push --set-upstream dokku master --force

