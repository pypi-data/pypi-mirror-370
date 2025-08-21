import json
from typing import Union, List, Literal, Optional
import pandas as pd
import requests
from brynq_sdk_brynq import BrynQ

class Jira(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug=False):
        super().__init__()
        credentials = self.interfaces.credentials.get(system="jira", system_type=system_type)
        credentials = credentials.get('data')
        self.base_url = credentials['base_url']
        self.headers = {
            "Authorization": f"Basic {credentials['access_token']}",
            "Content-Type": "application/json"
        }
        self.debug = debug
        self.timeout = 3600

    def get_issues(self, jql_filter: str = None, jira_filter_id: int = None, get_extra_fields: list = None, expand_fields: list = None) -> pd.DataFrame:
        """
        This method retrieves issues from Jira.
        :param jql_filter: optional filter in jql format
        :param jira_filter_id: optional filter id of predefined filter in jira
        :param get_extra_fields: an optional list of extra fields to retrieve
        :param expand_fields: an optional list of fields to expand
        :return: dataframe with issues
        """
        if jira_filter_id is not None:
            raise ValueError("Jira filter id is no longer supported, use jql_filter instead")

        # Use new JQL search endpoint
        url = f"{self.base_url}rest/api/3/search/jql"

        all_issues = []
        next_page_token = None

        while True:
            payload = {
                "maxResults": 100,
                "fields": ["summary", "issuetype", "timetracking", "timespent", "description", "assignee", "project"]
            }

            if jql_filter:
                payload["jql"] = jql_filter

            if get_extra_fields:
                payload["fields"].extend(get_extra_fields)

            if expand_fields:
                # Convert list to comma-delimited string
                payload["expand"] = ",".join(expand_fields)

            if next_page_token:
                payload["nextPageToken"] = next_page_token

            if self.debug:
                print(f"Payload: {payload}")

            response = requests.post(
                url=url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=self.timeout
            )

            if response.status_code == 200:
                response_json = response.json()
                all_issues.extend(response_json.get("issues", []))

                # Check for next page
                if "nextPageToken" in response_json:
                    next_page_token = response_json["nextPageToken"]
                else:
                    break
            else:
                raise ConnectionError(f"Error getting issues from Jira with message: {response.status_code, response.text}")

        if self.debug:
            print(f"Received {len(all_issues)} issues from Jira")

        df = pd.json_normalize(all_issues)
        return df

    def get_projects(self) -> pd.DataFrame:
        """
        This method retrieves projects from Jira.
        :return: a dataframe with projects
        """
        total_response = []
        got_all_results = False
        no_of_loops = 0

        while not got_all_results:
            query = {
                'startAt': f'{50 * no_of_loops}',
                'maxResults': '50',
                'expand': 'description'
            }
            if self.debug:
                print(query)
            response = requests.get(f"{self.base_url}rest/api/3/project/search", headers=self.headers, params=query, timeout=self.timeout)
            if response.status_code == 200:
                response_json = response.json()
                response.raise_for_status()
                no_of_loops += 1
                got_all_results = False if len(response_json['values']) == 50 else True
                total_response += response_json['values']
            else:
                raise ConnectionError(f"Error getting projects from Jira with message: {response.status_code, response.text}")

        if self.debug:
            print(f"Received {len(total_response)} projects from Jira")

        df = pd.json_normalize(total_response)

        return df

    def get_versions(self, project_key: str) -> pd.DataFrame:
        """
        This method retrieves versions for a given project from Jira.
        :param project_key: The key of the project for which versions are to be retrieved.
        :return: A dataframe with the versions.
        """
        url = f"{self.base_url}rest/api/latest/project/{project_key}/versions"
        response = requests.get(url=url, headers=self.headers, timeout=self.timeout)
        if response.status_code == 200:
            response_json = response.json()
            df = pd.json_normalize(response_json)
            if self.debug:
                print(f"Received {len(df)} versions for project {project_key}")
            return df
        else:
            raise ConnectionError(f"Error getting versions from Jira with message: {response.status_code, response.text}")

    def get_users(self) -> pd.DataFrame:
        """
        This method retrieves users from Jira.
        :return: a dataframe with users
        """
        start_at = 0
        max_results = 50
        all_users = []

        while True:
            response = requests.get(f"{self.base_url}rest/api/3/users/search?startAt={start_at}&maxResults={max_results}", headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            if response.status_code == 200:
                users = response.json()  # A list of user objects
                all_users.extend(users)  # Add users to the total list

                # Stop if no more users are returned
                if not users:
                    break

                # Increment startAt for the next page
                start_at += len(users)
            else:
                raise ConnectionError(f"Error getting users from Jira with message: {response.status_code, response.text}")
            if self.debug:
                print(f"Received {len(all_users)} jira users from Jira")

        df = pd.json_normalize(all_users)
        return df
