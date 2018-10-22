#!/usr/bin/env python

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from datetime import date
from dateutil.relativedelta import relativedelta

# TODO: Add paginatioon for when the number of results goes over 10000 limit

class AnalyticsApi:
  
  
  SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
  
  def __init__(self, key_file, account, property, profile):
    self.key_file = key_file
    self.account = account
    self.property = property
    self.profile = profile
    self.create_service()
  

  def create_service(self):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(self.key_file, self.SCOPES)
    self.service = build("analytics", "v3", credentials=credentials)

  def get_profile_id(self):
    accounts = self.service.management().accounts().list().execute()

    account = [acc.get('id') for acc in accounts.get('items') if acc.get('name') == self.account][0]

    properties = self.service.management().webproperties().list(accountId=account).execute()

    web_property = [prop.get('id') for prop in properties.get('items') if prop.get('name') == self.property][0]

    profiles = self.service.management().profiles().list(accountId=account, webPropertyId=web_property).execute()
          
    return [prof.get('id') for prof in profiles.get('items') if prof.get('name') == self.profile][0]



  def get_results(self):
    id = self.get_profile_id()
    start_date = date(2017, 10, 1)

    results = list()
    while start_date < date.today():
        end_date = start_date + relativedelta(months=1)

        results.append(self.service.data().ga().get(
                        ids='ga:' + id,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat(),
                        metrics='ga:totalEvents',
                        max_results=10000,
                        dimensions='ga:eventCategory,ga:eventAction,ga:eventLabel').execute())
        start_date = end_date + relativedelta(days = 1)
    rows = [row for result in results for row in result["rows"]]
    headers = [r.get('name') for r in results[0].get('columnHeaders')]
    return rows, headers