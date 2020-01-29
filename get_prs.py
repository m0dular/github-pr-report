#!/usr/bin/env python3

from github import Github
from os.path import expanduser
from os import environ
from datetime import datetime
import csv
import argparse
import re


def get_token(token):
    return Github(token, per_page=100)


def get_prs(github, params, get_owners):
    prs = []

    with open('pr_report.csv', 'w') as f:
        writer = csv.DictWriter(
            f, ['Repository', 'Author', 'Date_Created', 'Title', 'Code_Owners'],
            lineterminator='\n')

        for pr in github.search_issues(**params):
            try:
                author = users[pr.user.login]
            except KeyError:
                author = pr.user.login

            # Hack to get the repo name and org from the url. Using pr.repository
            # results in another api call per pr, which is terribly slow
            org = pr.url.split('/')[-4]
            repo = pr.url.split('/')[-3]

            prs.append(dict(
                Repository=repo,
                Author=author if author else pr.user.login,
                Date_Created=pr.created_at, Title=pr.title,
                Code_Owners=''
                ))

        # Search for CODEOWNERS file one for every repo to minimize api calls
        if get_owners:
            query = ' '.join(['repo:%s/%s' % (org, pr['Repository']) for pr in prs])
            query += ' filename:CODEOWNERS'

            owners_dict = {}
            for r in github.search_code(query=query):
                if r.repository.name in owners_dict:
                    continue

                owners = ''
                # Strip comments and blank lines from the file
                content = re.sub(r'(?m)^ *#.*\n?', '', r.decoded_content.decode('utf-8'))
                for line in content.split('\n'):
                    if line.strip():
                        owners += line + '\n'
                owners_dict[r.repository.name] = owners.strip('\n')

            for pr in prs:
                if pr['Repository'] in owners_dict:
                    pr.update({'Code_Owners': owners_dict[pr['Repository']]})

        writer.writeheader()
        s = sorted(prs, key=lambda x: x['Repository'])
        writer.writerows(s)


def main():
    global users, org, get_owners
    p = argparse.ArgumentParser()
    p.add_argument(
        "-u", "--user", type=str,
        help="Comma separated string of users to query for")
    p.add_argument(
        "-o", "--org", type=str,
        help="Organization id. Required")
    p.add_argument(
        "-t", "--team", type=str,
        help="Comma separated string of teams to query for")
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
    p.add_argument(
        "-c", "--codeowners", action='store_true',
        help="Include content of CODEOWNERS file in the report")
    args = p.parse_args()

    if not args.org:
        print("Error: org is required")
        p.print_help()
        exit(1)
    org = args.org

    if args.team and args.user:
        print("Error: mutually exclusive values team and user specified.")
        p.print_help()
        exit(1)

    token = args.token if args.token else open(
            "%s/.pr_token" % expanduser("~")).read().strip('\n')
    state = args.state if args.state else 'open'

    github = get_token(token)

    if args.team:
        users = {}
        all_teams = github.get_organization(args.org).get_teams()

        for team in args.team.split(','):
            team = [t for t in all_teams if int(t.id) == int(team)]

            if not team:
                print(
                    "Error: could not find team %s in org %s" %
                    (args.team, args.org))
                exit(1)

            users.update({m.login: m.name for m in team[0].get_members()})
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

    try:
        exclude_users = environ['PR_EXCLUDE_USERS'].split(',')
        for user in exclude_users:
            users.pop(user)
    except KeyError:
        pass

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

    if args.after or args.before:
        created = "%s..%s" % (
            args.after if args.after else '*',
            args.before if args.before else '*')
        params.update({'created': created})

    get_prs(github, params, get_owners=args.codeowners)


if __name__ == '__main__':
    main()
