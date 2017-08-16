#!/usr/bin/env python

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

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
    # Use the Analytics Service Object to query the Core Reporting API
    # for the number of sessions within the past seven days.
    return self.service.data().ga().get(
      ids='ga:' + id,
      start_date='2016-10-01',
      end_date='today',
      metrics='ga:totalEvents',
      max_results=10000,
      dimensions='ga:eventCategory,ga:eventAction,ga:eventLabel').execute()