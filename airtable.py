import requests
import json
import os


class Airtable_Service():
    """airtable base call to get all data from airtable and update record by id"""

    def __init__(self,BASE_ID=None):
        # Airtable constructor
        self.AIRTABLE_HEADER = {
            "Authorization": f"Bearer {os.getenv('AIRTABLE_API_KEY')}",
            'Content-Type': 'application/json'
        }
        if BASE_ID == None:
            self.BASE_ID = os.getenv('BASE_ID')
        else:
            self.BASE_ID = BASE_ID
        self.url = 'https://api.airtable.com/v0/'

    def get_all_data(self, table_name: str, filterByFormula=None ) -> list:
        """get all data from airtable"""
        all_records = []

        # Parameters for pagination
        params = {
            'pageSize': 100  # Adjust the page size as needed
        }

        # Send a GET request to fetch data
        while True:
            if filterByFormula == None :
                response = requests.get(f"{self.url}{self.BASE_ID}/{table_name}", headers=self.AIRTABLE_HEADER,
                                    params=params)
            else:
                params['filterByFormula']=filterByFormula
                # print(params)
                response = requests.get(f"{self.url}{self.BASE_ID}/{table_name}", headers=self.AIRTABLE_HEADER,
                                    params=params)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                data = response.json()
                # Extract records from the response
                records = data.get('records', [])
                all_records.extend(records)
                # Check if there are more records to fetch
                if 'offset' in data:
                    params['offset'] = data['offset']
                else:
                    break  # No more records to fetch
            else:
                print(f"Error: {response.status_code} - {response.text}")
                break
        return all_records


    def add_record(self,table_name, data):
        data_at = {
            "records": [{"fields": data}],
        }

        create = requests.post(f"{self.url}{self.BASE_ID}/{table_name}",
                                json=data_at,
                                headers=self.AIRTABLE_HEADER
                                )
        return json.loads(create.text)
