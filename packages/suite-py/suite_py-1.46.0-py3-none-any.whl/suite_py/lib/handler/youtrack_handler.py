# -*- encoding: utf-8 -*-
import logging
import re
import time
from urllib.parse import urljoin

from suite_py.lib import logger
from suite_py.lib.requests.auth import BearerAuth
from suite_py.lib.requests.session import Session

REGEX = r"([A-Za-z]+-[0-9]+)"
# PRs should only be linked to level 3 and 4 type youtrack issues
# see https://www.notion.so/helloprima/YouTrack-Current-Setup-Review-a3fadcf81323465d957801055d49d2f5?pvs=4#431a2ac606f848e7a80bf0628d30c1d0
WORKABLE_CARD_TYPES = [
    "Feature",
    "Bug",
    "Performance",
    "Refactor",
    "Rework",
    "Analysis",
    "Sec Issue",
    "UXUI",
]


# pylint: disable=too-many-public-methods
class YoutrackHandler:
    def __init__(self, config, tokens):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        self._base_url = config.youtrack["url"] + "/"
        self._default_issue_type = config.youtrack["default_issue_type"]
        self._issue_url = urljoin(self._base_url, "issue/")
        self._client = Session(base_url=urljoin(self._base_url, "api/"))
        self._client.headers = headers
        self._client.auth = BearerAuth(tokens.youtrack)

    def get_projects(self):
        params = {"fields": "id,name,shortName"}
        return self._client.get("admin/projects", params=params).json()

    def get_current_user(self):
        params = {"fields": "login"}
        return self._client.get("users/me", params=params).json()

    def get_issue(self, issue_id):
        logger.debug(f"YouTrack issue_id: {issue_id}")
        _fields = [
            "$type",
            "id",
            "idReadable",
            "summary",
            "parent(issues(id))",
            "customFields(name,value(name))",
        ]
        params = {"fields": ",".join(_fields)}
        issue = self._client.get(f"issues/{issue_id}", params=params).json()
        issue["Type"] = self._get_issue_type_name(issue)
        logger.debug(f"YouTrack Issue json {issue}")

        return issue

    def search_issues(self, search, amount=5):
        return self._client.get(
            "issues",
            params={"fields": "idReadable,summary", "$top": amount, "query": search},
        ).json()

    def list_issues(self, amount=5):
        return self._client.get(
            "issues", params={"fields": "idReadable,summary", "$top": amount}
        ).json()

    def get_comments(self, issue_id):
        params = {"fields": "$type,id,text"}
        return self._client.get(f"issues/{issue_id}/comments", params=params).json()

    def update_deployed_field(self, issue_id):
        payload = {
            "customFields": [
                {
                    "name": "Deployed",
                    "$type": "SimpleIssueCustomField",
                    "value": time.time() * 1000,
                }
            ]
        }
        self._client.post(f"issues/{issue_id}", json=payload)

    def validate_issue(self, issue_id):
        try:
            if self.get_issue(issue_id):
                return True
        except Exception:
            pass
        return False

    def comment(self, issue_id, comment):
        payload = {"text": comment}
        self._client.post(f"issues/{issue_id}/comments", json=payload)

    def update_state(self, issue_id, status):
        payload = {
            "customFields": [
                {
                    "name": "State",
                    "$type": "StateIssueCustomField",
                    "value": {"name": status},
                }
            ]
        }
        self._client.post(f"issues/{issue_id}", json=payload)

    def add_tag(self, issue_id, label):
        params = {"fields": "id,name", "query": label}
        tag = self._client.get("issueTags", params=params).json()

        params = {"fields": "$type,id,tags($type,id,name)"}
        issue = self._client.get(f"issues/{issue_id}", params=params).json()

        issue["tags"].append(tag[0])

        payload = {"tags": issue["tags"]}
        self._client.post(f"issues/{issue_id}", json=payload)

    def assign_to(self, issue_id, user):
        payload = {
            "customFields": [
                {
                    "name": "Assignee",
                    "$type": "SingleUserIssueCustomField",
                    "value": {"login": user},
                }
            ]
        }

        try:
            # NOTE: This is not atomic. The OpenAPI specification provides no way of
            #       pushing to an array in a single request :(
            issue = self._client.get(
                f"issues/{issue_id}?fields=customFields(id,name,value(login))"
            ).json()

            assigned = next(
                (
                    field
                    for field in issue["customFields"]
                    if field["name"] == "Assignee"
                ),
                None,
            )
            if assigned is None:
                # Assignee field is not present... try setting it anyway
                pass
            elif assigned["$type"] == "SingleUserIssueCustomField":
                # Legacy assignee field, our payload is already setup for this
                if assigned["value"] is not None and assigned["value"]["login"] == user:
                    # We're already assigned, nothing to do
                    return
            elif assigned["$type"] == "MultiUserIssueCustomField":
                # New assignee field (accepts multiple users)
                assigned = assigned["value"]

                # Add ourselves if we're not in there already
                if [a for a in assigned if a["login"] == user]:
                    return

                assigned.append({"login": user})

                # Update the payload
                payload["customFields"] = [
                    {
                        "name": "Assignee",
                        "$type": "MultiUserIssueCustomField",
                        "value": assigned,
                    }
                ]
            else:
                raise ValueError(f"Unknown issue Assignee type {assigned['$type']}")
        except Exception as error:
            logging.warning(
                "Error getting current status of issue: %s\nYou may need to manually assign the issue to %s yourself, trying anyway...",
                error,
                user,
            )

        self._client.post(f"issues/{issue_id}", json=payload)

    def get_link(self, issue_id):
        return f"{self._issue_url}{issue_id}"

    def get_issue_ids(self, commits):
        issue_ids = []
        for c in commits:
            issue_id = self.get_card_from_name(c.commit.message)
            if issue_id:
                issue_ids.append(issue_id)
        return issue_ids

    def get_card_from_name(self, name):
        if re.search(REGEX, name):
            id_card = re.findall(REGEX, name)[0]
            if self.validate_issue(id_card):
                return id_card
        return None

    def get_ids_from_release_body(self, body):
        return list(set(re.findall(REGEX, body)))

    def replace_card_names_with_md_links(self, text):
        return re.sub(REGEX, f"[\\1]({self._issue_url}\\1)", text)

    def _get_issue_type_name(self, issue):
        type_field = [x for x in issue["customFields"] if x["name"] == "Type"][0]

        if type_field["value"]["name"] in WORKABLE_CARD_TYPES:
            return type_field["value"]["name"]

        if len(issue["parent"]["issues"]) == 0:
            return self._default_issue_type

        parent = issue["parent"]["issues"][0]
        # recursively get parent issue's type
        return self.get_issue(parent["id"])["Type"]

    def get_issue_descendants(self, issue_id):
        _fields = [
            "resolved",
            "subtasks(issues(id,idReadable,resolved,summary,customFields(name,value),subtasks(issues(id))))",
        ]
        params = {"fields": ",".join(_fields)}
        issue = self._client.get(f"issues/{issue_id}", params=params).json()

        descendants = []
        for child in issue.get("subtasks", {}).get("issues", []):
            descendants.append(child)
            if child.get("subtasks", {}).get("issues"):
                descendants.extend(self.get_issue_descendants(child["id"]))
        return descendants

    def get_current_sprint(self, agile_board_id):
        params = {
            "fields": "id",
        }
        return self._client.get(
            f"agiles/{agile_board_id}/sprints/current", params=params
        ).json()

    def get_sprints(self, agile_board_id):
        params = {
            "fields": "id",
        }
        return self._client.get(
            f"agiles/{agile_board_id}/sprints", params=params
        ).json()

    def get_sprint_resolved_story_points(self, agile_board_id, sprint_id):
        """Get the sum of the story point estimates of all resolved issues of a sprint."""
        params = {
            "fields": "id,name,goal,issues(id,idReadable,summary,resolved,customFields(name,value))",
        }
        sprint = self._client.get(
            f"agiles/{agile_board_id}/sprints/{sprint_id}", params=params
        ).json()

        resolved_issues = [issue for issue in sprint["issues"] if issue["resolved"]]

        total_story_points = 0
        for issue in resolved_issues:
            # Find the Story Points custom field
            story_points_field = next(
                (
                    field
                    for field in issue.get("customFields", [])
                    if field["name"] == "Story Points"
                ),
                None,
            )
            if story_points_field and story_points_field.get("value"):
                try:
                    story_points = int(story_points_field["value"])
                    total_story_points += story_points
                except (ValueError, TypeError):
                    # Skip issues with invalid story points values
                    logger.debug(
                        f"Invalid story points value for issue {issue.get('idReadable', 'unknown')}: {story_points_field.get('value')}"
                    )
                    continue

        return total_story_points
