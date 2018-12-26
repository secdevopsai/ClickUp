import requests
from collections import defaultdict
import datetime

class Client:
    def __init__(self, email, password, api):
        self.server = "https://api.clickup.com/"
        self.email = email
        self.password = password
        self.api = api
        self.bearer = self.login(email, password)

        user_response = self.get_user()
        self.username = user_response['user']['username']
        self.user_id = user_response['user']['id']

        team_response = self.get_teams()
        self.teams = {}
        self.subcategories = {}
        for team in team_response['teams']:
            self.teams[team['id']] = team['name']

        self.spaces = {}
        for team in self.teams:
            spaces_response = self.get_team_spaces(team)
            for space in spaces_response['spaces']:
                self.spaces[space['id']] = {
                    "name": space["name"], "team": team}

    def login(self, email, password):
        """Login to clickup and retrieve bearer token

        Arguments:
            email {str} 
            password {str}

        Returns:
            token -- Bearer Token
        """

        uri = "v1/login?include_teams=true"
        data = {"email": email, "password": password}
        response = requests.request(
            method="GET", url=self.server + uri, data=data).json()
        return response["token"]

    def send_request(self, method="GET", uri=None, version="v1", **kwargs):
        """Send HTTP Request to ClickUP API

        Keyword Arguments:
            method {str} -- HTTP Request Method (default: {"GET"})
            uri {str} -- URI
            version {str} -- API Endpoint version (default: {"v1"})

        Returns:
            response -- JSON object from ClickUP HTTP Response
        """

        if version == "v1":
            headers = {"Authorization": self.api}
        else:
            headers = {"Authorization": "Bearer {}".format(self.bearer)}
        response = requests.request(
            method=method, url=self.server + uri, headers=headers, **kwargs).json()
        return response

    def get_user(self):
        """Retrieve user information 

        Returns:
            dict -- JSON Object of user information
        """

        uri = "api/v1/user"
        response = self.send_request("GET", uri=uri)
        return response

    def get_teams(self):
        """Retrieve teams

        Returns:
            response -- JSON Object of team information
        """

        uri = "api/v1/team"
        response = self.send_request("GET", uri=uri)
        return response

    def get_team_spaces(self, team_id):
        """Retrieve Team Spaces

        Arguments:
            team_id

        Returns:
            response -- JSON Object of team spaces
        """

        uri = "api/v1/team/{}/space".format(team_id)
        response = self.send_request("GET", uri=uri)
        return response

    def get_tasks_by_team(self, team_id, space_id=None, include_closed="true", version='v1'):
        """Get tasks associated with team id

        Arguments:
            team_id {str}

        Keyword Arguments:
            space_id {str} -- Space ID (default: {None})
            include_closed {str} -- Include closed tasks (default: {"true"})
            version {str} -- API Version (default: {'v1'})

        Returns:
            response -- JSON Object of team spaces
        """

        if version == 'v1':
            uri = "api/{}/team/{}/task?include_closed={}".format(
                version, team_id, include_closed)
            if space_id:
                uri += "&space_ids%5B%5D={}".format(space_id)
            response = self.send_request("GET", uri=uri)
            return response

    def enrich_task_ids(self, team_id, space_id, task_ids):
        """Retrieve more detailed task information
        
        Arguments:
            team_id {str} -- Team ID
            space_id {str} -- Space ID
            task_ids {list} -- Collection of task ids
        
        Returns:
            response -- JSON Object of enriched tasks
        """

        uri = "v2/task?team_id={}&project_ids%5B%5D={}?fields%5B%5D=assignees&fields%5B%5D=assigned_comments_count&fields%5B%5D=assigned_checklist_items&fields%5B%5D=attachments_thumbnail_count&fields%5B%5D=dependency_state&fields%5B%5D=parent_task&fields%5B%5D=attachments_count&fields%5B%5D=followers&fields%5B%5D=totalTimeSpent&fields%5B%5D=subtasks_count&fields%5B%5D=subtasks_by_status&fields%5B%5D=tags&fields%5B%5D=simple_statuses&fields%5B%5D=fallback_coverimage&fields%5B%5D=customFields".format(
            team_id, space_id)
        uri_args = "&task_ids[]=".join([task_id for task_id in task_ids])
        response = self.send_request("GET", uri=uri + uri_args, version="v2")
        return response

    def enrich_task(self, task_id):
        """Retrieve basic task information (not including time estimates)
        
        Arguments:
            task_id {str} -- Task ID
        
        Returns:
            response -- JSON Object of task details
        """

        uri = "v1/task/{}".format(task_id)
        response = self.send_request("GET", uri=uri, version="v2")
        return response

    def get_task_ids(self, team_id, project_id, category_id, show_all=False):
        """[summary]
        
        Arguments:
            team_id {str} -- Team ID
            project_id {[type]} -- Project ID
            category_id {[type]} -- Category ID
        
        Keyword Arguments:
            show_all {bool} -- Show all tasks - including open (default: {False})
        
        Returns:
            response -- JSON Object of task ids
        """

        uri = "v2/taskId?team_id={}&project_ids%5B%5D={}&category_ids%5B%5D={}".format(
            team_id, project_id, category_id)
        if not show_all:
            uri += "&statuses%5B%5D=Open"
        response = self.send_request("GET", uri=uri, version="v2")
        return response

    def get_categories(self, space_id):
        """Retrieve Categories

        Arguments:
            space_id {str} - Space ID

        Returns:
            response -- JSON Object and appends subcategories to object instance
        """

        uri = "v1/project/{}/category".format(space_id)
        response = self.send_request("GET", uri=uri, version="v2")
        self.get_subcategories(response, space_id)
        return response

    def get_subcategories(self, categories, space_id):
        """Retrieve Subcategories from get_categories() response

        Arguments:
            categories {dict}
            space_id -- Space ID
        """

        for category in categories["categories"]:
            for subcategory in category['subcategories']:
                name = subcategory['name']
                category_id = category['id']
                subcategory_id = subcategory['id']
                self.subcategories[subcategory_id] = {
                    "name": name,
                    "category_id": category_id,
                    "space_id": space_id
                }

    def create_task(self, subcategory, name, timestamp, estimate):
        """Create task in ClickUp subcategory

        Arguments:
            subcategory str -- Subcategory
            name str -- Task name
            timestamp int -- Due Date (unix timestamp)
            estimate int -- Minutes estimated to complete task

        Returns:
            response -- JSON Object of task creation
        """

        uri = "v1/subcategory/{}/task".format(
            subcategory)
        data = {
            "name": name, "assignees": [],
            "due_date": int(timestamp) * 1000,
            "start_date": None, "due_date_time": False, "status": "Open",
            "priority": "none", "position_wide": "subcategory",
            "position": 0
        }

        response = self.send_request("POST", uri=uri, version="v2", data=data)

        if estimate_time:
            task_id = response['id']
            estimate_time = {"time_estimate": 60000 * estimate,
                             "time_estimate_string": "{} minutes".format(estimate)}

            uri = "v1/task/{}".format(task_id)
            response = self.send_request(
                "PUT", uri=uri, version="v2", data=estimate_time)
        return response

    def get_tags(self, project_id):
        """Retrieve task tags from Project

        Arguments:
            project_id
        """

        uri = "v1/tag?project_id={}".format(project_id)
        response = self.send_request("GET", uri=uri, version="v2")
        return response
