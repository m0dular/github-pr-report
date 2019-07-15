#!/usr/bin/env python3

from github import Github
from os.path import expanduser
from datetime import datetime
import sys
import csv
import argparse


def get_token(token):
    return Github(token, per_page=100)


def get_prs(github, params):
    prs = []

    with open('pr_report.csv', 'w') as f:
        writer = csv.DictWriter(
            f, ['Repository', 'Author', 'Date_Created', 'Title'])

        for pr in github.search_issues(**params):
            try:
                author = users[pr.user.login]
            except KeyError:
                author = pr.user.login
            prs.append(dict(
                # Hack to get the repo name from the url. Using pr.repository
                # results in another api call per pr, which is terribly slow
                Repository=pr.url.split('/')[-3],
                Author=author if author else pr.user.login,
                Date_Created=pr.created_at, Title=pr.title))

        writer.writeheader()
        s = sorted(prs, key=lambda x: x['Repository'])
        writer.writerows(s)


def main():
    global users
    p = argparse.ArgumentParser()
    p.add_argument(
        "-u", "--user", type=str,
        help="Comma separated string of users to query for")
    p.add_argument(
        "-o", "--org", type=str,
        help="Organization id. Required")
    p.add_argument(
        "-t", "--team", type=int,
        help="Numeric identifier of the team to query for")
    p.add_argument(
        "-k", "--token", type=str,
        help="Token to use in api calls. Can be saved in ~/.pr_token")
    p.add_argument(
        "-s", "--state", type=str,
        help="State of PRs.  One of 'open' or 'closed'. Defaults to 'open'")
    p.add_argument(
        "-b", "--before", type=str,
        help="Get PRs created before DATE.  Must by YYYY-MM-DD")
    p.add_argument(
        "-a", "--after", type=str,
        help="Get PRs created after DATE.  Must by YYYY-MM-DD")
    args = p.parse_args()

    if not args.org:
        print("Error: org is required")
        p.print_usage()
        exit(1)

    if args.team and args.user:
        print("Error: mutually exclusive values team and user specified.")
        p.print_usage()
        exit(1)

    token = args.token if args.token else open(
            "%s/.pr_token" % expanduser("~")).read().strip('\n')
    state = args.state if args.state else 'open'

    github = get_token(token)

    if args.team:
        teams = github.get_organization(args.org).get_teams()
        team = [t for t in teams if int(t.id) == int(args.team)]

        if not team:
            print(
                "Error: could not find team %s in org %s" %
                (args.team, args.org))
            exit(1)

        users = {m.login: m.name for m in team[0].get_members()}
    elif args.user:
        users = args.user.split(',')
        query = ' '.join(['user:%s' % u for u in users])
        params = {'query': query}
        users = {u.login: u.name for u in github.search_users(**params)}
    else:
        # Getting all members of an org can result in 414 Request-URI Too Large
        # For now, just use the login name for org-wide search
        query = ''
        users = {}

    # Turn a single user into a list so we don't iterate over each character
    if users and isinstance(users, str):
        users = [users]
    if users:
        query = ' '.join(['author:%s' % u for u in users.keys()])
        query = 'is:pr ' + query

    params = {'org': args.org, 'state': state, 'query': query}

    if args.before:
        try:
            datetime.strptime(args.before, '%Y-%m-%d')
        except Exception:
            print("--before and --after arguments must be YYYY-MM-DD")
            exit(1)

    if args.after:
        try:
            datetime.strptime(args.after, '%Y-%m-%d')
        except Exception:
            print("--before and --after arguments must be YYYY-MM-DD")
            exit(1)

    created = "%s..%s" % (
        args.after if args.after else '*',
        args.before if args.before else '*')
    params.update({'created': created})

    get_prs(github, params)


if __name__ == '__main__':
    main()
