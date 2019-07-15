# github-pr-report
Make a CSV of pull requests for a specific org/team/user

# Description
Make management happy with answers to questions like:
* How many PRs has Bob submitted in the past year?
* What are the oldest open PRs submitted by our team?

`get_prs.py` can geneate a CSV file with open or closed pull requests for a Github organiztion, team, or list of users.

The `upload.py` script can take the contents of the CSV and insert it into a Google Sheet.

# Setup

* Follow the GSheets [quickstart guide](https://developers.google.com/sheets/api/quickstart/python) for Python and save the `token.json` and `credentials.json` files for use with `upload.py`.
* Install [PyGithub](https://github.com/PyGithub/PyGithub) for Python 3
* Create a Github OAuth token for your organization and optionally save it at `~/.pr_token`.

# Usage
## get_prs.py
```
usage: get_prs.py [-h] [-u USER] [-o ORG] [-t TEAM] [-k TOKEN] [-s STATE]
                  [-b BEFORE] [-a AFTER]

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Comma separated string of users to query for
  -o ORG, --org ORG     Organization id. Required
  -t TEAM, --team TEAM  Numeric identifier of the team to query for
  -k TOKEN, --token TOKEN
                        Token to use in api calls. Can be saved in ~/.pr_token
  -s STATE, --state STATE
                        State of PRs. One of 'open' or 'closed'. Defaults to
                        'open'
  -b BEFORE, --before BEFORE
                        Get PRs created before DATE. Must by YYYY-MM-DD
  -a AFTER, --after AFTER
                        Get PRs created after DATE. Must by YYYY-MM-DD
```

## upload.py
```
usage: upload.py [-h] [-f FILE] [-s SPREADSHEET] [-t TOKEN] [-c CREDENTIALS]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Absolute path to file to read
  -s SPREADSHEET, --spreadsheet SPREADSHEET
                        ID of the Google Sheet to upload to
  -t TOKEN, --token TOKEN
                        Absolute path to token file
  -c CREDENTIALS, --credentials CREDENTIALS
                        Absolute path to credentials file
```
