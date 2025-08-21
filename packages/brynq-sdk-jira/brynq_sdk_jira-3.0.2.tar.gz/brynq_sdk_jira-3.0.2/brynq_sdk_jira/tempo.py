import json
import requests
from itertools import islice
from brynq_sdk_brynq import BrynQ
from typing import Union, List, Literal, Optional


class Tempo(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug=False):
        super().__init__()
        self.debug = debug
        credentials = self.interfaces.credentials.get(system="jira", system_type=system_type)
        credentials = credentials.get('data')
        self.headers = {
            "Authorization": f"Bearer {credentials['api_token']}",
            "Content-Type": "application/json"
        }
        if self.debug:
            print(self.headers)
        self.timeout = 3600

    def get_tempo_hours(self, from_date: str = None, to_date: str = None, updated_from: str = None) -> json:
        """
        This function gets hours from Tempo for the specified time period

        :param from_date: (Optional) string - retrieve results starting with this date
        :param to_date: (Optional) string - retrieve results up to and including this date
        :param updated_from: (Optional) string <yyyy-MM-dd['T'HH:mm:ss]['Z']> - retrieve results that have been updated from this date(e.g "2023-11-16") or date time (e.g "2023-11-06T16:48:59Z")
        :return: json response with results
        """
        total_response = []
        got_all_results = False
        no_of_loops = 0
        parameters = {}
        if from_date is not None:
            parameters.update({"from": from_date})
        if to_date is not None:
            parameters.update({"to": to_date})
        if updated_from is not None:
            parameters.update({"updatedFrom": updated_from})

        while not got_all_results:
            loop_parameters = parameters | {"limit": 1000, "offset": 1000 * no_of_loops}
            response = requests.get('https://api.tempo.io/4/worklogs', headers=self.headers, params=loop_parameters, timeout=self.timeout)
            if response.status_code == 200:
                response_json = response.json()
                no_of_loops += 1
                got_all_results = False if int(response_json['metadata']['count']) == 1000 else True
                total_response += response_json['results']
            else:
                raise ConnectionError(f"Error getting worklogs from Tempo: {response.status_code, response.text}")

        if self.debug:
            print(f"Received {len(total_response)} lines from Tempo")

        return total_response

    def get_tempo_teams(self, team_members: List[str] = None, name: str = None) -> json:
        """
        Fetches teams from the Tempo API in smaller batches to prevent long URLs if team_members is specified,
        otherwise, retrieves a list of all existing Teams.

        :param team_members: (Optional) List of Jira user account IDs to filter teams.
        :param name: (Optional) Name of the team to filter teams.
        :return: A json response containing team details.
        """
        total_response = []

        # Split team members into smaller chunks (avoid long URLs)
        team_member_chunks = self._chunk_list(team_members, 50) if team_members else [None]

        for team_chunk in team_member_chunks:
            parameters = {"limit": 1000, "offset": 0}
            if team_chunk:
                parameters["teamMembers"] = ",".join(team_chunk)  # Send fewer team members at a time
            if name:
                parameters["name"] = name
            got_all_results = False
            no_of_loops = 0

            while not got_all_results:
                parameters["offset"] = 1000 * no_of_loops
                response = requests.get('https://api.tempo.io/4/teams', headers=self.headers, params=parameters, timeout=self.timeout)
                if response.status_code == 200:
                    response_json = response.json()
                    total_response.extend(response_json["results"])
                    got_all_results = False if int(response_json['metadata']['count']) == 1000 else True
                    no_of_loops += 1
                else:
                    raise ConnectionError(f"Error getting teams from Tempo: {response.status_code}, {response.text}")

        if self.debug:
            print(f"Received {len(total_response)} teams from Tempo")
        return total_response

    def get_tempo_team_members(self, team_ids: List[int]) -> json:
        """
        Fetches members of multiple teams from the Tempo API iteratively.

        :param team_ids: List of Tempo team IDs to retrieve members from.
        :return: A json response containing team members' details.
        """
        total_response = []

        for team_id in team_ids:
            got_all_results = False
            no_of_loops = 0

            while not got_all_results:
                parameters = {"limit": 1000, "offset": 1000 * no_of_loops}
                response = requests.get(f'https://api.tempo.io/4/teams/{team_id}/members', headers=self.headers, params=parameters, timeout=self.timeout)
                if response.status_code == 200:
                    response_json = response.json()
                    total_response.extend(response_json["results"])
                    got_all_results = False if int(response_json.get('metadata', {}).get('count', 0)) == 1000 else True
                    no_of_loops += 1
                else:
                    raise ConnectionError(f"Error getting team members from Tempo: {response.status_code}, {response.text}")

        if self.debug:
            print(f"Received {len(total_response)} team members from Tempo")
        return total_response

    def get_accounts(self) -> json:
        """
        Fetches account details from the Tempo API in batches to handle large datasets.

        :return: A json object containing account details.
        """
        total_response = []
        got_all_results = False
        no_of_loops = 0
        parameters = {}

        while not got_all_results:
            loop_parameters = parameters | {"limit": 1000, "offset": 1000 * no_of_loops}
            response = requests.get('https://api.tempo.io/4/accounts', headers=self.headers, params=loop_parameters, timeout=self.timeout)
            if response.status_code == 200:
                response_json = response.json()
                no_of_loops += 1
                got_all_results = False if int(response_json['metadata']['count']) == 1000 else True
                total_response += response_json['results']
            else:
                raise ConnectionError(f"Error getting accounts from Tempo: {response.status_code}, {response.text}")

        if self.debug:
            print(f"Received {len(total_response)} accounts from Tempo")
        return total_response

    def get_worklog_accounts(self, account_key: str, from_date: str = None, to_date: str = None, updated_from: str = None) -> json:
        """
        Fetches worklog data for a given account key from the Tempo API.

        :param account_key: (Required) string - The account key for which worklog data is required.
        :param from_date: (Optional) string - retrieve results starting with this date
        :param to_date: (Optional) string - retrieve results up to and including this date
        :param updated_from: (Optional) string <yyyy-MM-dd['T'HH:mm:ss]['Z']> - retrieve results that have been updated from this date(e.g "2023-11-16") or date time (e.g "2023-11-06T16:48:59Z")
        :return: A json containing worklog details.
        """
        total_response = []
        got_all_results = False
        no_of_loops = 0
        parameters = {}
        if from_date is not None:
            parameters.update({"from": from_date})
        if to_date is not None:
            parameters.update({"to": to_date})
        if updated_from is not None:
            parameters.update({"updatedFrom": updated_from})

        while not got_all_results:
            loop_parameters = parameters | {"limit": 1000, "offset": 1000 * no_of_loops}
            response = requests.get(f"https://api.tempo.io/4/worklogs/account/{account_key}", headers=self.headers, params=loop_parameters, timeout=self.timeout)
            if response.status_code == 200:
                response_json = response.json()
                total_response.extend(response_json.get("results", []))
                got_all_results = False if int(response_json.get('metadata', {}).get('count', 0)) == 1000 else True
                no_of_loops += 1
            else:
                raise ConnectionError(f"Failed to fetch data for account key {account_key}: {response.status_code}, {response.text}")

        if self.debug:
            print(f"Received {len(total_response)} worklogs for account key {account_key}")

        return total_response

    def _chunk_list(self, data_list, chunk_size):
        """Splits a list into chunks of `chunk_size`."""
        it = iter(data_list)
        return iter(lambda: list(islice(it, chunk_size)), [])