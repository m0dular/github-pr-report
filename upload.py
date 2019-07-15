#!/usr/bin/env python3
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import csv
import argparse

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "-f", "--file", type=str,
        help="Absolute path to file to read")
    p.add_argument(
        "-s", "--spreadsheet", type=str,
        help="ID of the Google Sheet to upload to")
    p.add_argument(
        "-t", "--token", type=str,
        help="Absolute path to token file")
    p.add_argument(
        "-c", "--credentials", type=str,
        help="Absolute path to credentials file")
    args = p.parse_args()

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = args.spreadsheet

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage(args.token)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(args.credentials, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    with open(args.file, 'r') as f:
        r = csv.reader(f)
        data = []
        for line in r:
            data.append(line)

    # Call the Sheets API
    request_body = {'values': data}
    sheet = service.spreadsheets()
    sheet.values().clear(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range='Sheet1').execute()
    request = sheet.values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, body=request_body,
        range='Sheet1', valueInputOption='RAW')
    values = request.execute()

    if not values:
        print('No data found.')
    else:
        print(values)


if __name__ == '__main__':
    main()
